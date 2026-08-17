# dsh-writing-anti-ai

DeepSeek Harness (DSH) 原生「去 AI 味」技能（Anti-AI / NTAI）。

把机器生成的文字改成更像真人写的：删填充词、去黑话、去掉价值判断形容词、拆机械枚举、处理箭头符号链等。支持中英文，覆盖报告、学术论文、叙事等多种文体。

## 为什么加 DSH 前缀

本技能是从 Claude/`.agents` 生态迁入 DSH 的版本。为避免两套生态同名冲突（若你的 GitHub 上还有一份 `claude-writing-anti-ai`），DSH 版统一用 `dsh-` 前缀区分。

## 利用的 DSH 特性

- **按长度自适应**：短文单通、中篇幅分块、长文自动触发。
- **长文用 DSH `workflow` + `subagent` 扇出**：`scripts/workflow_deanti.js` 把长文档按段切开，每块交给独立子代理在自己的上下文里处理（有界上下文，对抗注意力衰减），并用 `opts.schema` 强制结构化输出。
- **机器可校验闭环**：`validation` 检查「没有丢块」「ledger 每行都有处置」「标 `fixed` 的原文必须真的从正文消失、标 `kept` 的必须还在」，防止「记了改但正文没改」。
- **语义三审**（不是硬编码白名单）：专有名词/固定搭配（景观格局、分布格局、闭环控制…）由模型看上下文判断保留，不用查字典穷举；拿不准交人工。

## 安装（DSH）

把 `skills/dsh-writing-anti-ai` 放到 DSH 用户技能根目录：

```
C:\Users\<you>\.dsh\skills\dsh-writing-anti-ai\
```

技能目录热刷新，无需重启。

## 结构

```
skills/dsh-writing-anti-ai/
  SKILL.md                      # 主指令（含分块/记账/语义三审/DSH workflow 编排）
  references/
    protocol.md                 # 执行协议：分块、记账、硬校验、失败重跑
    patterns_data.json          # 词表数据（加词不改代码）
    allowlist.json              # 常见专有名词提示（仅提示，非权威跳过）
    replacements.md             # 逐词替换表
    principles.md               # 每个模式为何是 AI 味
    patterns/universal.md       # 通用模式清单
    patterns/report.md          # 政府/技术报告
    patterns/academic.md        # 学术论文
    patterns-english.md         # 英文 AI 模式
    wikipedia-source.md         # 来源
  scripts/
    detect.py                   # 扫描器（--triage / --hits / --residual / --chunks）
    workflow_deanti.js          # DSH workflow 编排模板（长文分块扇出）
  examples/
    chinese.md                  # 中文改写示例
    english.md                  # 英文改写示例
```
