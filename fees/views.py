from django.conf import settings
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from accounts.permissions import IsAdmin, IsAdminOrTeacher
from accounts import audit

from .models import Fee, Payment, FeeSchedule
from academics.models import Enrollment
from .serializers import FeeSerializer


class FeeViewSet(viewsets.ModelViewSet):
    queryset = Fee.objects.select_related("student__profile__user", "created_by").all()
    serializer_class = FeeSerializer
    filterset_fields = ["student", "status", "due_date"]
    search_fields = [
        "title",
        "student__profile__user__first_name",
        "student__profile__user__last_name",
    ]

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy"}:
            return [
                IsAdmin() if self.action != "partial_update" else IsAdminOrTeacher()
            ]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        profile = getattr(self.request.user, "profile", None)
        role = getattr(profile, "role", None)
        if profile and role == "parent":
            return queryset.filter(student__parents=profile)
        if profile and role == "student":
            return queryset.filter(student__profile=profile)
        if profile and role in ("admin", "teacher"):
            return queryset
        return queryset.none()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=["post"], permission_classes=[IsAdmin])
    def bulk_generate(self, request):
        schedule_id = request.data.get("schedule_id")
        class_id = request.data.get("class_id")

        if not schedule_id or not class_id:
            return Response(
                {"detail": "schedule_id and class_id are required."}, status=400
            )

        try:
            schedule = FeeSchedule.objects.get(id=schedule_id)
        except FeeSchedule.DoesNotExist:
            return Response({"detail": "FeeSchedule not found."}, status=404)

        enrollments = Enrollment.objects.filter(school_class_id=class_id)
        if not enrollments.exists():
            return Response(
                {"detail": "No enrollments found for this class."}, status=400
            )

        generated = 0
        for enrollment in enrollments:
            # Prevent duplicate fee for the same schedule and student
            fee, created = Fee.objects.get_or_create(
                student=enrollment.student,
                title=f"{schedule.title} ({schedule.academic_year})",
                defaults={
                    "amount": schedule.amount,
                    "due_date": schedule.due_date,
                    "created_by": request.user,
                },
            )
            if created:
                generated += 1

        return Response({"detail": f"Successfully generated {generated} invoices."})


class PaymentWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Verify webhook signature
        import hashlib, hmac, json

        webhook_secret = getattr(settings, "PAYMENT_WEBHOOK_SECRET", None)
        if webhook_secret:
            signature = request.headers.get("X-Webhook-Signature", "")
            payload = json.dumps(request.data, sort_keys=True).encode()
            expected = hmac.new(
                webhook_secret.encode(), payload, hashlib.sha256
            ).hexdigest()
            if not hmac.compare_digest(signature, expected):
                return Response(
                    {"detail": "Invalid webhook signature"},
                    status=status.HTTP_403_FORBIDDEN,
                )

        invoice_id = request.data.get("invoice_id")
        payment_status = request.data.get("status")
        transaction_ref = request.data.get("transaction_ref")

        if not invoice_id or not payment_status or not transaction_ref:
            return Response(
                {"detail": "Missing required fields"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if payment_status != "success":
            return Response(
                {"detail": "Only success status is supported for now"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            fee = Fee.objects.get(id=invoice_id)
        except Fee.DoesNotExist:
            return Response(
                {"detail": "Invoice not found"}, status=status.HTTP_404_NOT_FOUND
            )

        if fee.status == "paid":
            return Response(
                {"detail": "Invoice already paid"}, status=status.HTTP_400_BAD_REQUEST
            )

        if Payment.objects.filter(transaction_ref=transaction_ref).exists():
            return Response(
                {"detail": "Duplicate transaction reference"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payment = Payment.objects.create(
            fee=fee,
            amount=fee.amount,
            transaction_ref=transaction_ref,
            status=payment_status,
        )

        fee.status = "paid"
        fee.paid_at = timezone.now()
        fee.save(update_fields=["status", "paid_at"])

        audit.record(
            actor=None,
            action="fee.payment_received",
            instance=fee,
            new_value={"transaction_ref": transaction_ref, "amount": str(fee.amount)},
            request=request,
        )

        return Response({"detail": "Payment processed successfully"})
