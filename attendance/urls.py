from rest_framework.routers import DefaultRouter

from .views import AttendanceRecordViewSet

router = DefaultRouter()
router.register("records", AttendanceRecordViewSet, basename="attendance-record")

urlpatterns = router.urls
