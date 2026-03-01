from rest_framework.routers import DefaultRouter
from .views import HostViewSet, IDCViewSet, CityViewSet

router = DefaultRouter()
router.register(r'hosts', HostViewSet, basename='host')
router.register(r'idcs', IDCViewSet, basename='idc')
router.register(r'cities', CityViewSet, basename='city')

urlpatterns = router.urls