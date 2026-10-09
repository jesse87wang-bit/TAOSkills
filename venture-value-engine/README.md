# Venture Value Engine v3.0.1

创业投资价值决策 Agent Skill：**V1完整初筛 + V2专业尽调/估值/交易分析 + V3多项目决策档案/投后跟踪**。

**重要边界**：它是决策辅助工具，不是经纪、保本投资顾问、持牌法律/审计服务，也不能保证投后收益。V3是**离线、按需运行**的本地JSON项目管理，不会自行跟踪市场、发送通知、建立云数据库或执行投资交易。

## 核心功能

| 能力 | 版本 | 交付/调用 |
|---|---|---|
| 创业项目完整分析、价值链、机会与风险、15个创始人问题、三轮验证 | V1.2保留 | `SKILL.md`, `assets/full-analysis-and-diligence-template.md` |
| 证据等级审计、跨材料冲突 | V2 | `scripts/diligence_audit.py` |
| 财务现金跑道、毛利率、CAC回收、真实输入可比估值、VC Method | V2 | `scripts/valuation_workbench.py` |
| 普通股多轮融资、期权池投前增发、单类优先清算示例 | V2 | `scripts/cap_table_model.py` |
| Term Sheet风险排查与数据缺口 | V2 | `scripts/term_review.py` |
| 结构化尽调一键汇总 | V2 | `scripts/v2_pipeline.py` |
| 多项目组合、决策历史、证据变化、估值更新（带来源）、历史时间点快照、期间差异、现金记录、里程碑比较 | V3 | `scripts/portfolio_tracker.py` |
| 详细投委会备忘录、组合复盘模板 | V2/V3 | `assets/v2-investment-committee-template.md`, `assets/v3-portfolio-quarterly-review-template.md` |

## 安装

这是兼容开放 [Agent Skills 目录规范](https://agentskills.io/specification) 的目录。解压ZIP，保留整个 `venture-value-engine/`，放到宿主客户端支持的 skills 目录。Codex 具体路径取决于安装与配置；其他Agent/WorkBuddy是否能直接运行Python脚本取决于它们的宿主能力。如果只能读取文本，则仍可运用分析规则，但脚本结果必须由可运行环境单独计算。

本Skill不需要Python第三方依赖，推荐Python 3.10以上；本包实测Python 3.13。

## 使用自然语言

- 一键全量报告：先上传企业背景材料、BP、聊天记录、财务表或技术演示，再输入 `用 Venture Value Engine 分析这家企业`。
- `用Venture Value Engine完整分析这家创业公司，给15项问题及验证方式。`
- `进入V2，审计客户、收入、成本，并分析融资估值、期权池和条款。`
- `按V3给我做创业项目跟踪档案，每轮补充新资料后对比新增证据和决策变化。`
- `比较TokenFly与另外两个创业项目，列出证据缺口、价格条件、风险和下一里程碑。`

## V2立即运行：TokenFly结构化案例

```bash
cd venture-value-engine
python scripts/v2_pipeline.py --input assets/v2-tokenfly-pipeline-input.json --output-dir validation/tokenfly_2026-10-09/v2-output
```

输出：`v2_bundle.json`、`v2_analysis.md`。因为没有TokenFly经营数据、股权表及融资条款，**不会**给虚构估值或持股比例。`assets/v2-valuation-example-SYNTHETIC.json`、`assets/v2-cap-table-example-SYNTHETIC.json`、`assets/v2-terms-example-SYNTHETIC.json`都是真实计算器的**纯虚构测试参数**，不是TokenFly的数据。

## V3立即运行：项目比较与里程碑

```bash
python scripts/portfolio_tracker.py validate --file validation/v3_demo_portfolio.json
python scripts/portfolio_tracker.py dashboard --file validation/v3_demo_portfolio.json --as-of 2026-10-09
python scripts/portfolio_tracker.py compare --file validation/v3_demo_portfolio.json --ids tokenfly demo-saas demo-consumer --as-of 2026-11-20
python scripts/portfolio_tracker.py diff --file validation/v3_demo_portfolio.json --from-date 2026-10-09 --to-date 2026-11-20
python scripts/portfolio_tracker.py timeline --file validation/v3_demo_portfolio.json --id tokenfly
```

已提供演示档案，TokenFly记录仅反映此前的初筛材料；另两个项目完全虚构。里程碑到期时间是**演示规划**，不代表TokenFly承诺过这些期限。要跟踪真实项目，请在私有目录中`init`一个新的JSON文件，参考`references/v3-monitoring.md`与`assets/v3-event-examples.json`的格式新增事件。估值记录可参考纯虚构的`assets/v3-valuation-event-SYNTHETIC.json`，程序要求独立验证后才能标记为已核验，不会混淆企业价值与股权价值。

## 专业参考与实现限制

- `references/v2-deep-diligence.md`：数据室、行业差异、工作流和问卷/验证。
- `references/v2-valuation-and-terms.md`：价格、普通股、优先清算示例和复杂证券禁区。
- `references/v3-monitoring.md`：事件API、里程碑判定、验证和保密。
- `references/evidence-protocol.md`、`references/stage-sector.md`：原有底层证据标准和行业框架。
- `assets/v2-investment-committee-template.md`和`assets/v3-portfolio-quarterly-review-template.md`：可直接复制的分析模板。
- `validation/tokenfly_2026-10-09/v2-output/`：TokenFly的V2结构化分析（只覆盖输入证据）。
- `validation/V2V3_验证与边界.md`：测试结果和未支持范围。

执行单元测试：

```bash
python -m unittest discover -s tests -v
```

不能从演示案例推出投资回报预测准确率。本Skill的财务模型只进行确定性计算、证据审查程序只检查输入规范、不承担发现全部造假责任。真实尽调时还需技术专家、律师及财务人员独立核查。
