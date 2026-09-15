from rest_framework.routers import DefaultRouter

from .views import (
    ClassViewSet,
    EnrollmentViewSet,
    GradeViewSet,
    SubjectViewSet,
    ClassScheduleViewSet,
)

router = DefaultRouter()
router.register("subjects", SubjectViewSet, basename="subject")
router.register("classes", ClassViewSet, basename="class")
router.register("enrollments", EnrollmentViewSet, basename="enrollment")
router.register("grades", GradeViewSet, basename="grade")
router.register("schedules", ClassScheduleViewSet, basename="class-schedule")

urlpatterns = router.urls
