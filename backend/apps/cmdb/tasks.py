from celery import shared_task
from django.db import transaction
from django.db.models import Count
from django.utils import timezone

from .models import Host, HostCountSnapshot


@shared_task(bind=True)
def daily_host_stat(self):
    """
    每天 00:00 统计主机数量（按城市 + 机房维度），并写入快照表。
    """

    today = timezone.localdate()

    # 按 city + idc 维度聚合
    stats = (
        Host.objects.filter(is_active=True)
        .values("city_id", "idc_id")
        .annotate(host_count=Count("id"))
    )

    created = 0
    updated = 0

    with transaction.atomic():
        for row in stats:
            obj, is_created = HostCountSnapshot.objects.update_or_create(
                date=today,
                city_id=row["city_id"],
                idc_id=row["idc_id"],
                defaults={"host_count": row["host_count"]},
            )

            if is_created:
                created += 1
            else:
                updated += 1

    return {
        "date": str(today),
        "created": created,
        "updated": updated,
        "total_groups": created + updated,
    }