from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'cart', views.CartViewSet, basename='cart')
router.register(r'orders', views.OrderViewSet, basename='order')

urlpatterns = router.urls