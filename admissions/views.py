from django.db import transaction
from django.utils import timezone
from rest_framework import generics, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from accounts import audit
from accounts.permissions import IsAdmin, IsApplicant

from .models import (
    AdmissionApplication,
    AdmissionDocument,
    ApplicationStatus,
    ParentRelationshipRequest,
    ParentRelationshipStatus,
)
from .permissions import IsApplicationOwner
from .serializers import (
    AdmissionApplicationAdminListSerializer,
    AdmissionApplicationDecisionSerializer,
    AdmissionApplicationDetailSerializer,
    AdmissionApplicationPublicStatusSerializer,
    AdmissionApplicationWriteSerializer,
    AdmissionDocumentSerializer,
    ParentRelationshipRequestAdminSerializer,
    ParentRelationshipRequestCreateSerializer,
    ParentRelationshipRequestDecisionSerializer,
)


class AdmissionApplicationViewSet(viewsets.ModelViewSet):
    """
    /api/admissions/applications/ -- an applicant's OWN admission
    applications. A single applicant account can have more than one (e.g.
    a parent applying for two children), each independently trackable.
    """

    permission_classes = [IsApplicant, IsApplicationOwner]
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        return AdmissionApplication.objects.filter(
            applicant=self.request.user
        ).prefetch_related("documents")

    def get_serializer_class(self):
        if self.action == "retrieve":
            return AdmissionApplicationDetailSerializer
        return AdmissionApplicationWriteSerializer

    def perform_create(self, serializer):
        serializer.save(applicant=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.status != ApplicationStatus.STARTED:
            raise PermissionDenied(
                "This application has already been submitted and can no longer be edited directly."
            )
        serializer.save()

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        """POST /api/admissions/applications/<id>/submit/ -- Section 19's
        review-and-submit step: locks the draft, generates the BFA-YYYY-NNNNNN
        reference number, and moves status to Submitted."""
        application = self.get_object()
        if application.status != ApplicationStatus.STARTED:
            return Response(
                {"detail": "This application has already been submitted."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        required_fields = [
            application.student_first_name,
            application.student_last_name,
            application.student_dob,
            application.class_applying_for,
            application.academic_session,
            application.guardian_full_name,
            application.guardian_phone,
            application.guardian_email,
        ]
        if not all(required_fields):
            return Response(
                {
                    "detail": "Complete the student and guardian sections before submitting."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        with transaction.atomic():
            application.reference = application.generate_reference()
            application.status = ApplicationStatus.SUBMITTED
            application.submitted_at = timezone.now()
            application.save(update_fields=["reference", "status", "submitted_at"])
        return Response(
            AdmissionApplicationDetailSerializer(application).data,
            status=status.HTTP_200_OK,
        )


class ApplicationDocumentListCreateView(generics.ListCreateAPIView):
    """/api/admissions/applications/<application_id>/documents/"""

    serializer_class = AdmissionDocumentSerializer
    permission_classes = [IsApplicant]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    pagination_class = None

    def _get_application(self):
        application = generics.get_object_or_404(
            AdmissionApplication.objects.all(), pk=self.kwargs["application_id"]
        )
        if application.applicant_id != self.request.user.id:
            raise PermissionDenied("This is not your application.")
        return application

    def get_queryset(self):
        return AdmissionDocument.objects.filter(application=self._get_application())

    def perform_create(self, serializer):
        serializer.save(application=self._get_application())


class AdmissionApplicationPublicStatusView(generics.RetrieveAPIView):
    """GET /api/admissions/status/<reference>/ -- public, unauthenticated
    reference lookup for the full application (Section 20), separate from
    public_site's AdmissionEnquiry status lookup."""

    queryset = AdmissionApplication.objects.all()
    serializer_class = AdmissionApplicationPublicStatusSerializer
    permission_classes = [AllowAny]
    lookup_field = "reference"
    lookup_url_kwarg = "reference"


class AdmissionApplicationAdminViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):

    @action(detail=True, methods=["post"])
    def provision(self, request, pk=None):
        from django.contrib.auth import get_user_model
        from django.conf import settings
        from accounts.models import Profile, RegistrationInvitation
        from students.models import Student

        application = self.get_object()
        if application.status != ApplicationStatus.APPROVED:
            return Response(
                {"detail": "Application must be APPROVED before provisioning."},
                status=400,
            )

        with transaction.atomic():
            student_email = (
                application.student_email
                or f"{application.reference.lower()}@student.local"
            )
            student_user, created = get_user_model().objects.get_or_create(
                username=student_email,
                defaults={
                    "email": student_email,
                    "first_name": application.student_first_name,
                    "last_name": application.student_last_name,
                    "is_active": False,
                },
            )

            if created:
                student_user.set_unusable_password()
                student_user.save()
                student_profile = student_user.profile
                student_profile.role = "student"
                student_profile.save(update_fields=["role"])
            else:
                student_profile = student_user.profile

            student, student_created = Student.objects.get_or_create(
                profile=student_profile,
                defaults={
                    "admission_number": application.reference,
                    "dob": application.student_dob,
                },
            )

            parent_email = application.guardian_email
            parent_user, p_created = get_user_model().objects.get_or_create(
                username=parent_email,
                defaults={
                    "email": parent_email,
                    "first_name": application.guardian_full_name.split()[0],
                    "last_name": (
                        " ".join(application.guardian_full_name.split()[1:])
                        if len(application.guardian_full_name.split()) > 1
                        else ""
                    ),
                    "is_active": False,
                },
            )

            if p_created:
                parent_user.set_unusable_password()
                parent_user.save()
                parent_profile = parent_user.profile
                parent_profile.role = "parent"
                parent_profile.save(update_fields=["role"])
            else:
                parent_profile = parent_user.profile

            student.parents.add(parent_profile)

            # Use existing or create new invitations
            student_inv = RegistrationInvitation.objects.filter(
                email=student_user.email
            ).first()
            if not student_inv:
                student_inv = RegistrationInvitation.objects.create(
                    email=student_user.email,
                    role="student",
                    token=RegistrationInvitation.generate_token(),
                    first_name=student_user.first_name,
                    last_name=student_user.last_name,
                    created_by=request.user,
                )

            parent_inv = RegistrationInvitation.objects.filter(
                email=parent_user.email
            ).first()
            if not parent_inv:
                parent_inv = RegistrationInvitation.objects.create(
                    email=parent_user.email,
                    role="parent",
                    token=RegistrationInvitation.generate_token(),
                    first_name=parent_user.first_name,
                    last_name=parent_user.last_name,
                    created_by=request.user,
                )

            frontend_url = getattr(settings, "FRONTEND_URL", "http://127.0.0.1:5173")
            try:
                from django.core.mail import send_mail

                send_mail(
                    "Activate your Schoolhub Parent Account",
                    f"An administrator has provisioned a parent account for you. Use this link to activate it and set your password: {frontend_url}/portal?activate_token={parent_inv.token}",
                    settings.DEFAULT_FROM_EMAIL,
                    [parent_inv.email],
                    fail_silently=True,
                )
            except Exception:
                pass

            audit.record(
                actor=request.user,
                action="admission_application.provisioned",
                instance=application,
                request=request,
            )

        return Response({"detail": "Student and Parent provisioned successfully."})

    permission_classes = [IsAdmin]
    queryset = AdmissionApplication.objects.exclude(
        status=ApplicationStatus.STARTED
    ).prefetch_related("documents")
    filterset_fields = ["status", "academic_session", "class_applying_for"]
    search_fields = [
        "reference",
        "student_first_name",
        "student_last_name",
        "guardian_email",
    ]

    def get_serializer_class(self):
        return (
            AdmissionApplicationDetailSerializer
            if self.action == "retrieve"
            else AdmissionApplicationAdminListSerializer
        )

    @action(detail=True, methods=["post"])
    def decide(self, request, pk=None):
        application = self.get_object()
        serializer = AdmissionApplicationDecisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        old_status = application.status
        application.status = serializer.validated_data["status"]
        application.decision_notes = serializer.validated_data.get(
            "decision_notes", application.decision_notes
        )
        application.reviewed_by = request.user
        application.save(
            update_fields=["status", "decision_notes", "reviewed_by", "updated_at"]
        )

        audit.record(
            actor=request.user,
            action="admission_application.status_change",
            instance=application,
            old_value={"status": old_status},
            new_value={"status": application.status},
            request=request,
        )
        return Response(AdmissionApplicationDetailSerializer(application).data)


class ParentRelationshipRequestViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    /api/admissions/parent-relationships/ -- Section 2.6 / 23: a parent
    registers publicly identifying the student they claim to be guardian
    of. This is create/list/retrieve only for the applicant -- no edit,
    since changing the claimed student after submission should go through
    a fresh request rather than mutating one an admin may already be
    reviewing.
    """

    permission_classes = [IsApplicant, IsApplicationOwner]
    serializer_class = ParentRelationshipRequestCreateSerializer

    def get_queryset(self):
        return ParentRelationshipRequest.objects.filter(applicant=self.request.user)

    def perform_create(self, serializer):
        serializer.save(applicant=self.request.user)


class ParentRelationshipRequestAdminViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """/api/admissions/admin/parent-relationships/ -- staff verification queue."""

    permission_classes = [IsAdmin]
    queryset = ParentRelationshipRequest.objects.all()
    serializer_class = ParentRelationshipRequestAdminSerializer
    filterset_fields = ["status"]
    search_fields = [
        "reference",
        "child_full_name",
        "student_admission_number",
        "email",
    ]

    @action(detail=True, methods=["post"])
    def decide(self, request, pk=None):
        """
        Marking a request VERIFIED here does NOT by itself provision a
        Parent account or link the student -- that's Stage 3's
        admin-provisioning step, which should treat a verified request as
        its input. Keeping verification and provisioning as two distinct,
        separately-audited actions means a verified relationship can be
        reviewed before an account is actually created.
        """
        relationship_request = self.get_object()
        serializer = ParentRelationshipRequestDecisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        old_status = relationship_request.status
        relationship_request.status = serializer.validated_data["status"]
        relationship_request.decision_notes = serializer.validated_data.get(
            "decision_notes", relationship_request.decision_notes
        )
        relationship_request.reviewed_by = request.user
        relationship_request.save(
            update_fields=["status", "decision_notes", "reviewed_by", "updated_at"]
        )

        audit.record(
            actor=request.user,
            action="parent_relationship_request.status_change",
            instance=relationship_request,
            old_value={"status": old_status},
            new_value={"status": relationship_request.status},
            request=request,
        )
        return Response(
            ParentRelationshipRequestAdminSerializer(relationship_request).data
        )
