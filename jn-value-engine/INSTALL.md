# jn-value-engine v3.6.1 安装与使用

> 企业价值引擎

## 推荐安装原则

**安装包中的 `SKILL.md` 是唯一执行真源。**

不要把仓库里的历史协议文件与 v3.6.1 并列成多份最高优先级指令，否则容易重新引入版本冲突或输出漂移。

推荐 clean bundle 结构：

```text
jn-value-engine/
├── SKILL.md
├── manifest.json
└── tests/
    ├── ACCEPTANCE.md
    └── validate_output.py
```

## 1. 在 ChatGPT 中安装

OpenAI Skills 的标准形态是一个包含 `SKILL.md` 和支持资源的可复用工作流。官方流程支持审阅并安装 Skill；安装后可自动使用相关 Skill，也可显式 @ 调用。

推荐方式：

1. 下载 `jn-value-engine-v3.6.1.zip` clean bundle；
2. 在支持 Skills 安装的 ChatGPT 工作区中上传这个 zip；
3. 审阅 Skill 内容；
4. 选择 **Install**；
5. 安装完成后，用下面的回归案例测试。

不要把整个 `TAOSkills/jn-value-engine` 历史目录原样压成安装包；v3.6.1 clean bundle 应只包含当前唯一执行真源和必要支持文件，避免旧执行协议造成冲突。

## 2. 在 Codex / 其他支持 Agent Skills 的环境中

把 clean bundle 解压后的整个 `jn-value-engine/` 目录放到该环境可识别的 Skill/workspace 位置，并以 `SKILL.md` 为入口。

关键要求：

```text
jn-value-engine/SKILL.md = Single Source of Truth
```

若环境会自动扫描支持资源，可以加载 `manifest.json` 和 `tests/`；这些文件用于状态机声明、验收和回归验证，不得反向覆盖 `SKILL.md`。

如果环境没有原生 Skill 安装功能，也可以把整个 clean bundle 放进 workspace，并明确要求 Agent 在每次调用前读取 `jn-value-engine/SKILL.md`。

## 3. 安装后必须做回归测试

测试输入：

```text
用 jn-value-engine 回答：
新能源设备公司订单和客户都不错，但下游回款太慢，导致拖欠供应商500多万元、资金链断了。应该继续融资还是缩业务？
```

合格执行顺序必须是：

```text
TRIGGERED
→ ANALYZED
→ TEXT_RENDERED
→ TEXT_VALIDATED
→ IMAGE_ALLOWED
→ IMAGE_RENDERED
→ COMPLETE
```

用户可见结果必须严格为：

1. 先出现标题 `企业价值引擎｜<案例主题>`；
2. 完整输出 01–09；
3. 04 至少包含 A/B/C；
4. 06 是分阶段路线图；
5. 08 恰好 4 个 Gate；
6. 09 同时包含下一步行动与“什么会让我改变判断”；
7. 直到第 09 最后一个字符输出完成前，不得调用图片生成；
8. TEXT VALIDATION 通过后，才生成一张单独的 TF 企业价值路线图；
9. 图片不得改变文字阶段结论，也不得新增未经验证的数据。
10. 图片顶部与 Footer 的视觉品牌只使用 `TF`、`TF 企业价值引擎`，不得出现 `JN`；右侧 Skill 署名必须保留 `jn-value-engine`，不得改为 `tf-value-engine`。

只要发生以下任一情况，都判安装/执行失败：

- 先出图；
- 只有图；
- 只有普通自由分析；
- 少模块或改模块名；
- A/B 二选一而无第三方案；
- 4 Gate 缺失；
- 09 没有反证条件；
- 图片代替九段文字；
- 图片阶段偷偷加入新的数字或改变结论。

## 4. 本地验证器

对一份已保存的文字输出运行：

```bash
python tests/validate_output.py output.md
```

返回：

```text
PASS
```

才代表结构性文字验收通过。

注意：这个 Python validator 是**辅助的确定性检查器**。在聊天产品中，真正的 Image Gate 仍由 `SKILL.md` 的执行协议约束；validator 不能单独阻止某个宿主产品调用图片工具，所以宿主必须正确执行 `SKILL.md`。

## 5. 版本管理

GitHub 是源码和版本历史的真源；安装环境里使用的是某个具体 Skill 版本。

推荐流程：

```text
修改 GitHub
→ 跑回归测试
→ 更新版本号
→ 重新生成 clean bundle
→ 在 ChatGPT / Codex 中更新或重新安装
```

不要依赖聊天 Memory 来“同步” Skill 版本。

## 6. 使用

安装后直接调用：

```text
用 jn-value-engine 回答：<你的企业决策问题>
```

或者在支持 @Skill 的产品中显式选择 / @mention `jn-value-engine`。
