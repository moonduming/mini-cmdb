import secrets
import string
from dataclasses import dataclass
from typing import Optional, Tuple
from django.conf import settings
from cryptography.fernet import Fernet, InvalidToken
from django.db import transaction
from django.utils import timezone
from ..models import HostCredential, PasswordRotationHistory
from ...cmdb.models import Host


@dataclass(frozen=True)
class RotateResult:
    """单台主机轮换结果。"""

    ok: bool
    host_id: int
    username: str
    rotated_at: timezone.datetime
    error: str = ""


def _get_fernet() -> Fernet:
    """获取 Fernet 实例。
    - Fernet key 必须是 urlsafe base64 编码的 32-byte key。
    - 可通过 `Fernet.generate_key()` 生成。
    """
    return Fernet(settings.CMDB_FERNET_KEY.encode("utf-8"))


def encrypt_password(plain: str) -> str:
    """加密明文密码"""
    f = _get_fernet()
    token = f.encrypt(plain.encode("utf-8"))
    return token.decode("utf-8")


def decrypt_password(token: str) -> str:
    """解密密文密码"""
    f = _get_fernet()
    try:
        plain = f.decrypt(token.encode("utf-8"))
        return plain.decode("utf-8")
    except InvalidToken as e:
        raise ValueError("密码密文无法解密（密钥不匹配或数据损坏）") from e


def generate_random_password(length: int = 20) -> str:
    """生成随机密码。
    - 使用 secrets 提供的安全随机数
    - 默认长度 20
    """
    if length < 12:
        length = 12
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*_-+"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def apply_password_to_host(host: Host, username: str, new_password: str) -> Tuple[bool, str]:
    """将新密码“应用”到主机。
    返回： (ok, error_message)
    """
    # TODO: 替换为真实实现
    return True, ""


def rotate_one_host_password(
    host_id: int,
    *,
    run_id: Optional[str] = None,
    username: str = "root",
    password_length: int = 20,
) -> RotateResult:
    """
    轮换单台主机密码：生成新密码 → 应用到主机 → 加密入库 → 写审计历史。
    """

    host = Host.objects.get(pk=host_id)
    rotated_at = timezone.now()

    # 生成新密码
    new_plain = generate_random_password(password_length)
    # 加密
    new_enc = encrypt_password(new_plain)

    # 写库（pending），确保“数据库没成功就不会去改主机”
    with transaction.atomic():
        cred, _created = HostCredential.objects.select_for_update().get_or_create(
            host=host,
            defaults={
                "username": username,
                "password_enc": "",
            },
        )

        old_enc = cred.password_enc

        cred.username = username
        cred.password_enc = new_enc
        cred.rotated_at = rotated_at
        cred.last_rotate_status = "pending"
        cred.last_rotate_error = ""
        cred.save(update_fields=[
            "username",
            "password_enc",
            "rotated_at",
            "last_rotate_status",
            "last_rotate_error",
            "updated_at",
        ])

        history = PasswordRotationHistory.objects.create(
            host=host,
            username=username,
            new_password_enc=new_enc,
            run_id=run_id,
            rotated_at=rotated_at,
            status=PasswordRotationHistory.Status.PENDING,
            error="",
        )

    # 改主机（慢 IO；不要放在事务里）
    ok, err = apply_password_to_host(host, username, new_plain)

    # 落最终结果（success/failed）
    with transaction.atomic():
        cred = HostCredential.objects.select_for_update().get(host=host)

        if ok:
            cred.last_rotate_status = "success"
            cred.last_rotate_error = ""
            cred.save(update_fields=["last_rotate_status", "last_rotate_error", "updated_at"])

            PasswordRotationHistory.objects.filter(pk=history.id).update(
                status=PasswordRotationHistory.Status.SUCCESS,
                error="",
            )
            return RotateResult(ok=True, host_id=host.id, username=username, rotated_at=rotated_at)

        # apply 失败：回滚 password_enc 到旧值
        cred.password_enc = old_enc
        cred.last_rotate_status = "failed"
        cred.last_rotate_error = err or "unknown"
        cred.save(update_fields=["password_enc", "last_rotate_status", "last_rotate_error", "updated_at"])

        PasswordRotationHistory.objects.filter(pk=history.id).update(
            status=PasswordRotationHistory.Status.PENDING,
            error=err or "unknown",
        )
        return RotateResult(ok=False, host_id=host.id, username=username, rotated_at=rotated_at, error=err or "unknown")
