from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(
    "monitoring-jobs", views.MonitoringJobViewSet, basename="monitoring-job"
)
router.register(
    "satellite-images", views.SatelliteImageViewSet, basename="satellite-image"
)

urlpatterns = router.urls
