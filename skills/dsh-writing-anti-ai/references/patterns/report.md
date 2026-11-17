# Report-Specific AI Patterns (大报告/技术报告)

Government and technical reports in Chinese have distinct AI-writing fingerprints beyond the universal patterns. This file covers patterns specific to this genre.

Load this file when the text is: a government report, technical report, feasibility study, project summary, or any formal institutional document in Chinese.

---

## 🔴 Must-Fix

### R1. Baidu-Baike Opening (百度百科式开头)

**Detect**: Opening paragraph that follows this template:
> [地名]位于[省名][方位]，[方位接壤列表]，是……的重要[节点/枢纽/组成部分]和[荣誉称号]。

**Why it's AI**: LLMs default to encyclopedia-entry format. A chapter in a technical report should not start like a Baidu Baike article.

**Action**: Cut to what the chapter is about. Move geographic background to a footnote or a short clause, not the opening paragraph.

**Before**:
> 某市位于某省西南部，东邻甲市和乙市，南接丙市并濒临南海，西连丁市，北靠戊县，是连接粤西与珠三角的重要节点和全国著名侨乡。

**After** (for a technical report chapter):
> 某市辖1街道10镇，面积约1700 km²。全市以丘陵山地为主，平原分布于主要河流流域，属南亚热带季风气候，年均温约24°C，年降水约2300 mm。

(Note: cut location boilerplate, keep only what the chapter needs.)

---

### R2. Policy Slogan Clusters (政策口号集群)

**Detect**: Clusters of 4-character policy phrases, especially in purpose statements:
- 严守耕地保护红线
- 全面推进乡村振兴
- 促进农业高质量发展
- 保障粮食安全
- 加快推进农业农村现代化
- 坚持……发展理念
- 贯彻……战略部署

**Why it's AI**: These are memorized templates from government documents. Their presence in a technical report signals that the model is regurgitating training data rather than writing about the specific project.

**Action**: Translate each slogan into a factual description of what the project actually does.

**Before**:
> 为严守耕地保护红线、优化农业生产布局、保障粮食安全、促进农业高质量发展与全面推进乡村振兴提供科学依据。

**After**:
> 为耕地保护、农业生产布局优化与粮食安全保障提供科学依据。

(Rule of thumb: if the slogan appears verbatim in central government documents, it probably doesn't belong in a local technical report.)

---

### R3. Bureaucratic Filler Verbs (官腔动词)

**Detect**: 统筹, 协同, 联动, 融合, 一体化, 系统推进, 全面部署, 周密安排, 精心组织

Also: 核心 (核心载体/核心区域/核心对象), 主导 (主导因素/主导驱动力), 根本 (根本原因/根本成因), 关键 (关键机制/关键指标) — these causal superlatives are overused as fillers. Use them once per document at most for the single most important factor; otherwise delete or downgrade to 主要.

**Action**: Delete or replace with the specific action taken.

**Before**: 由市政府分管领导任组长的市专项工作领导小组及办公室负责统筹协调。
**After**: 由市政府分管领导任组长的市专项工作领导小组及办公室负责协调。

("统筹协调" → "协调" — the "统筹" adds nothing.)

---

### R4. 了-Stacking (了字堆砌)

**Detect**: Three or more consecutive sentences ending with 了 + verb completion pattern (完成了/实现了/形成了/建立了/确保了/达到了/促进了/推动了).

**Why it's AI**: AI Chinese defaults to 了 as a universal completion marker. Human writing varies aspect more naturally.

**Action**: Remove unnecessary 了. Alternate structures (是…的, noun phrases, ongoing state descriptions).

**Before**:
> 本次调查完成了500个样点调查。获取了丰富的立地条件信息。建立了完善的质控体系。确保了数据的准确性。

**After**:
> 本次调查共完成样点500个，获取立地条件与土壤利用信息[具体项]。质控体系覆盖外业采样到内业检测全过程。数据异常比例约0.03%。

---

### R5. Formulaic Opening Paragraphs (八股式开头)

**Detect**: Paragraphs that start with:
- 根据/依据/遵照……的要求/部署/精神
- 在……的正确领导下
- 按照……的总体部署
- 为贯彻落实…… 

**Action**: Delete the framing. Start with what was done.

**Before**: 某市第三次全国土壤普查遵循国家、省、市的统一部署和技术规范，由市、镇两级协同推进各环节工作。具体程序与做法如下：

**After**: 普查工作分为方案编制、外业调查采样、内业测试化验、数据审核与成果汇总四个阶段。质量控制覆盖全过程。

---

## 🟡 Should-Fix

### R6. Data + Empty Summary (数据后跟空洞总结)

**Detect**: A sentence with specific numbers, followed by a vague summary sentence. A particularly common variant is **反映了……的……** (reflects the XYZ of...):
- 反映了耕作培肥对……的提升作用
- 反映了深耕改土……的成效
- 反映了本市……的多样性

**Action**: Delete the summary sentence. The numbers speak for themselves. For 反映了 closers, either delete entirely or convert to a factual statement without 反映了.

**Before**:
> 完成表层样点300个、剖面样点30个。所有样点覆盖全市各镇（街道）及主要林场，其空间分布充分考虑各区域土地面积与类型差异，在农业主产区布设较为密集，确保了普查样本的代表性与科学性。

> 水田有机质最高（23.69 g/kg），旱地最低（17.60 g/kg），反映了耕作培肥对水田有机质的提升作用和园地单一栽培模式下的消耗效应。

**After**:
> 完成表层样点300个、剖面样点30个，覆盖全市各镇（街道）及主要林场。A镇、B镇、C街道等农业主产区样点密度较高。

> 水田有机质最高（23.69 g/kg），旱地最低（17.60 g/kg）。耕作培肥提升了水田有机质，园地单一栽培则消耗有机质。

(删除"确保了……代表性与科学性"这句空话，用具体事实替代。删"反映了"或转为事实陈述。)

---

### R7. Standardized Process Boasting (流程标准化自夸)

**Detect**: Descriptions of processes that use 标准化, 规范化, 系统化, 科学化 as modifiers for every step.

**Action**: Describe the process. Delete the modifiers. If the process follows a national standard, say which standard — once.

**Before**: 标准化流程包括规范的风干、研磨、过筛与分装。
**After**: 样品经风干、研磨、过筛后分装，执行国家标准技术规范。

---

### R10. 突出 Overuse (突出滥用)

**Detect**: 突出 used as a vague intensifier more than 3-5 times per document. Common patterns:
- 问题突出 / 矛盾突出 / 特征突出 / 差异突出
- 最为突出 / 日趋突出 / 更为突出

**Why it's a problem**: 突出 is the single most common AI filler word in Chinese technical reports. In this genre, it appears 10-20+ times per document, almost always as a substitute for specific description. By the 5th occurrence, the reader registers it as verbal tic.

**Action**: First pass: replace with 明显 (less severe). Second pass: delete entirely where the context already implies prominence. For 问题突出 → state what the problem causes, not that it's "prominent."

**Before**:
> 林地酸化问题突出，酸性林地面积155.54万亩。
> 钾素不足问题凸显，4级和5级合计占比超过70%。

**After**:
> 林地酸化面积155.54万亩。
> 钾素不足：4级和5级合计占比超过70%。

(The problems are evident from the numbers. No need to label them 突出.)

---

### R12. Section-Head Slogans (二级/三级标题口号化)

**Detect**: Section headings that are policy slogan pairs separated by commas or spaces:
- 优化农业产业布局，促进乡村产业发展
- 推进土壤资源科学利用，提升农产品质量与资源利用效益
- 培肥改良土壤，提升耕地质量
- 加强信息化建设，推进数字化管理
- 做强地理标志产业集群
- 优化全域农业空间格局

**Why it's AI**: These headings follow a formulaic "verb+object, verb+object" or "做强XX" template. Human-written report headings are shorter and descriptive (培肥改良土壤 → 改良建议 / 信息化建设). The comma-separated pair pattern is a memorized government document template.

**Action**: Replace with short noun-phrase headings that describe the section's content. Delete the second clause entirely or merge into a single 3-5 character noun.

**Before → After**:
| Original | Fixed |
|----------|-------|
| 培肥改良土壤，提升耕地质量 | 培肥改良土壤 |
| 优化农业产业布局，促进乡村产业发展 | 产业布局建议 |
| 推进土壤资源科学利用，提升农产品质量与资源利用效益 | 土壤资源利用建议 |
| 加强信息化建设，推进数字化管理 | 信息化建议 |
| 优化全域农业空间格局 | (delete heading, merge into paragraph) |
| 做强地理标志产业集群 | (delete heading, keep content as sub-bullet) |

(Rule of thumb: if the heading has a comma, it's probably a slogan pair. Cut to the first 2-4 characters.)

---

### R13. Condensed Parallel Slogan Framework (缩写式排比框架)

**Detect**: A set of 3+ items sharing a common single-character prefix, typically arranged as standalone sub-headings or bolded items:
- 因土适种 / 因土施肥 / 因制养地 / 因水管护 / 因品提质
- 因土适种 / 因土施肥 / 因土养地 / 因土用水 / 因土提质
- 保优先 / 提中 / 退劣

**Why it's AI**: LLMs favor "单字+双字" three-or-more parallelism because it looks structured. Human writing might use one or two such items but rarely sustains 4-5 across a section. The shared prefix (因土) is a dead giveaway that the model generated the set from a template rather than writing from content.

**Action**: Collapse the framework. Merge all items into a single plain paragraph. Delete the bolded/labeled prefixes. Each item becomes one clause connected by punctuation.

**Before**:
> 因土适种：在A区种植B作物。
> 因土施肥：在A区提高钾肥比例。
> 因土养地：在A区推广轮作。

**After**:
> 种植布局上，在A区种植B作物。施肥管理上，在A区提高钾肥比例。耕作制度上，在A区推广轮作。

(Or just write a flowing paragraph without labels at all.)

---

### R14. 方针 as Closing Marker (方针收尾)

**Detect**: Sentences ending with 方针, especially in recommendations sections:
- 提出……的利用方针
- 坚持……的发展方针
- 遵循……的指导方针

**Why it's AI**: "方针" is the go-to closing noun for AI-generated recommendation paragraphs. It signals "I need to end this section with a generic wrap-up." Human-written recommendations rarely use this word.

**Action**: Delete "方针" or replace the entire closing sentence with the specific action item. If "提出...方针" is the section's topic sentence, replace with a plain statement ("建议..." or "分以下几方面").

**Before**:
> 提出"因土适种、因土施肥、因制养地、因水管护、因品提质"的利用方针。

**After**:
> 提出分类利用建议。
> (Then list items as plain text without the "方针" label.)

---

### R11. Degree Adverb Stacking in Reports (程度副词堆砌)

**Detect**: Clusters of degree adverbs used as generic emphasis without data backing, common in report summaries and recommendations:
- 极度 + adjective (极度匮乏/极度稀缺)
- 急剧 + verb (急剧下降/急剧上升)
- 严重 + adjective (严重偏低/严重不足) — only keep if there's a defined threshold for "严重" in the grading system
- 较为/相对 + adjective (较为复杂/相对较好) — hedges that weaken the statement

**Action**: Delete the degree adverb. The data or grading system already conveys intensity.

**Before**:
> 耕层厚度严重偏薄（3级占97.73%）
> 速效钾极度匮乏（5级占65.73%）

**After**:
> 耕层厚度偏薄（3级占97.73%）
> 速效钾含量低（5级占65.73%）

(The grade classification already communicates severity. 严重/极度 adds nothing.)

---

## ⚪ Consider

### R8. Administrative Hierarchy Lists (行政层级罗列)

**Detect**: Long lists of government units involved (国家、省、市、县、镇……).

**Action**: Condense. The reader doesn't need the full org chart.

### R9. Report Inventory Sections (成果清单)

**Detect**: Bullet-point lists of outputs at the end of chapters (数据成果、图件成果、文字成果…).

**Action**: These are often fine as-is (they're reference material). But check for AI padding within each item description.

---

## Integration Note

When processing a report chapter, apply universal patterns first (Pass 1-2), then load this file for Pass 3 (document-level restructuring). 

**Priority order for a typical long report (1000+ lines):**
1. **R1 (opening)** — fix once, sets tone for entire document
2. **R2 (slogan clusters)** — scan purpose statements in chapter intro and closing
3. **R12 (section-head slogans)** — scan all `===`/`====` headings for comma-slogans; this alone can remove 10-20 slogan headings from a multi-chapter report
4. **R13 (condensed parallel frameworks)** — scan for 因土/X适Y/X化 patterns in recommendation sections
5. **R14 (方针 closers)** — scan the last paragraph of each section
6. **R10 (突出 overuse)** — the highest-frequency fix, 15-20 instances per chapter

**Watch for compound patterns**: a single paragraph can contain R2 (slogan cluster) + R14 (方针 closer) + R13 (parallel items inside). Fix the framing first (R2/R5), then the heading (R12), then collapse parallelism (R13), then delete the 方针 closer (R14).

**Typical distribution in a 400-line report chapter**: R10 (15-20) > R6 (5-8) > R3/R12 (3-5 each) > R1/R2/R5/R13/R14 (0-2 each). R12 is disproportionately impactful because each fix removes an entire heading rather than a single word.
