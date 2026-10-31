# 随机点名器 API 契约

本文档定义前端与后端共同遵守的最小接口契约。当前提交只约定接口，不包含业务实现。

## 通用约定

- 基础路径：`/api`
- 请求与响应格式：`application/json; charset=utf-8`
- 字符串按去除首尾空白后的值校验。
- 同一请求中的候选人以 `id` 唯一标识；`name` 可以重复。
- 成功响应与错误响应均为 JSON。

## 随机点名

### `POST /api/pick`

从本次请求提供的候选人中随机选出指定数量的人。

### 请求体

```json
{
  "candidates": [
    { "id": "student-001", "name": "张三" },
    { "id": "student-002", "name": "李四" },
    { "id": "student-003", "name": "王五" }
  ],
  "count": 1
}
```

字段约束：

| 字段 | 类型 | 必填 | 约束 |
| --- | --- | --- | --- |
| `candidates` | array | 是 | 1～100 项 |
| `candidates[].id` | string | 是 | 去除首尾空白后长度为 1～64；在本次请求中唯一 |
| `candidates[].name` | string | 是 | 去除首尾空白后长度为 1～50 |
| `count` | integer | 否 | 默认值为 `1`；范围为 1～`candidates.length` |

未在契约中定义的额外字段应被忽略，以便后续扩展客户端而不破坏现有服务端。

### 成功响应

状态码：`200 OK`

```json
{
  "picked": [
    { "id": "student-002", "name": "李四" }
  ],
  "candidate_count": 3
}
```

字段说明：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `picked` | array | 被选中的候选人；数量等于请求中的 `count` |
| `candidate_count` | integer | 本次请求中可参与抽取的候选人数 |

同一次响应中的 `picked` 不得包含重复的 `id`。接口不保证多次请求之间不重复点到同一人，也不持久化抽取历史。

## 错误约定

所有错误使用相同结构：

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "请求参数不符合约定",
    "details": [
      {
        "field": "count",
        "reason": "必须小于或等于候选人数"
      }
    ]
  }
}
```

- `code`：稳定、可供程序判断的错误码。
- `message`：面向用户或开发者的简短说明。
- `details`：可选；提供字段级问题。不得包含堆栈、密钥或内部实现信息。

| HTTP 状态码 | `error.code` | 使用场景 |
| --- | --- | --- |
| `400 Bad Request` | `INVALID_JSON` | 请求体不是合法 JSON |
| `422 Unprocessable Entity` | `VALIDATION_ERROR` | 缺少必填字段、字段类型错误、候选人 ID 重复，或字段值超出约束 |
| `500 Internal Server Error` | `INTERNAL_ERROR` | 未预期的服务端错误 |

### 校验错误示例

状态码：`422 Unprocessable Entity`

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "请求参数不符合约定",
    "details": [
      {
        "field": "candidates",
        "reason": "至少需要 1 名候选人"
      }
    ]
  }
}
```
