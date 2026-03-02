from datetime import timedelta

from celery import shared_task
from django.apps import apps
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from .models import HostCredential, RotationRun
from .services.password_rotation import rotate_one_host_password


# pending 状态的超时窗口：超过该时间认为卡死，可允许重试
PENDING_STALE_MINUTES = 10


@shared_task(bind=True)
def rotate_passwords_batch(self):
    """
    每 8 小时触发一次：创建批次记录，并为每台主机派发子任务。
    """
    Host = apps.get_model("cmdb", "Host")

    now = timezone.now()
    run = RotationRun.objects.create(
        scheduled_for=now,
        started_at=now,
        status=RotationRun.Status.RUNNING,
    )

    # 只轮换启用主机
    qs = Host.objects.filter(is_active=True).values_list("id", flat=True)
    host_ids = list(qs)

    RotationRun.objects.filter(pk=run.pk).update(total_hosts=len(host_ids))

    for host_id in host_ids:
        rotate_one_host_task.delay(host_id=host_id, run_id=str(run.pk))

    return {"run_id": str(run.pk), "total_hosts": len(host_ids)}


@shared_task(bind=True)
def rotate_one_host_task(self, *, host_id: int, run_id: str):
    """轮换单台主机（子任务）。

    额外策略：
    - 若该主机凭据处于 pending 且未过期，认为已有轮换在进行中，直接跳过（避免并发重复轮换）。
    """

    # pending 去重：避免同一主机并发轮换
    cred = HostCredential.objects.filter(host_id=host_id).only(
        "id", "last_rotate_status", "rotated_at"
    ).first()

    if cred and cred.last_rotate_status == "pending" and cred.rotated_at:
        if timezone.now() - cred.rotated_at < timedelta(minutes=PENDING_STALE_MINUTES):
            _inc_run_counts(run_id=run_id, ok=False, skipped=True)
            return {"ok": False, "skipped": True, "reason": "pending_not_expired"}

    result = rotate_one_host_password(host_id, run_id=run_id)
    _inc_run_counts(run_id=run_id, ok=result.ok, skipped=False)
    return {"ok": result.ok, "host_id": result.host_id, "error": result.error}


def _inc_run_counts(*, run_id: str, ok: bool, skipped: bool):
    """回写批次统计，并在最后一台完成时收敛 run 状态。"""

    with transaction.atomic():
        run = RotationRun.objects.select_for_update().get(pk=run_id)

        # 统计：skipped 计入 fail_count（你也可以改成单独字段，这里笔试从简）
        if ok:
            run.success_count = F("success_count") + 1
        else:
            run.fail_count = F("fail_count") + 1

        run.save(update_fields=["success_count", "fail_count", "updated_at"])

        # 重新读取最新值（F 表达式）
        run.refresh_from_db(fields=["total_hosts", "success_count", "fail_count", "status"])

        done = (run.success_count + run.fail_count) >= run.total_hosts and run.total_hosts > 0
        if done and run.status == RotationRun.Status.RUNNING:
            run.finished_at = timezone.now()

            if run.fail_count == 0:
                run.status = RotationRun.Status.SUCCESS
            elif run.success_count == 0:
                run.status = RotationRun.Status.FAILED
            else:
                run.status = RotationRun.Status.PARTIAL

            run.save(update_fields=["finished_at", "status", "updated_at"])
