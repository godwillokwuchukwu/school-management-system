from rest_framework.routers import DefaultRouter

from django.urls import path

from .views import (
    AdmissionEnquiryCreateView,
    AdmissionEnquiryStatusView,
    ContactMessageCreateView,
    EventViewSet,
    FAQItemViewSet,
    JobApplicationCreateView,
    JobApplicationStatusView,
    JobPostingViewSet,
    NewsArticleViewSet,
    ProgramViewSet,
    SchoolProfileView,
    TestimonialViewSet,
)

router = DefaultRouter()
router.register("news", NewsArticleViewSet, basename="public-news")
router.register("events", EventViewSet, basename="public-event")
router.register("programs", ProgramViewSet, basename="public-program")
router.register("testimonials", TestimonialViewSet, basename="public-testimonial")
router.register("faqs", FAQItemViewSet, basename="public-faq")
router.register("careers/jobs", JobPostingViewSet, basename="public-job")

urlpatterns = [
    path("school/", SchoolProfileView.as_view(), name="public-school"),
    path("careers/apply/", JobApplicationCreateView.as_view(), name="public-job-apply"),
    path(
        "careers/applications/<str:reference>/",
        JobApplicationStatusView.as_view(),
        name="public-job-application-status",
    ),
    path(
        "admissions/enquiries/",
        AdmissionEnquiryCreateView.as_view(),
        name="public-admission-enquiry",
    ),
    path(
        "admissions/enquiries/<str:reference>/",
        AdmissionEnquiryStatusView.as_view(),
        name="public-admission-status",
    ),
    path("contact/", ContactMessageCreateView.as_view(), name="public-contact"),
] + router.urls
