# Universal AI Patterns (跨文体通用)

Patterns in this file apply to ALL writing genres. Organized by signal level.

---

## Must-Fix

### U1. Filler Phrases (填充短语)

**Detect**: 值得注意的是, 需要强调的是, 需要指出的是, 众所周知, 不可否认, 毋庸置疑, 换句话说, 也就是说, 总体而言, 从某种程度上说, 基于……的事实, 在……的背景下

**Action**: Delete. The sentence that follows is always stronger without the filler.

**Before**: 值得注意的是，该区域土壤资源分布不均。
**After**: 该区域土壤资源分布不均。

---

### U2. AI Vocabulary — "依托" (tuō)

**Detect**: 依托 (as verb meaning "rely on / depend on")

**Action**: Replace with 通过, 基于, or 利用, depending on context.

**Before**: 数据采集依托统一的信息管理平台。
**After**: 数据采集通过统一的信息管理平台进行。

---

### U3. AI Vocabulary — Buzzwords (黑话)

**Detect**: 赋能, 闭环, 抓手, 格局, 夯实, 扎实推进, 深入开展, 持续优化, 着力, 大力, 深化, 强化, 加大……力度

**Action**: Replace with plain language. Describe what actually happens.

| AI | → | Natural |
|----|---|---------|
| 赋能产业 | → | 支持产业发展 |
| 闭环处理 | → | 完成处理 |
| 夯实基础 | → | (delete or be specific) |
| 扎实推进 | → | 推进 |
| 深入开展 | → | 开展 |

---

### U4. Value-Judgment Adjectives (价值判断形容词)

**Detect**: 重要的, 著名的, 优良的, 完善的, 严格的, 充分的, 深刻的, 丰富的, 重大的, 显著的, 突出的, 关键的 (when used as generic positive modifiers, not as technical terms)

**Action**: Delete the adjective. If removing it changes the factual claim, replace with a specific, measurable description.

**Before**: 建立了完善的内部质控体系。
**After**: 建立了内部质控体系。

**Before**: 该县是全省重要的粮食产区。
**After**: 该县是全省粮食产区之一。 (or state annual output instead)

---

### U5. Vague Attributions (模糊归因)

**Detect**: 专家认为, 研究表明, 据悉, 据了解, 数据显示, 业内人士指出, 相关人士表示

**Action**: Cite a specific source, or delete the attribution entirely and state as fact (if it is an established fact), or delete the sentence (if it's padding).

**Before**: 专家认为该模式有效提升了产量。
**After**: (either name the expert with affiliation, or delete the sentence, or write: 该模式下产量提升了X%。)

---

### U6. Self-Praising Summary (自我表扬式总结)

**Detect**: Sentence at paragraph/section end that uses: 为……奠定了坚实基础, 有效保障了……, 充分体现了……, 标志着……, 具有重要的……意义, 对……产生深远影响

**Action**: Delete the entire sentence. It adds no information.

**Before**: 通过严密的组织管理和标准化的操作流程，有效保障了数据的科学性、准确性和可靠性，为全面摸清资源家底奠定了坚实基础。
**After**: (deleted)

---

### U7. 确保/保障…性 Endings

**Detect**: Sentence pattern: 确保/保障了 + [abstract noun] + 的 + [-性 abstract noun]

**Action**: Replace with a factual statement, or delete.

**Before**: 确保了调查样本的代表性与科学性。
**After**: 样本覆盖各主要土地利用类型。 (state the fact, not the claim)

---

### U8. AI Symbol Chains (AI符号链)

**Detect**: Arrow symbols (→, ⇒, ➡, ➤, ➜) used to chain 3+ items in a flowchart-like sequence within prose text. Common patterns include A→B→C, A→B→C→D, or 步骤→步骤→步骤.

**Why it's AI**: LLMs compress processes into visual arrow chains instead of writing natural sentences. A human writer uses commas, 到, 再到, or plain verbs. The arrow chain reads like a diagram squeezed into prose — no human writes "我从家→地铁站→公司".

**Action**: Replace with natural Chinese listing. Use commas、顿号、到/再到, or restructure into a full sentence with verbs.

**Before**: 设计流程包括总平→建模→渲染→分析图→展板。
**After**: 设计流程从总平、建模、渲染，到分析图和展板。

**Before**: 数据采集→预处理→建模→验证→输出。
**After**: 数据经采集、预处理后建模，验证后输出。

**Before**: 入口→大厅→走廊→会议室。
**After**: 从入口经大厅和走廊，到达会议室。

**Note**: A single → between two items (A→B) may be acceptable in technical contexts (e.g., file format conversion, data pipeline labels). Chains of 3+ arrows are always must-fix.

---

## Should-Fix

### U9. Mechanical Enumeration (机械枚举)

**Detect**: Consecutive sentences or paragraphs starting with 首先/第一, 其次/第二, 再次/第三, 第四, 最后/第五 in sequence.

**Action**: Break the sequence. Keep substantive content, remove numbering words. Vary paragraph structure: expand one step into a full paragraph, collapse others into shorter descriptions.

**Before**:
> 首先，是方案编制阶段。…… 其次，是外业调查采样阶段。…… 第三，进入内业测试化验阶段。…… 第四，是数据审核与成果汇总阶段。…… 最后，贯穿全过程的是严格的质量控制。

**After**: Reorganize so steps are not numbered. The quality control step can be integrated into earlier sections. Some steps get paragraphs, others get sentences.

---

### U10. Double Modifiers (双重修饰)

**Detect**: Noun phrases with A与B or A和B where A and B serve the same function (synonyms or near-synonyms).

**Action**: Keep the more specific or measurable term. Delete the other.

| Before | After |
|--------|-------|
| 验证与确认 | 验证 (or 确认, depending on actual process) |
| 精密度与准确度 | 精密度 (if measured by RSD) or 准确度 (if measured by recovery) |
| 科学性与可靠性 | (pick one, or delete both and state the evidence) |
| 线上实时审核与全过程追溯 | 在线审核与追溯 |

---

### U11. Intensifier Stacking (程度词堆叠)

**Detect**: 非常, 极其, 大幅, 显著, 持续, 不断, 明显 (when they add no measurable information)

**Action**: Remove. If the intensity matters, use a number.

**Before**: 检测数据量大幅增加，数据质量显著提升。
**After**: 检测数据量从X增加到Y。数据异常比例从Z%降至W%。

---

### U12. Em-Dash Overuse (破折号滥用)

**Detect**: More than 2 em-dashes (—) per 1000 characters.

**Action**: Replace with comma, period, or restructure sentence.

---

### U13. Colon Overuse (冒号滥用)

**Detect**: More than 1 colon per 100 characters.

**Action**: Restructure. Replace "X：Y" with "X是Y" or break into separate sentences.

---

## Consider

### U14. Rule of Three (三段式)

**Detect**: Lists of exactly three items or three parallel clauses in one sentence.

**Action**: Consider if all three are needed. Prefer two or four — odd numbers that aren't three feel more human. But don't force it. If three is natural, keep three.

---

### U15. Elegant Variation (同义词刻意替换)

**Detect**: Different words used to refer to the same thing within a paragraph (to avoid repetition).

**Action**: Use the same word. Consistency > variety.

**Before**: 主人公面临许多挑战。主要角色必须克服障碍。中心人物最终获得胜利。
**After**: 主人公面临许多挑战，但最终获得胜利。

---

### U16. Echo Conclusion (结论回音壁)

**Detect**: The conclusion paragraph restates the introduction without adding new information.

**Action**: Ensure each section's ending adds something the beginning didn't. If the conclusion is just a rephrase of the intro, delete it or merge the new information into the body.
