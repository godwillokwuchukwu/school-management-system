import re

file_path = r"c:\Users\Godwill\Downloads\school-management-system-stage2-riverside\school-management-system\fees\views.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(
    "from rest_framework import viewsets",
    "from rest_framework import viewsets, status\nfrom rest_framework.views import APIView\nfrom rest_framework.response import Response",
)
content = content.replace(
    "from rest_framework.permissions import IsAuthenticated",
    "from rest_framework.permissions import IsAuthenticated, AllowAny",
)
content = content.replace("from .models import Fee", "from .models import Fee, Payment")
if "from accounts import audit" not in content:
    content = content.replace(
        "from accounts.permissions import IsAdmin, IsAdminOrTeacher",
        "from accounts.permissions import IsAdmin, IsAdminOrTeacher\nfrom accounts import audit",
    )
if "from django.utils import timezone" not in content:
    content = "from django.utils import timezone\n" + content

webhook_view = """
class PaymentWebhookView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        invoice_id = request.data.get("invoice_id")
        payment_status = request.data.get("status")
        transaction_ref = request.data.get("transaction_ref")
        
        if not invoice_id or not payment_status or not transaction_ref:
            return Response({"detail": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)
            
        if payment_status != "success":
            return Response({"detail": "Only success status is supported for now"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            fee = Fee.objects.get(id=invoice_id)
        except Fee.DoesNotExist:
            return Response({"detail": "Invoice not found"}, status=status.HTTP_404_NOT_FOUND)
            
        if fee.status == "paid":
            return Response({"detail": "Invoice already paid"}, status=status.HTTP_400_BAD_REQUEST)
            
        if Payment.objects.filter(transaction_ref=transaction_ref).exists():
            return Response({"detail": "Duplicate transaction reference"}, status=status.HTTP_400_BAD_REQUEST)
            
        payment = Payment.objects.create(
            fee=fee,
            amount=fee.amount,
            transaction_ref=transaction_ref,
            status=payment_status
        )
        
        fee.status = "paid"
        fee.paid_at = timezone.now()
        fee.save(update_fields=["status", "paid_at"])
        
        audit.record(
            actor=None,
            action="fee.payment_received",
            instance=fee,
            new_value={"transaction_ref": transaction_ref, "amount": str(fee.amount)},
            request=request
        )
        
        return Response({"detail": "Payment processed successfully"})
"""

if "class PaymentWebhookView" not in content:
    content += webhook_view

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
