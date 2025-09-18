from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("aois", views.AoiViewSet, basename="aoi")
router.register(
    "encroachments", views.EncroachmentDetectionViewSet, basename="encroachment"
)

urlpatterns = router.urls
