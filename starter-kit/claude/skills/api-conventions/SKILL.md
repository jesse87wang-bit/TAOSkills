---
name: api-conventions
description: 本仓库的 API 设计与错误处理约定。在新增或修改 HTTP 接口、路由、请求校验、错误返回时应用。
paths:
  - "src/api/**"
  - "src/routes/**"
  - "**/*controller*"
user-invocable: false
---

新增接口时遵守：

- 路由命名用复数名词，动作靠 HTTP 方法表达：`GET /users/:id`，不要 `GET /getUser`。
- 所有入参在进入业务逻辑前校验，失败返回 `400` 并带字段级错误。
- 错误响应统一为 `{ "error": { "code": "SNAKE_CASE_CODE", "message": "给人看的描述" } }`。
- 不要把内部异常直接透传给客户端；记日志，对外返回通用 message。
- 每个新增接口都要有一个 happy path 测试和一个错误路径测试。

完整错误码清单见 `references/error-codes.md`，需要时再读，不要预先加载。
