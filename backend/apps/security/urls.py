from django.urls import path

from .views import (
    RotationRunDetailAPIView,
    RotationRunListAPIView,
    RotationTriggerAPIView,
)


urlpatterns = [
    path("rotate/trigger/", RotationTriggerAPIView.as_view(), name="rotation-trigger"),
    path("runs/", RotationRunListAPIView.as_view(), name="rotation-run-list"),
    path("runs/<uuid:run_id>/", RotationRunDetailAPIView.as_view(), name="rotation-run-detail"),
]
