import sys
import subprocess
from datetime import timedelta

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from ..cmdb.models import Host



def _ping_ipv4(ip: str, timeout_seconds: int = 1) -> bool:
    """
    对指定 IPv4 进行一次 ping 探测。
    """
    ip = (ip or "").strip()
    if not ip:
        return False

    platform = sys.platform

    try:
        if platform.startswith("win"):
            cmd = ["ping", "-n", "1", "-w", str(timeout_seconds * 1000), ip]
        elif platform == "darwin":
            cmd = ["ping", "-c", "1", "-W", str(timeout_seconds * 1000), ip]
        else:
            cmd = ["ping", "-c", "1", "-W", str(timeout_seconds), ip]

        r = subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        return r.returncode == 0
    except Exception:
        return False


class HostPingAPIView(APIView):
    """
    人工触发：探测某台主机是否 ping 可达。

    说明：
    - 同步执行 ping，设置 1s 超时。
    - 增加简单的冷却时间，避免同一主机被高频触发（默认 10 秒）。
    """

    COOLDOWN_SECONDS = 10
    TIMEOUT_SECONDS = 1

    def post(self, request, host_id: int):
        host = get_object_or_404(Host, pk=host_id)
        now = timezone.now()

        # 10 秒内重复请求直接返回上次结果（如没有上次结果则继续探测）
        if host.last_ping_at and (now - host.last_ping_at) < timedelta(seconds=self.COOLDOWN_SECONDS):
            return Response(
                {
                    "message": "ok",
                    "data": {
                        "host_id": host.id,
                        "ip": host.ip,
                        "reachable": host.last_ping_ok,
                        "checked_at": host.last_ping_at.strftime("%Y-%m-%d %H:%M:%S"),
                        "cached": True,
                    },
                },
                status=status.HTTP_200_OK,
            )

        reachable = _ping_ipv4(host.ip, timeout_seconds=self.TIMEOUT_SECONDS)
        host.last_ping_ok = reachable
        host.last_ping_at = now
        host.save(update_fields=["last_ping_ok", "last_ping_at", "updated_at"])

        return Response(
            {
                "message": "ok",
                "data": {
                    "host_id": host.id,
                    "ip": host.ip,
                    "reachable": reachable,
                    "checked_at": now.strftime("%Y-%m-%d %H:%M:%S"),
                    "cached": False,
                },
            },
            status=status.HTTP_200_OK,
        )
