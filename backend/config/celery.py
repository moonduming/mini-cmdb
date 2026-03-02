import os
from celery import Celery

# 设置默认 Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("mini_cmdb")

# 从 Django settings 读取 CELERY_ 开头配置
app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()