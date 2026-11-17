---
name: dsh-writing-anti-ai
description: This skill should be used when the user asks to "remove AI writing patterns", "去AI味", "除AI痕迹", "humanize this text", "make this sound more natural", "remove AI-generated traces", "fix robotic writing", or needs to eliminate AI writing patterns from prose. Supports Chinese and English across multiple genres including reports, academic papers, and narrative. Uses a closed-loop protocol (sizing, per-instance ledger, re-scan of the original, hard verification) so fixes do not get silently dropped on long documents. Based on Wikipedia's "Signs of AI writing" guide.
version: 2.1.0
author: gaoruizhang
license: MIT
tags: [Writing, AI, Anti-AI, Humanizer, NTAI]
---

# Writing Anti-AI (NTAI)

Remove AI-generated writing patterns. Turn machine prose into human prose.

## Signal Levels

Every pattern carries a signal level that determines how to handle it:

| Level | Tag | Rule |
|-------|-----|------|
| **Must-fix** | 🔴 | Remove on sight. No exceptions. |
| **Should-fix** | 🟡 | Remove unless genre explicitly requires it. |
| **Consider** | ⚪ | Flag. Decision depends on context. |

When uncertain: 🔴 is non-negotiable. 🟡 needs a reason to keep.

## Step 0. Size the job before editing

Estimate the target text size. Choose the strategy that matches. **Never attempt a full multi-pass edit of a long document in a single context** — attention decays across a long input and fixes silently get dropped. This is the single most common cause of "I only corrected 50 of 100."

| Size | Threshold | Strategy |
|------|-----------|----------|
| Short | up to ~600 chars | Single pass, then forced re-check of the original. |
| Medium | ~600–2,500 chars | Split into chunks; edit each chunk; re-check with a ledger. |
| Long | over ~2,500 chars or 40+ sentences | Fan out to subagents (Step 6) or manual chunking (Step 5). |

For Medium/Long, load `references/protocol.md` for the full execution protocol (chunking, ledger reconciliation, failure retry).

## Step 1. Scan (词汇层)

Flag every instance of:

- **Filler phrases** — consult `references/replacements.md` for the lookup table.
- **AI marker words** — 依托, 赋能, 闭环, 抓手, 格局, 夯实, 扎实推进, 深入开展, 持续优化, 显著, 大幅, plus the extended list in `references/patterns_data.json` (着力, 大力, 强化, 深化, 全面提升, 显著提升, 大幅增加, 不断完善, 充分发挥, 有机结合, 深度融合, 统筹协调, 协同推进, 系统部署, 周密安排, 精心组织).
- **Overused vague intensifiers** — 突出 (most common offender in reports, over 10+ instances per file is typical), 核心, 关键, 主导, 根本 (causal connectors used as filler).
- **Value-judgment adjectives** — 重要的, 著名的, 优良的, 完善的, 严格的, 充分的, 深刻的, 丰富的, 良好的, 优越的, 优异的, 独特的.
- **Intensifier stacking** — 非常, 极其, 极为, 极度, 急剧, 大幅, 持续, 不断, 严重 (when used as generic emphasis without data backing).
- **Vague attributions** — 专家认为, 研究表明, 据悉, 据了解, 数据显示 (without a specific source).
- **黑话 / 翻案腔** — two extra Must-fix families in `references/patterns_data.json` (`jargon_ban`, `fanan`), plus the semantic library in `references/lexicon.md`. 翻案腔 is judged by the *move*, not the words: 先造一个读者没有的误解，再推翻它抬价（"不是 X，而是 Y"、"看似 A，实则 B"）。Strip it to the plain judgment.
- **AI symbols** — four families, all delete-on-sight (any occurrence, not just 3+ arrow chains):
  - Arrow connectors — →, ⇒, ➡, ➤, ➜. Replace with 顿号、逗号, or 到/再到.
  - Status emoji — ✅ ❌ ⚠️ 🔴 🟠 🟡 🟢 ⭐. Replace with the Chinese word the mark stood for (符合 / 不符合 / 需注意).
  - Corner brackets — 「 」. Replace with “ ” (standard Chinese quotes, typeable on any pinyin IME).
  - Check marks — √ ✓ ✖ △. Same replacement as emoji. **Exception**: × is a multiplication sign in `3000元/㎡ × 面积` — judge by context, never blanket-replace.
  - Rationale: these render as tofu boxes in many government portals and cannot be typed on a standard pinyin IME, so a colleague cannot edit the file after you hand it over.

**Action**: 🔴 → replace or delete immediately. 🟡 → mark for the sentence pass. Record every hit in the ledger (Step 4).

For a token that might be a 专有名词 or fixed term (景观格局, 分布格局, 发展格局, 闭环控制…), do **not** auto-fix or auto-skip from a list. Decide by meaning using the surrounding context — see Step 4.5 (semantic triage). A hard-coded allowlist cannot cover every domain, so the judgment is semantic, not lookup.

## Step 2. Restructure (句法层)

Target structural patterns:

- **Mechanical enumeration** — sequences of 首先/其次/第三/第四/最后. Break the sequence: expand one step, collapse the others.
- **Double modifiers** — A与B pairs doing the same job (验证与确认, 精准度与准确度). Keep one.
- **确保/保障…性 endings** — Replace with a factual statement or delete.
- **Self-praising paragraph closers** — Delete the entire closing sentence.
- **Em-dash overuse** — >2 per 1000 characters. Replace with comma or period.
- **Heavy colon density** — >1.5 per 100 characters. Restructure.

Rewrite sentence structure and vary length. Every 200 characters must contain at least one sentence ≤12 characters.

## Step 3. Reorganize (语篇层)

Check document-level patterns:

- **Encyclopedia openings** — "XX位于…是…的重要…". Cut to what the reader needs.
- **Policy slogan clusters** — Replace with factual description.
- **Echo conclusions** — Conclusion must add new information, not restate the intro.
- **Uniform paragraph length** — Vary paragraph size by at least 2x within the document.
- **[Genre-specific]** — If genre is known, load the matching pattern file from `references/patterns/`.

Restructure paragraphs and sections for natural rhythm.

## Step 4. Maintain a ledger — this closes the loop

Never finish without a ledger. The ledger is what makes omissions visible. Produce a table with a row per detected instance:

| Type | Original | Fixed | Disposition |
|------|----------|-------|-------------|
| Must-fix: filler | 值得注意的是 | (deleted) | fixed |
| Must-fix: arrow chain | A→B→C | A、B 到 C | fixed |
| Consider: rule of three | …X、Y、Z… | — | kept (natural) |

- Every Must-fix token you find gets a row.
- Disposition is one of `fixed`, `kept (reason)`, `skipped (reason)`. Never leave it blank. A blank disposition is a missing accountability entry.
- At the end, re-scan the **ORIGINAL** text with fresh eyes, not your edited output. Compare the ledger against the original. Anything you missed the first time is exactly what attention decay hides — add it.
- **Rule: do not report completion until the re-scan of the original adds zero new rows.**

### Hard verification (the guard against "记了 fixed 但正文没改")

A ledger row that claims `disposition: fixed` must be reflected in the text, not just in the ledger. Verify both directions:

- Every `fixed` row: its literal `original` must NOT still appear in the edited text. If it does, the change was claimed but not applied — treat as a dropped fix and redo it.
- Every `kept` row: its literal `original` SHOULD still appear. If it vanished, a kept item was accidentally changed — restore it.

You can automate the first half with `python scripts/detect.py --residual <original> <edited>` — it lists which pattern hits remain in the edited text.

## Step 4.5 Semantic triage — 专有名词 vs AI word, by meaning

The scanner outputs candidates, not verdicts. For every candidate, decide its disposition **semantically** from its context, not from any hard-coded list:

- 专有名词 / fixed term → `kept` (景观格局, 分布格局, 发展格局, 食物链, 闭环控制…).
- Genuine AI usage → `fixed` (bare 格局 in "打开工作格局", 深化 as filler, 依托 where 通过 works).
- A general token that is a 专有名词 in this domain but AI filler in another → judge by THIS text's conventions.
- Unsure → `review (human)` and surface it. Do not guess to save work.

Use `python scripts/detect.py --triage <file>` to get candidates with `context_before`/`context_after` and an `allowlist_hint`. The hint is advisory only — verify it against context (e.g. "格局" inside "景观格局" is fine, bare "格局" is not). Full decision rules: `references/protocol.md` §3.5.

## Step 5. Long documents — manual chunking (fallback)

If you are not fanning out to subagents but the text is Long:

1. Split the text at paragraph or section boundaries into chunks of roughly 500–800 characters. Do not split mid-sentence. Use `python scripts/detect.py --chunks <file>` for line ranges, or split by hand. Number the chunks (chunk_01, chunk_02, …) so reassembly order is unambiguous.
2. Process each chunk independently against Steps 1–4.
3. After every chunk, re-read that chunk's original once more and reconcile the ledger.
4. Concatenate the fixed chunks, then run a whole-document scan for cross-chunk issues (echo conclusions, uniform-length problems, symbols spanning a break).

## Step 6. Long documents — fan out to subagents (preferred)

For Long text, the scalable fix is bounded context: each chunk is edited by its own subagent in its own context, so no single context holds the whole document while applying rules.

**On DSH, do not write the orchestrator from scratch** — `scripts/workflow_deanti.js` is ready to run. Put its body verbatim into the `workflow` tool's `script` parameter and pass the document as `args` (`{ "text": "…", "genre": "report", "chunkTarget": 700 }`). It chunks, runs `pipeline` with one subagent per chunk, forces `{ fixed_text, ledger }` through `opts.schema`, strips chunk-seam `…` markers, and returns `{ assembled_text, merged_ledger, counts, validation }`. Reconcile `validation.issues` if any; a `false-fixed` (claimed fixed but still present) or `false-kept` (kept but missing) row names the chunk and fragment, so re-run that chunk only. Feed `review (human)` rows to the human.

**On any other harness**, do the same thing by hand:

1. Split the text into chunks of ~500–800 chars at paragraph/section boundaries (same rule as Step 5).
2. Launch one Task subagent per chunk (in parallel). Give each subagent:
   - The chunk text, with a `…` seam marker at the start/end as a context hint for neighboring text (tell it NOT to keep the marker in its output).
   - The rule set: Must/Should/Consider lists + semantic triage (专有名词 → `kept`; unsure → `review (human)`, do not default every Should-fix to `kept`).
   - A strict output contract: return JSON `{ "fixed_text": string, "ledger": [ { "type", "original", "fixed", "disposition" } ] }` where disposition ∈ `fixed` / `kept` / `skipped` / `review (human)`.
   - The hard rule: `fixed_text` must be plain prose only (no JSON structure, no keys like "fixed_text", no braces, no "返回：" prefixes); every `fixed` row's `original` must NOT remain in `fixed_text`; every `kept` row's original must remain verbatim.
3. Reassemble in chunk order; merge ledgers.
4. Hard-verify programmatically: every `fixed` row's `original` absent from the assembled text, every `kept` row's original present. Any chunk that fails → re-run that chunk only. Feed `review (human)` rows to the human.

Both routes run the same two mechanisms: bounded context + a machine-checkable loop.

## Step 7. Verify

Audit before declaring done:

- [ ] All 🔴 patterns removed? Confirmed by re-scanning the ORIGINAL, not the output.
- [ ] Ledger present with no empty disposition?
- [ ] Sentence length variance: longest/shortest ≥ 4 within any 500-char window?
- [ ] No intact "首先/其次/第三/第四/最后" sequence?
- [ ] No paragraph ends with a self-praising summary?
- [ ] No sentence opens with "值得注意的是" or "需要强调的是"?
- [ ] No sentence ends with "反映了……的……"? Replace with a factual statement or delete.
- [ ] Em-dash count < 2 per 1000 chars?
- [ ] All value-judgment adjectives justified or removed?
- [ ] 突出 count < 5 per 1000 chars (if higher, most are filler)?
- [ ] Zero arrows of ANY direction (→ ← ↑ ↓ ⇒ ⇐ ⇑ ⇓ ➡ ⟶ ⇨ and ASCII `->` `=>`) anywhere in prose — verified by `python scripts/qa_symbols.py <edited>` exiting 0, not by eyeballing?
- [ ] Zero corner brackets 「」, zero check marks and zero status emoji — same gate confirms it?
- [ ] Any surviving × confirmed to be a multiplication sign, not a verdict mark?
- [ ] ①②③ and ≤ ≥ left alone (these are correct Chinese typography, not AI symbols)?
- [ ] Hard check passed: every `fixed` ledger row's `original` is absent from the assembled text, and every `kept` row's `original` is still present?
- [ ] No `…` seam marker leaked into the assembled text?
- [ ] For Long docs: every chunk has a ledger and appears in the assembled output exactly once?

## Five Universal Rules

### 1. Cut, Don't Soften
Filler adds nothing. Delete it.
> 值得注意的是， → (delete)
> 需要强调的是， → (delete)

### 2. State Facts, Not Judgments
Let facts carry weight. Strip the adjectives.
> 建立了完善的质控体系 → 建立了质控体系
> 重要的粮食产区 → 粮食产区
> 品质优良 → (delete, the data speaks)

**Edge case — 显著**: Keep when backed by a p-value (显著影响, p<0.05). Delete when used as generic emphasis (显著改善, 显著提升). The difference: if you can't cite a significance test, it's filler.

### 3. Name Specifically, Don't Gesture
> 专家认为 → name the expert, or delete
> 研究表明 → cite the study, or delete

### 4. Vary Structure, Don't Template
> Don't start three consecutive sentences the same way.
> Don't end three consecutive paragraphs with a summary.
> Avoid "首先A, 其次B, 第三C, 第四D, 最后E" at all costs.

### 5. Connect by Meaning, Not by Marker
Kill connective words. Let logic carry the transition.
> 此外 / 另外 / 同时 / 并且 → delete
> 因此 / 所以 → reduce by 70%
> 然而 / 但是 → reduce by 50%

## Genre Adaptation

When the genre is known, load the corresponding pattern file for genre-specific 🔴 patterns:

| Genre | File | Key additions |
|-------|------|--------------|
| Government/technical report | `references/patterns/report.md` | encyclopedia openings, policy slogans, bureaucratic filler, 了-stacking |
| Academic paper | `references/patterns/academic.md` | "填补空白" claims, citation hallucinations, formulaic challenges |
| Narrative / general prose | (universal only) | Focus on voice injection over pattern removal |

To activate: state the genre at the start. The agent loads the file and merges with universal patterns.

## Boundaries

This skill does NOT:
- Rewrite content or alter factual meaning
- Fix grammar, spelling, or punctuation (separate concern)
- Add new content or expand arguments
- Convert between languages
- Judge writing quality beyond AI-pattern presence

If AI-pattern density exceeds ~40% of sentences, flag the text rather than attempting full rewrite — the underlying content may need human restructuring first.

## Resources

Load on demand, not all at once:

- `references/protocol.md` — the execution protocol for chunking, ledger reconciliation, and failure retry.
- `references/principles.md` — WHY each pattern signals AI (read when unsure about an edge case).
- `references/replacements.md` — Quick lookup: AI word → natural alternative.
- `references/lexicon.md` — 语义库：翻案腔七类外衣、绝对禁词、语境词、借喻词、抒情词、名词化与结尾大词。先过 A 类（翻案腔），再清 B 类，C/D/E 按语境判。
- `references/patterns_data.json` — Data-driven pattern catalog (add words/categories by editing JSON, not code).
- `references/allowlist.json` — Hint-only allowlist of known 专有名词/固定搭配 (advisory for semantic triage, never an authoritative skip).
- `references/patterns/universal.md` — Full universal catalog with signal levels and examples.
- `references/patterns/report.md` — Government/technical report patterns.
- `references/patterns/academic.md` — Academic paper patterns.
- `references/patterns-english.md` — English AI patterns (legacy, Wikipedia-based).
- `references/wikipedia-source.md` — Original source attribution.
- `scripts/detect.py` — Scanner. Modes: default `<file>` (summary report); per-instance candidates `--hits <file>`; candidates with context for semantic triage `--triage <file>`; residual hits left in an edited text `--residual <original> <edited>`; chunk line ranges `--chunks <file>`. Pure standard library.
- `scripts/qa_symbols.py` — Delivery gate. Full-text zero-tolerance scan for arrows of every direction (plus ASCII `->` `=>`), status emoji, check marks and corner brackets; code fences are skipped by default. Exits 1 if anything fatal remains — run it before handing text over.
- `scripts/workflow_deanti.js` — Ready-to-run DSH `workflow` orchestrator body for Step 6. Put its body verbatim into the `workflow` tool's `script` parameter and pass the document as `args` (`{ "text": "…", "genre": "report", "chunkTarget": 700 }`).
