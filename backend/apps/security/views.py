from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import RotationRun
from .tasks import rotate_passwords_batch
from .serializers import RotationRunSerializer
from rest_framework.generics import GenericAPIView


class RotationTriggerAPIView(APIView):
    """人工触发一次批量密码轮换。"""

    def post(self, request):
        result = rotate_passwords_batch.delay()
        return Response(
            {
                "task_id": result.id,
                "queued": True,
            },
            status=status.HTTP_202_ACCEPTED,
        )


class RotationRunListAPIView(GenericAPIView):
    """查看密码轮换批次列表（使用全局分页）。"""

    queryset = RotationRun.objects.all()
    serializer_class = RotationRunSerializer

    def get(self, request):
        qs = self.get_queryset()
        page = self.paginate_queryset(qs)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class RotationRunDetailAPIView(APIView):
    """查看单次密码轮换批次详情。"""

    def get(self, request, run_id):
        run = get_object_or_404(RotationRun, pk=run_id)
        return Response(
            {
                "id": str(run.id),
                "scheduled_for": run.scheduled_for,
                "started_at": run.started_at,
                "finished_at": run.finished_at,
                "total_hosts": run.total_hosts,
                "success_count": run.success_count,
                "fail_count": run.fail_count,
                "status": run.status,
                "message": run.message,
                "created_at": run.created_at,
                "updated_at": run.updated_at,
            },
            status=status.HTTP_200_OK,
        )
