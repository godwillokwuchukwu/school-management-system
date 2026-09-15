from django.utils import timezone
from rest_framework import generics, mixins, status, viewsets
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from .models import (
    AdmissionEnquiry,
    Event,
    FAQItem,
    JobApplication,
    JobPosting,
    NewsArticle,
    Program,
    SchoolProfile,
    Testimonial,
)
from .serializers import (
    AdmissionEnquiryCreateSerializer,
    AdmissionEnquiryStatusSerializer,
    ContactMessageCreateSerializer,
    EventSerializer,
    FAQItemSerializer,
    JobApplicationCreateSerializer,
    JobApplicationStatusSerializer,
    JobPostingSerializer,
    NewsArticleDetailSerializer,
    NewsArticleListSerializer,
    ProgramSerializer,
    SchoolProfileSerializer,
    TestimonialSerializer,
)


class SchoolProfileView(APIView):
    """GET /api/public/school/ -- homepage/about content (Sections 11-12)."""

    permission_classes = [AllowAny]

    def get(self, request):
        return Response(SchoolProfileSerializer(SchoolProfile.load()).data)


class PublicReadOnlyMixin:
    permission_classes = [AllowAny]
    lookup_field = "slug"


class NewsArticleViewSet(PublicReadOnlyMixin, viewsets.ReadOnlyModelViewSet):
    queryset = NewsArticle.objects.filter(is_published=True)
    filterset_fields = ["category", "is_featured"]
    search_fields = ["title", "excerpt", "body"]

    def get_serializer_class(self):
        return (
            NewsArticleDetailSerializer
            if self.action == "retrieve"
            else NewsArticleListSerializer
        )


class EventViewSet(PublicReadOnlyMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Event.objects.filter(is_published=True)
    serializer_class = EventSerializer
    filterset_fields = ["category"]
    search_fields = ["title", "description", "location"]

    def get_queryset(self):
        qs = super().get_queryset()
        when = self.request.query_params.get("when")
        now = timezone.now()
        if when == "upcoming":
            return qs.filter(starts_at__gte=now)
        if when == "past":
            return qs.filter(starts_at__lt=now)
        return qs


class ProgramViewSet(PublicReadOnlyMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Program.objects.filter(is_published=True)
    serializer_class = ProgramSerializer
    filterset_fields = ["category"]


class TestimonialViewSet(
    PublicReadOnlyMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    queryset = Testimonial.objects.filter(is_published=True)
    serializer_class = TestimonialSerializer
    pagination_class = None


class FAQItemViewSet(
    PublicReadOnlyMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    queryset = FAQItem.objects.filter(is_published=True)
    serializer_class = FAQItemSerializer
    filterset_fields = ["category"]
    pagination_class = None


class JobPostingViewSet(PublicReadOnlyMixin, viewsets.ReadOnlyModelViewSet):
    queryset = JobPosting.objects.filter(is_active=True)
    serializer_class = JobPostingSerializer
    filterset_fields = ["department", "employment_type"]
    search_fields = ["title", "department"]


class PublicWriteThrottle(ScopedRateThrottle):
    scope = "public_write"


class JobApplicationCreateView(generics.CreateAPIView):
    """POST /api/public/careers/apply/ -- Section 16 employment application.

    Lead-capture only for now; see JobApplication's model docstring and
    GAP_ANALYSIS_AND_ROADMAP.md item #4 for the full recruitment pipeline
    this will be superseded by.
    """

    queryset = JobPosting.objects.none()
    serializer_class = JobApplicationCreateSerializer
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    throttle_classes = [PublicWriteThrottle]
    throttle_scope = "public_write"

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        application = serializer.save()
        return Response(
            {"reference": application.reference, "message": "Application received."},
            status=status.HTTP_201_CREATED,
        )


class AdmissionEnquiryCreateView(generics.CreateAPIView):
    """POST /api/public/admissions/enquiries/ -- preliminary interest form
    on the public /admissions page. See AdmissionEnquiry's model docstring
    -- this is a lead, not the full admission application from Section 19,
    which belongs to the dedicated `admissions` app (Stage 2 continued)."""

    serializer_class = AdmissionEnquiryCreateSerializer
    permission_classes = [AllowAny]
    throttle_classes = [PublicWriteThrottle]
    throttle_scope = "public_write"

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        enquiry = serializer.save()
        return Response(
            {
                "reference": enquiry.reference,
                "message": "Enquiry received. Use your reference to track status.",
            },
            status=status.HTTP_201_CREATED,
        )


class AdmissionEnquiryStatusView(generics.RetrieveAPIView):
    """GET /api/public/admissions/enquiries/<reference>/ -- Section 20 status tracking."""

    queryset = AdmissionEnquiry.objects.all()
    serializer_class = AdmissionEnquiryStatusSerializer
    permission_classes = [AllowAny]
    lookup_field = "reference"
    lookup_url_kwarg = "reference"


class ContactMessageCreateView(generics.CreateAPIView):

    serializer_class = ContactMessageCreateSerializer
    permission_classes = [AllowAny]
    throttle_classes = [PublicWriteThrottle]
    throttle_scope = "public_write"

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "Thanks for reaching out -- we'll be in touch shortly."},
            status=status.HTTP_201_CREATED,
        )


class JobApplicationStatusView(generics.RetrieveAPIView):
    """GET /api/public/careers/applications/<reference>/ -- Stage 2.5's
    'independent status tracking' for an employment application, separate
    from the admissions reference/status system."""

    queryset = JobApplication.objects.all()
    serializer_class = JobApplicationStatusSerializer
    permission_classes = [AllowAny]
    lookup_field = "reference"
    lookup_url_kwarg = "reference"
