# 错误码清单（示例）

这个文件演示**渐进式披露**：`SKILL.md` 里只写一句"详见本文件"，
只有当 Claude 确实需要查错误码时才会读进来。长参考资料都该这么放，
否则它会在 Skill 加载后一直占着上下文。

| code | HTTP | 含义 |
|---|---|---|
| `VALIDATION_FAILED` | 400 | 请求参数校验不通过，`details` 带字段级错误 |
| `UNAUTHENTICATED` | 401 | 缺少或无效的凭证 |
| `PERMISSION_DENIED` | 403 | 已认证但无权限 |
| `RESOURCE_NOT_FOUND` | 404 | 目标资源不存在 |
| `CONFLICT` | 409 | 与当前资源状态冲突（如重复创建） |
| `RATE_LIMITED` | 429 | 触发限流，响应头带 `Retry-After` |
| `INTERNAL_ERROR` | 500 | 服务端异常，对外不暴露细节 |

新增错误码时同步更新本表，并在 `SKILL.md` 里保持只有一行引用。
