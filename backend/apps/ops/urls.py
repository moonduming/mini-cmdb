from django.urls import path
from .views import HostPingAPIView


urlpatterns = [
    path(
        "hosts/<int:host_id>/ping/",
        HostPingAPIView.as_view(),
        name="host-ping",
    ),
]