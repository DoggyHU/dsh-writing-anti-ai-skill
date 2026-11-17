# Academic Paper AI Patterns (学术论文)

Patterns specific to academic writing (Chinese and English). This file is a living document — extend it as you encounter new patterns.

Load this file when the text is: a research paper, thesis, conference submission, journal article, or grant proposal.

---

## 🔴 Must-Fix

### A1. "填补空白" Claims (Gap-Filling Template)

**Detect**: 填补了……空白, 目前尚无……研究, 现有研究尚未关注……, 国内外未见报道, To the best of our knowledge, this is the first...

**Why it's AI**: AI models default to claiming novelty through gap-filling rhetoric. Real papers state their contribution without declaring a vacuum.

**Action**: State what the work does. Let readers judge novelty.

**Before**: 目前尚无研究系统分析某区域土壤酸化空间分布特征，本研究填补了这一空白。
**After**: 本研究基于500个样点的pH测定数据，分析该区域土壤酸化空间分布特征。

---

### A2. Citation Hallucination Patterns (引用幻觉)

**Detect**: 研究表明, 大量研究证实, 众多学者指出, 学术界普遍认为 (without specific citations); or 张三等人认为 followed by content that doesn't match any real paper by 张三.

**Action**: Cite specific papers with author-year. If the claim can't be traced to a verifiable source, delete or rephrase as the authors' own observation.

---

### A3. Formulaic "Challenges" Sections (八股式"挑战"段落)

**Detect**: Paragraph that follows: "Despite X, [topic] faces several challenges. First, ... Second, ... Third, ..."

**Action**: Integrate challenges into the analysis. Don't segregate them into a dedicated boilerplate paragraph.

---

## 🟡 Should-Fix

### A4. Overly Smooth Transitions (过度平滑过渡)

**Detect**: However, Moreover, Furthermore, Additionally, In addition, Nevertheless, Consequently at the start of every paragraph.

**Action**: Reduce by 70%. Let paragraphs connect through content, not transition words.

---

### A5. Hedging Stacking (堆叠式模糊限制)

**Detect**: may potentially, could possibly, might perhaps, 可能在一定程度上, 或许可以认为

**Action**: Pick one hedging word. One is enough.

**Before**: 这可能在一定程度上可以认为是由土壤母质差异导致的。
**After**: 这可能由土壤母质差异导致。

---

### A6. Abstract Inflation (摘要膨胀)

**Detect**: Abstracts that use promotional language: 首次, 创新性地, 突破性地, 具有重要意义, 为……提供参考

**Action**: Remove promotional adjectives. State findings directly.

---

## ⚪ Consider

### A7. Paper Structure Templates (论文结构模板化)

**Detect**: Introduction → Related Work → Method → Experiment → Conclusion as rigid, unmodified sections.

**Action**: Consider if the paper's argument benefits from a different organization. But don't force it — standard structure exists for a reason.

---

## Integration Note

Academic writing has the tightest tolerance for AI patterns because reviewers are increasingly trained to spot them. Prioritize A1-A3 (the most detectable academic AI patterns) before addressing style issues.
