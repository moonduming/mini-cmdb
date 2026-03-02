import uuid
from django.db import models
from django.utils import timezone
from ..cmdb.models import Host


class RotationRun(models.Model):
    """一次密码轮换批次记录（用于审计和统计）。"""

    class Status(models.TextChoices):
        RUNNING = "running", "运行中"
        SUCCESS = "success", "全部成功"
        PARTIAL = "partial_failed", "部分失败"
        FAILED = "failed", "全部失败"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scheduled_for = models.DateTimeField("计划执行时间", default=timezone.now)
    started_at = models.DateTimeField("开始时间", null=True, blank=True)
    finished_at = models.DateTimeField("结束时间", null=True, blank=True)

    total_hosts = models.PositiveIntegerField("主机总数", default=0)
    success_count = models.PositiveIntegerField("成功数量", default=0)
    fail_count = models.PositiveIntegerField("失败数量", default=0)

    status = models.CharField(
        "执行状态",
        max_length=20,
        choices=Status.choices,
        default=Status.RUNNING,
    )
    message = models.TextField("执行摘要", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "security_rotation_run"
        ordering = ("-created_at",)


class HostCredential(models.Model):
    """当前主机凭据（加密存储）。"""

    class RotateStatus(models.TextChoices):
        SUCCESS = "success", "成功"
        PENDING = "pending", "执行中"
        FAILED = "failed", "失败"

    host = models.OneToOneField(
        Host,
        on_delete=models.CASCADE,
        related_name="credential",
        verbose_name="主机",
    )
    username = models.CharField("用户名", max_length=64, default="root")
    password_enc = models.TextField("加密后的密码")
    enc_version = models.CharField("加密版本", max_length=32, blank=True)

    rotated_at = models.DateTimeField("最近轮换时间", null=True, blank=True)
    last_rotate_status = models.CharField(
        "最近轮换状态",
        max_length=16,
        choices=RotateStatus.choices,
        blank=True,
    )
    last_rotate_error = models.TextField("最近错误信息", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "security_host_credential"


class PasswordRotationHistory(models.Model):
    """密码变更历史记录（审计用）。"""

    class Status(models.TextChoices):
        SUCCESS = "success", "成功"
        PENDING = "pending", "执行中"
        FAILED = "failed", "失败"

    host = models.ForeignKey(
        Host,
        on_delete=models.CASCADE,
        related_name="rotation_histories",
        verbose_name="主机",
    )
    username = models.CharField("用户名", max_length=64, default="root")

    new_password_enc = models.TextField("新密码密文")
    run = models.ForeignKey(
        RotationRun,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="histories",
        verbose_name="所属批次",
    )

    rotated_at = models.DateTimeField("轮换时间", default=timezone.now)
    status = models.CharField(
        "执行结果",
        max_length=16,
        choices=Status.choices,
        default=Status.PENDING,
    )
    error = models.TextField("错误信息", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "security_password_rotation_history"
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["host", "rotated_at"]),
        ]
