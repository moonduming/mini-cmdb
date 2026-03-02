# mini-cmdb

一个用于笔试展示的 `mini CMDB + 安全轮换 + 运维探测` 项目，基于 Django / DRF / PostgreSQL / Celery / Redis 实现。

项目覆盖以下能力：

- CMDB 资产模型设计：城市、机房、主机
- 资产 CRUD 接口
- 主机 Ping 探测接口
- 主机 root 密码加密存储与定时轮换
- 每日按城市 / 机房维度统计主机数量
- 请求耗时中间件与基础日志

## 技术栈

- Django `6.0.2`
- Django REST Framework（DRF）
- PostgreSQL
- Celery
- Redis
- cryptography（Fernet）

## 目录结构

```text
backend/
├── apps/
│   ├── cmdb/       # 资产域：城市、机房、主机、每日统计
│   ├── security/   # 安全域：凭据、密码轮换、轮换审计、Celery 任务
│   ├── ops/        # 运维域：主机 ping 探测
│   └── __init__.py
├── common/         # 通用能力：统一分页、统一返回、请求耗时中间件
├── config/         # Django 配置、URL、Celery 初始化
└── manage.py
```

重点目录说明：

- `backend/apps/cmdb`
  - `models.py`：`City`、`IDC`、`Host`、`HostCountSnapshot`
  - `serializers.py`：CMDB 相关序列化
  - `views.py`：CMDB CRUD 接口
  - `tasks.py`：每日主机统计任务
- `backend/apps/security`
  - `models.py`：`HostCredential`、`PasswordRotationHistory`、`RotationRun`
  - `services/password_rotation.py`：密码生成、加解密、单机轮换逻辑
  - `tasks.py`：批量轮换与单机轮换 Celery 任务
  - `views.py`：手工触发轮换、查询轮换批次
- `backend/apps/ops`
  - `views.py`：主机 Ping 探测 API
- `backend/common`
  - `drf.py`：统一分页 `CountDataPagination`、统一返回 `MessageDataJSONRenderer`、请求耗时中间件

## 本地启动

### 1. 准备 Python 环境

建议使用虚拟环境：

```bash
python3 -m venv .venv
source .venv/bin/activate
```

安装依赖（当前仓库未提供依赖锁文件，可先按以下方式安装）：

```bash
pip install "Django==6.0.2" djangorestframework "psycopg[binary]" celery redis cryptography
```

### 2. 准备 PostgreSQL

当前代码默认连接如下数据库（见 `backend/config/settings.py`）：

- 数据库名：`mydb`
- 用户：`postgres`
- 密码：`123456`
- 地址：`127.0.0.1:5432`

请先确保本地 PostgreSQL 已启动，并创建数据库：

```bash
createdb mydb
```

如果你的本地账号不是 `postgres / 123456`，请先修改 `backend/config/settings.py`，或自行扩展为环境变量方式。

### 3. 准备 Redis

本项目使用 Redis 作为 Celery broker/result backend，默认地址：

- broker：`redis://127.0.0.1:6379/0`
- result backend：`redis://127.0.0.1:6379/1`

先启动 Redis：

```bash
redis-server
```

### 4. 配置环境变量

至少建议配置 `CMDB_FERNET_KEY`：

```bash
export CMDB_FERNET_KEY='YOUR_FERNET_KEY'
```

说明：

- `CMDB_FERNET_KEY` 用于加密/解密主机 root 密码
- 必须是合法的 Fernet key
- 本质上是“32 字节原始 key 的 urlsafe-base64 编码”
- 通常长度约为 `44`，且末尾常见 `=`

可以使用 Python 生成：

```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

如果 `CMDB_FERNET_KEY` 非法，Django 启动时会直接报错：

- `CMDB_FERNET_KEY 非法：必须为 Fernet 规范的 urlsafe-base64 key`

注意：

- 当前代码中若未设置该环境变量，会使用一个仅用于开发测试的默认值
- 生产环境必须通过环境变量注入，不能使用代码中的 DEV 默认值
- 更换 key 会导致历史密文无法解密

### 5. 执行迁移

```bash
python backend/manage.py makemigrations
python backend/manage.py migrate
```

### 6. 启动 Django

```bash
python backend/manage.py runserver
```

默认访问：

- `http://127.0.0.1:8000/`

### 7. 启动 Celery Worker

在新终端中执行：

```bash
cd backend
celery -A config worker -l info
```

### 8. 启动 Celery Beat

在另一个终端中执行：

```bash
cd backend
celery -A config beat -l info
```

## 环境变量配置

当前代码里显式使用的环境变量主要是：

- `CMDB_FERNET_KEY`
  - 用途：主机 root 密码加解密
  - 要求：必须是合法 Fernet key
  - 生产建议：由部署平台注入，不写死到仓库

建议你在生产化时进一步把以下配置也改成环境变量：

- `SECRET_KEY`
- `DEBUG`
- `ALLOWED_HOSTS`
- PostgreSQL 连接信息
- Redis 连接信息

## 关键功能说明

### 1. CMDB CRUD

提供以下资源的增删改查：

- 城市（`City`）
- 机房（`IDC`）
- 主机（`Host`）

主机与机房关系约束：

- `Host.idc` 决定其所属机房
- `Host.city` 与 `Host.idc.city` 应保持一致
- 当前实现中创建 / 更新主机时，会自动把 `city` 同步为 `idc.city`

### 2. 统一分页返回

全局 DRF 分页类为：

- `common.drf.CountDataPagination`

目标返回格式：

```json
{
  "count": 100,
  "data": []
}
```

### 3. 统一返回格式

全局 DRF renderer 为：

- `common.drf.MessageDataJSONRenderer`

目标返回格式：

非分页接口：

```json
{
  "message": "ok",
  "data": {}
}
```

错误时：

```json
{
  "message": "error",
  "data": {
    "detail": "..."
  }
}
```

### 4. 请求耗时中间件

中间件：

- `common.drf.RequestTimingMiddleware`

作用：

- 统计每个请求耗时
- 输出 `method / path / status / cost_ms` 到日志

### 5. Ping API

接口位置：

- `POST /api/ops/hosts/{host_id}/ping/`

能力：

- 对指定主机做一次同步 Ping 探测
- 更新 `Host.last_ping_ok` 和 `Host.last_ping_at`
- 默认有 10 秒冷却时间，避免高频重复探测

### 6. 密码轮换

核心流程：

- 生成随机密码
- 用 Fernet 加密后写入 `HostCredential`
- 先记为 `pending`
- 调用“应用到主机”的执行逻辑
- 最终收敛到 `success / failed`
- 写入 `PasswordRotationHistory`
- 批次执行信息记录在 `RotationRun`

说明：

- 当前代码中使用 `pending` 表示中间态，便于审计
- 当前并发控制采用轻量方案：依赖 `pending + 超时窗口`
- 目前未引入分布式锁，属于有意简化，后续可扩展
- 当前已提供手工触发轮换与查询轮换批次的 API

### 7. 每天统计

定时任务：

- `apps.cmdb.tasks.daily_host_stat`

默认行为：

- 每天 `00:00`
- 统计所有启用主机（`is_active=True`）
- 按 `城市 + 机房` 维度聚合
- 将结果写入 `HostCountSnapshot`

### 8. Celery Beat 当前调度说明

当前代码中的默认调度是：

- 密码轮换：每 `8` 小时一次
- 每日统计：每天 `00:00`

为了测试方便，代码里预留了注释切换方案：

- 密码轮换可切到每 `2` 分钟
- 每日统计可切到每 `3` 分钟

## 常见问题排查

### 1. `ModuleNotFoundError: No module named 'django'`

说明依赖未安装或虚拟环境未激活。

处理：

```bash
source .venv/bin/activate
pip install "Django==6.0.2" djangorestframework "psycopg[binary]" celery redis cryptography
```

### 2. Redis 未安装 / 未启动

常见报错：

- `Error 61 connecting to 127.0.0.1:6379`
- Celery worker/beat 无法连接 broker

处理：

- 安装 Redis
- 启动 `redis-server`
- 确认 `127.0.0.1:6379` 可访问

### 3. `CMDB_FERNET_KEY` 不合法

常见报错：

- `CMDB_FERNET_KEY 非法：必须为 Fernet 规范的 urlsafe-base64 key`

原因：

- key 不是合法的 Fernet 格式
- 手工复制时丢失末尾 `=`
- 误把任意字符串当作 Fernet key 使用

处理：

```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

### 4. `celerybeat-schedule.db` 是什么？

这是 Celery Beat 的本地调度状态文件（常见文件名为 `celerybeat-schedule`，某些环境里也可能看到以 `.db` 形式呈现）。

作用：

- 保存 Beat 调度器的本地状态
- 帮助 Celery 记录上次调度时间

说明：

- 它不是业务数据表
- 通常不需要提交到仓库
- 停止 beat 后可以删除，重新启动会自动生成

### 5. PostgreSQL 连接失败

常见原因：

- 数据库未启动
- `mydb` 数据库不存在
- 用户名 / 密码和本地实际不一致

处理：

- 确认 PostgreSQL 已启动
- 创建数据库 `mydb`
- 检查 `backend/config/settings.py` 中的连接配置

## 后续可扩展方向

- 接入鉴权（如 Token / JWT / Session + 权限校验）
- 增加更细粒度的权限模型（按资源、按动作、按主机分组授权）
- 引入 Redis 分布式锁，提升密码轮换并发一致性
- 增加异步幂等控制，避免任务重复执行
- 密码轮换接入真实远程执行器（SSH / Agent）
- 增加批量探测能力（批量 Ping / 并发探测）
- 引入任务重试、死信、失败分类
- 增加 `enc_version` 对应的密钥轮换策略
- 增加结构化日志与 trace id
- 补齐单元测试、接口测试、任务测试
- 对接 Prometheus / Sentry 等可观测性工具
- 增加审计查询接口（查看轮换批次、失败原因、历史记录）
