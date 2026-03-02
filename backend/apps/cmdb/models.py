from django.db import models
from django.core.exceptions import ValidationError


class TimeStampedModel(models.Model):
    """通用的创建时间与更新时间字段（抽象基类）。"""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class City(TimeStampedModel):
    """城市/区域：表示机房（IDC）所在的城市。"""

    name = models.CharField("城市名称", max_length=64, unique=True)
    code = models.CharField("城市编码", max_length=32, blank=True, default="", db_index=True)

    class Meta:
        db_table = "cmdb_city"
        verbose_name = "City"
        verbose_name_plural = "Cities"


class IDC(TimeStampedModel):
    """机房（IDC）：数据中心/机房信息。"""

    city = models.ForeignKey(
        City,
        verbose_name="所属城市",
        on_delete=models.PROTECT,
        related_name="idcs",
    )
    name = models.CharField("机房名称", max_length=128)
    address = models.CharField("机房地址", max_length=255, blank=True, default="")
    remark = models.TextField("备注", blank=True, default="")

    class Meta:
        db_table = "cmdb_idc"
        verbose_name = "IDC"
        verbose_name_plural = "IDCs"
        constraints = [
            models.UniqueConstraint(fields=["city", "name"], name="uniq_idc_city_name"),
        ]


class Host(TimeStampedModel):
    """主机资产信息。"""

    class OSType(models.TextChoices):
        LINUX = "linux", "Linux"
        WINDOWS = "windows", "Windows"
        OTHER = "other", "Other"

    class EnvType(models.TextChoices):
        PROD = "prod", "Production"
        STAGING = "staging", "Staging"
        TEST = "test", "Test"
        DEV = "dev", "Development"

    hostname = models.CharField("主机名", max_length=128, db_index=True)
    ip = models.GenericIPAddressField("IP 地址", protocol="IPv4", unique=True)

    city = models.ForeignKey(
        City,
        verbose_name="所属城市",
        on_delete=models.PROTECT,
        related_name="hosts",
    )
    idc = models.ForeignKey(
        IDC,
        verbose_name="所属机房",
        on_delete=models.PROTECT,
        related_name="hosts",
    )

    os_type = models.CharField(
        "操作系统类型",
        max_length=16,
        choices=OSType.choices,
        default=OSType.LINUX,
    )
    env = models.CharField(
        "环境类型",
        max_length=16,
        choices=EnvType.choices,
        default=EnvType.PROD,
    )

    is_active = models.BooleanField("是否启用", default=True, db_index=True)

    # 运维字段：记录最近一次 ping 的结果快照
    last_ping_ok = models.BooleanField("最近一次 Ping 是否成功", null=True, blank=True)
    last_ping_at = models.DateTimeField("最近一次 Ping 时间", null=True, blank=True)

    remark = models.TextField("备注", blank=True, default="")

    class Meta:
        db_table = "cmdb_host"
        verbose_name = "Host"
        verbose_name_plural = "Hosts"
        indexes = [
            models.Index(fields=["city", "idc"], name="idx_host_city_idc"),
            models.Index(fields=["is_active"], name="idx_host_active"),
            models.Index(fields=["hostname"], name="idx_host_hostname"),
        ]

    def clean(self):
        """数据一致性校验：host.city 必须与 idc.city 保持一致"""
        super().clean()
        if self.idc_id and self.city_id and self.idc.city_id != self.city_id:
            raise ValidationError({"city": "city 必须与 idc 所属城市一致"})


class HostCountSnapshot(models.Model):
    """每日主机数量统计快照（按城市 + 机房维度）。"""

    date = models.DateField("统计日期", db_index=True)

    city = models.ForeignKey(
        City,
        verbose_name="所属城市",
        on_delete=models.CASCADE,
        related_name="host_count_snapshots",
    )
    idc = models.ForeignKey(
        IDC,
        verbose_name="所属机房",
        on_delete=models.CASCADE,
        related_name="host_count_snapshots",
    )

    host_count = models.PositiveIntegerField("主机数量")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cmdb_host_count_snapshot"
        verbose_name = "Host Count Snapshot"
        verbose_name_plural = "Host Count Snapshots"
        unique_together = ("date", "city", "idc")
        indexes = [
            models.Index(fields=["date", "city"], name="idx_snapshot_date_city"),
            models.Index(fields=["date", "idc"], name="idx_snapshot_date_idc"),
        ]
