# Changelog

## v3.0

- 从“软约束 Skill”升级为**强协议 Skill**。
- 新增三层架构：`Decision Engine → Decision Schema → Renderer`。
- 新增固定 `JN Decision Schema`，不同 Agent 必须先填同一结构再输出。
- 文字版固定为 10 个模块，模块名、顺序、表格列名和数量上限统一。
- 视觉版改为固定 Renderer；宿主支持 SVG/HTML 时必须优先确定性渲染。
- 固定画布 1200×1800、2:3，固定 Hero / 诊断区 / A-B-C / 路线 / KPI / Gate / 下一步 / Footer 布局。
- 文字和图片必须从同一份 Schema 生成，禁止图片再次独立分析。
- 生成式图片仅作为无法程序化渲染时的 fallback。
- 新增 `schema/jn-decision-schema.json` 与 `renderer/README.md`。

## v2.4

- 将参考图视觉固化为 `JN VISUAL DESIGN SYSTEM`。
- 新增颜色、栅格、Hero、卡片、A/B/C、时间轴、KPI、Gate、Footer 等跨 Agent 视觉规范。

## v2.3.1

- 明确完整输出必须先完整文字版，再紧接一张路线图。
- 路线图不替代文字答案。

## v2.3

- 品牌统一为 **企业价值引擎**。
- 新增回答后自动生成路线图。
- 移除默认 PDF 输出。

## v2.2

- 新增 `JN Decision Dashboard`。

## v2.1

- 新增 `SCOPE_ROUTER`、`EXECUTIVE_COMPRESSION`、`DIVISIBILITY_CHECK`。

## v2.0

- 升级为 `DEFINE → MECHANISM → DESIGN → DECIDE` 四层思考架构。
