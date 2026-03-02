

from rest_framework import serializers

from .models import RotationRun


class RotationRunSerializer(serializers.ModelSerializer):
    """密码轮换批次序列化器。"""

    class Meta:
        model = RotationRun
        fields = (
            "id",
            "scheduled_for",
            "started_at",
            "finished_at",
            "total_hosts",
            "success_count",
            "fail_count",
            "status",
            "message",
            "created_at",
            "updated_at",
        )