# API 接口文档

Base URL（本地）：

- `http://127.0.0.1:8000`

## 统一返回格式

### 1. 分页接口

```json
{
  "count": 2,
  "data": []
}
```

字段说明：

- `count`：总数
- `data`：当前页数据列表

### 2. 非分页接口

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

---

# cmdb 模块

资源：

- 城市 `City`
- 机房 `IDC`
- 主机 `Host`

## 1. 城市列表

- URL: `/api/cmdb/cities/`
- Method: `GET`
- 类型: 人工触发

### Query 参数

- `page`：页码，可选
- `page_size`：每页数量，可选，最大 100
- `search`：按 `name / code` 搜索，可选
- `ordering`：支持 `id,name,code,created_at,updated_at`，可选

### Body

无

### Response 示例

```json
{
  "count": 2,
  "data": [
    {
      "id": 1,
      "name": "上海",
      "code": "sh",
      "created_at": "2026-03-02T10:00:00+08:00",
      "updated_at": "2026-03-02T10:00:00+08:00"
    }
  ]
}
```

### 错误示例

```json
{
  "message": "error",
  "data": {
    "detail": "Invalid page."
  }
}
```

---

## 2. 创建城市

- URL: `/api/cmdb/cities/`
- Method: `POST`
- 类型: 人工触发

### Query 参数

无

### Body

```json
{
  "name": "上海",
  "code": "sh"
}
```

### Response 示例

```json
{
  "message": "ok",
  "data": {
    "id": 1,
    "name": "上海",
    "code": "sh",
    "created_at": "2026-03-02T10:00:00+08:00",
    "updated_at": "2026-03-02T10:00:00+08:00"
  }
}
```

### 错误示例

```json
{
  "message": "error",
  "data": {
    "name": [
      "city with this 城市名称 already exists."
    ]
  }
}
```

---

## 3. 城市详情

- URL: `/api/cmdb/cities/{id}/`
- Method: `GET`
- 类型: 人工触发

### Query 参数

无

### Body

无

### Response 示例

```json
{
  "message": "ok",
  "data": {
    "id": 1,
    "name": "上海",
    "code": "sh",
    "created_at": "2026-03-02T10:00:00+08:00",
    "updated_at": "2026-03-02T10:00:00+08:00"
  }
}
```

### 错误示例

```json
{
  "message": "error",
  "data": {
    "detail": "Not found."
  }
}
```

---

## 4. 更新城市

- URL: `/api/cmdb/cities/{id}/`
- Method: `PUT` / `PATCH`
- 类型: 人工触发

### Query 参数

无

### Body

```json
{
  "name": "上海",
  "code": "cn-sh"
}
```

### Response 示例

```json
{
  "message": "ok",
  "data": {
    "id": 1,
    "name": "上海",
    "code": "cn-sh",
    "created_at": "2026-03-02T10:00:00+08:00",
    "updated_at": "2026-03-02T10:05:00+08:00"
  }
}
```

### 错误示例

```json
{
  "message": "error",
  "data": {
    "name": [
      "This field may not be blank."
    ]
  }
}
```

---

## 5. 删除城市

- URL: `/api/cmdb/cities/{id}/`
- Method: `DELETE`
- 类型: 人工触发

### Query 参数

无

### Body

无

### Response 示例

HTTP `204 No Content`

### 错误示例

```json
{
  "message": "error",
  "data": {
    "detail": "Cannot delete some instances of model 'City' because they are referenced through protected foreign keys: 'IDC.city', 'Host.city'."
  }
}
```

---

## 6. 机房列表

- URL: `/api/cmdb/idcs/`
- Method: `GET`
- 类型: 人工触发

### Query 参数

- `page`：页码，可选
- `page_size`：每页数量，可选
- `search`：按 `name / address / remark / city__name / city__code` 搜索，可选
- `ordering`：支持 `id,name,city,created_at,updated_at`，可选

### Body

无

### Response 示例

```json
{
  "count": 1,
  "data": [
    {
      "id": 1,
      "name": "浦东 A 机房",
      "city_id": 1,
      "city_name": "上海",
      "address": "浦东新区 xx 路",
      "remark": "",
      "created_at": "2026-03-02T10:10:00+08:00",
      "updated_at": "2026-03-02T10:10:00+08:00"
    }
  ]
}
```

### 错误示例

```json
{
  "message": "error",
  "data": {
    "detail": "Invalid page."
  }
}
```

---

## 7. 创建机房

- URL: `/api/cmdb/idcs/`
- Method: `POST`
- 类型: 人工触发

### Query 参数

无

### Body

```json
{
  "name": "浦东 A 机房",
  "city_id": 1,
  "address": "浦东新区 xx 路",
  "remark": "主机房"
}
```

### Response 示例

```json
{
  "message": "ok",
  "data": {
    "id": 1,
    "name": "浦东 A 机房",
    "city_id": 1,
    "city_name": "上海",
    "address": "浦东新区 xx 路",
    "remark": "主机房",
    "created_at": "2026-03-02T10:10:00+08:00",
    "updated_at": "2026-03-02T10:10:00+08:00"
  }
}
```

### 错误示例

```json
{
  "message": "error",
  "data": {
    "non_field_errors": [
      "The fields city, name must make a unique set."
    ]
  }
}
```

---

## 8. 机房详情

- URL: `/api/cmdb/idcs/{id}/`
- Method: `GET`
- 类型: 人工触发

### Query 参数

无

### Body

无

### Response 示例

```json
{
  "message": "ok",
  "data": {
    "id": 1,
    "name": "浦东 A 机房",
    "city_id": 1,
    "city_name": "上海",
    "address": "浦东新区 xx 路",
    "remark": "主机房",
    "created_at": "2026-03-02T10:10:00+08:00",
    "updated_at": "2026-03-02T10:10:00+08:00"
  }
}
```

### 错误示例

```json
{
  "message": "error",
  "data": {
    "detail": "Not found."
  }
}
```

---

## 9. 更新机房

- URL: `/api/cmdb/idcs/{id}/`
- Method: `PUT` / `PATCH`
- 类型: 人工触发

### Query 参数

无

### Body

```json
{
  "name": "浦东 B 机房",
  "city_id": 1,
  "address": "浦东新区 yy 路",
  "remark": "扩容后机房"
}
```

### Response 示例

```json
{
  "message": "ok",
  "data": {
    "id": 1,
    "name": "浦东 B 机房",
    "city_id": 1,
    "city_name": "上海",
    "address": "浦东新区 yy 路",
    "remark": "扩容后机房",
    "created_at": "2026-03-02T10:10:00+08:00",
    "updated_at": "2026-03-02T10:20:00+08:00"
  }
}
```

### 错误示例

```json
{
  "message": "error",
  "data": {
    "city_id": [
      "Invalid pk \"999\" - object does not exist."
    ]
  }
}
```

---

## 10. 删除机房

- URL: `/api/cmdb/idcs/{id}/`
- Method: `DELETE`
- 类型: 人工触发

### Query 参数

无

### Body

无

### Response 示例

HTTP `204 No Content`

### 错误示例

```json
{
  "message": "error",
  "data": {
    "detail": "Cannot delete some instances of model 'IDC' because they are referenced through protected foreign keys: 'Host.idc'."
  }
}
```

---

## 11. 主机列表

- URL: `/api/cmdb/hosts/`
- Method: `GET`
- 类型: 人工触发

### Query 参数

- `page`：页码，可选
- `page_size`：每页数量，可选
- `search`：按 `hostname / ip / remark / city__name / city__code / idc__name` 搜索，可选
- `ordering`：支持 `id,hostname,ip,city,idc,is_active,last_ping_ok,last_ping_at,created_at,updated_at`
- `city_id`：按城市过滤，可选
- `idc_id`：按机房过滤，可选
- `is_active`：按启用状态过滤，可选，支持 `true/false/1/0`

### Body

无

### Response 示例

```json
{
  "count": 1,
  "data": [
    {
      "id": 1,
      "hostname": "web-01",
      "ip": "10.0.0.10",
      "os_type": "linux",
      "env": "prod",
      "is_active": true,
      "city_id": "1",
      "city_name": "上海",
      "idc_id": 1,
      "idc_name": "浦东 A 机房",
      "last_ping_ok": true,
      "last_ping_at": "2026-03-02T10:30:00+08:00",
      "remark": "Nginx 网关",
      "created_at": "2026-03-02T10:15:00+08:00",
      "updated_at": "2026-03-02T10:30:00+08:00"
    }
  ]
}
```

### 错误示例

```json
{
  "message": "error",
  "data": {
    "detail": "Invalid page."
  }
}
```

---

## 12. 创建主机

- URL: `/api/cmdb/hosts/`
- Method: `POST`
- 类型: 人工触发

### Query 参数

无

### Body

说明：

- 当前实现中不需要传 `city_id`
- `city` 会由 `idc_id` 自动推导并写入

```json
{
  "hostname": "web-01",
  "ip": "10.0.0.10",
  "os_type": "linux",
  "env": "prod",
  "is_active": true,
  "idc_id": 1,
  "remark": "Nginx 网关"
}
```

### Response 示例

```json
{
  "message": "ok",
  "data": {
    "id": 1,
    "hostname": "web-01",
    "ip": "10.0.0.10",
    "os_type": "linux",
    "env": "prod",
    "is_active": true,
    "city_id": "1",
    "city_name": "上海",
    "idc_id": 1,
    "idc_name": "浦东 A 机房",
    "last_ping_ok": null,
    "last_ping_at": null,
    "remark": "Nginx 网关",
    "created_at": "2026-03-02T10:15:00+08:00",
    "updated_at": "2026-03-02T10:15:00+08:00"
  }
}
```

### 错误示例

```json
{
  "message": "error",
  "data": {
    "ip": [
      "host with this IP 地址 already exists."
    ]
  }
}
```

---

## 13. 主机详情

- URL: `/api/cmdb/hosts/{id}/`
- Method: `GET`
- 类型: 人工触发

### Query 参数

无

### Body

无

### Response 示例

```json
{
  "message": "ok",
  "data": {
    "id": 1,
    "hostname": "web-01",
    "ip": "10.0.0.10",
    "os_type": "linux",
    "env": "prod",
    "is_active": true,
    "city_id": "1",
    "city_name": "上海",
    "idc_id": 1,
    "idc_name": "浦东 A 机房",
    "last_ping_ok": true,
    "last_ping_at": "2026-03-02T10:30:00+08:00",
    "remark": "Nginx 网关",
    "created_at": "2026-03-02T10:15:00+08:00",
    "updated_at": "2026-03-02T10:30:00+08:00"
  }
}
```

### 错误示例

```json
{
  "message": "error",
  "data": {
    "detail": "Not found."
  }
}
```

---

## 14. 更新主机

- URL: `/api/cmdb/hosts/{id}/`
- Method: `PUT` / `PATCH`
- 类型: 人工触发

### Query 参数

无

### Body

说明：

- 如果修改了 `idc_id`，系统会自动把 `city` 同步为新机房所属城市

```json
{
  "hostname": "web-01",
  "ip": "10.0.0.11",
  "os_type": "linux",
  "env": "staging",
  "is_active": true,
  "idc_id": 1,
  "remark": "预发环境"
}
```

### Response 示例

```json
{
  "message": "ok",
  "data": {
    "id": 1,
    "hostname": "web-01",
    "ip": "10.0.0.11",
    "os_type": "linux",
    "env": "staging",
    "is_active": true,
    "city_id": "1",
    "city_name": "上海",
    "idc_id": 1,
    "idc_name": "浦东 A 机房",
    "last_ping_ok": true,
    "last_ping_at": "2026-03-02T10:30:00+08:00",
    "remark": "预发环境",
    "created_at": "2026-03-02T10:15:00+08:00",
    "updated_at": "2026-03-02T10:40:00+08:00"
  }
}
```

### 错误示例

```json
{
  "message": "error",
  "data": {
    "idc_id": [
      "Invalid pk \"999\" - object does not exist."
    ]
  }
}
```

---

## 15. 删除主机

- URL: `/api/cmdb/hosts/{id}/`
- Method: `DELETE`
- 类型: 人工触发

### Query 参数

无

### Body

无

### Response 示例

HTTP `204 No Content`

### 错误示例

```json
{
  "message": "error",
  "data": {
    "detail": "Not found."
  }
}
```

---

## 16. 定时任务：每日主机统计（不对外暴露 API）

- 模块：`cmdb`
- 类型：定时任务
- 任务名：`apps.cmdb.tasks.daily_host_stat`
- 默认调度：每天 `00:00`
- 测试可切换：每 `3` 分钟（通过代码中的注释方案切换）

### 行为说明

- 仅统计 `is_active=True` 的主机
- 按 `city_id + idc_id` 聚合
- 写入 `HostCountSnapshot`
- 使用 `update_or_create`，同一天重复触发不会插入重复快照

### 成功返回（Celery 任务结果示意）

```json
{
  "date": "2026-03-02",
  "created": 2,
  "updated": 0,
  "total_groups": 2
}
```

---

# ops 模块

## 1. 主机 Ping 探测

- URL: `/api/ops/hosts/{host_id}/ping/`
- Method: `POST`
- 类型: 人工触发

### Query 参数

无

### Body

无

### Response 示例

首次探测：

```json
{
  "message": "ok",
  "data": {
    "host_id": 1,
    "ip": "10.0.0.10",
    "reachable": true,
    "checked_at": "2026-03-02 10:30:00",
    "cached": false
  }
}
```

冷却时间内重复调用（默认 10 秒）：

```json
{
  "message": "ok",
  "data": {
    "host_id": 1,
    "ip": "10.0.0.10",
    "reachable": true,
    "checked_at": "2026-03-02 10:30:00",
    "cached": true
  }
}
```

### 错误示例

主机不存在：

```json
{
  "message": "error",
  "data": {
    "detail": "Not found."
  }
}
```

---

# security 模块

## 1. 手工触发批量密码轮换

- URL: `/api/security/rotate/trigger/`
- Method: `POST`
- 类型: 人工触发

### Query 参数

无

### Body

无

### Response 示例

```json
{
  "message": "ok",
  "data": {
    "task_id": "fbc7b64e-9d99-4d59-97f6-1d4a9bb56a98",
    "queued": true
  }
}
```

### 错误示例

```json
{
  "message": "error",
  "data": {
    "detail": "Celery broker unavailable."
  }
}
```

---

## 2. 轮换批次列表

- URL: `/api/security/runs/`
- Method: `GET`
- 类型: 人工触发

### Query 参数

- `limit`：返回最近多少条，默认 `20`，最大 `100`

### Body

无

### Response 示例

```json
{
  "message": "ok",
  "data": [
    {
      "id": "7b604d3c-bb5c-4a4f-8f67-8b9a14c9e38d",
      "scheduled_for": "2026-03-02T08:00:00+08:00",
      "started_at": "2026-03-02T08:00:00+08:00",
      "finished_at": "2026-03-02T08:00:05+08:00",
      "total_hosts": 3,
      "success_count": 3,
      "fail_count": 0,
      "status": "success",
      "message": "",
      "created_at": "2026-03-02T08:00:00+08:00",
      "updated_at": "2026-03-02T08:00:05+08:00"
    }
  ]
}
```

### 错误示例

```json
{
  "message": "error",
  "data": {
    "detail": "Authentication credentials were not provided."
  }
}
```

---

## 3. 轮换批次详情

- URL: `/api/security/runs/{run_id}/`
- Method: `GET`
- 类型: 人工触发

### Query 参数

无

### Body

无

### Response 示例

```json
{
  "message": "ok",
  "data": {
    "id": "7b604d3c-bb5c-4a4f-8f67-8b9a14c9e38d",
    "scheduled_for": "2026-03-02T08:00:00+08:00",
    "started_at": "2026-03-02T08:00:00+08:00",
    "finished_at": "2026-03-02T08:00:05+08:00",
    "total_hosts": 3,
    "success_count": 3,
    "fail_count": 0,
    "status": "success",
    "message": "",
    "created_at": "2026-03-02T08:00:00+08:00",
    "updated_at": "2026-03-02T08:00:05+08:00"
  }
}
```

### 错误示例

```json
{
  "message": "error",
  "data": {
    "detail": "Not found."
  }
}
```

---

## 4. 定时任务：批量密码轮换（不对外暴露 API）

- 模块：`security`
- 类型：定时任务
- 任务名：`apps.security.tasks.rotate_passwords_batch`
- 默认调度：每 `8` 小时一次
- 测试可切换：每 `2` 分钟（通过代码中的注释方案切换）

### 行为说明

- 创建一条 `RotationRun` 批次记录
- 查询所有 `is_active=True` 的主机
- 若当前无可轮换主机，批次会直接结束为成功态
- 为每台主机派发一个 `rotate_one_host_task`
- 子任务中调用 `rotate_one_host_password`
- 如果主机当前凭据处于 `pending` 且未超过超时窗口，会跳过本次轮换
- 轮换中间态会先写成 `pending`，用于审计
- 最终更新 `HostCredential` 和 `PasswordRotationHistory`

### 成功返回（Celery 任务结果示意）

```json
{
  "run_id": "7b604d3c-bb5c-4a4f-8f67-8b9a14c9e38d",
  "total_hosts": 3
}
```

---

## 5. 子任务：单机密码轮换（内部任务，不对外暴露 API）

- 模块：`security`
- 类型：内部异步任务
- 任务名：`apps.security.tasks.rotate_one_host_task`

### 行为说明

- 检查当前主机是否存在未过期的 `pending`
- 如果存在，则跳过并计入批次统计
- 否则执行单机轮换逻辑
- 更新所属 `RotationRun` 的 `success_count / fail_count`
- 当所有主机都处理完成后，收敛批次状态为：
  - `success`
  - `failed`
  - `partial_failed`

### 成功返回（Celery 任务结果示意）

```json
{
  "ok": true,
  "host_id": 1,
  "error": ""
}
```

### 跳过示例

```json
{
  "ok": false,
  "skipped": true,
  "reason": "pending_not_expired"
}
```
