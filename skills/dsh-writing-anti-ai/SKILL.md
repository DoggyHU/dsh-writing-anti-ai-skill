---
name: dsh-writing-anti-ai
description: This skill should be used when the user asks to "remove AI writing patterns", "去AI味", "除AI痕迹", "humanize this text", "make this sound more natural", "remove AI-generated traces", "fix robotic writing", or needs to eliminate AI writing patterns from prose. Supports Chinese and English across multiple genres including reports, academic papers, and narrative. Native to DeepSeek Harness (DSH): automatically scales short/medium/long documents, and for long text uses the DSH workflow + subagent tools to fan out per-chunk edits with machine-checkable structure. Based on Wikipedia's "Signs of AI writing" guide.
---

# Writing Anti-AI (NTAI)

Remove AI-generated writing patterns. Turn machine prose into human prose.

## Signal Levels

Every pattern carries a signal level that decides how to handle it:

| Level | Rule |
|-------|------|
| Must-fix | Remove on sight. No exceptions. |
| Should-fix | Remove unless the genre explicitly requires it. |
| Consider | Flag. The decision depends on context. |

When uncertain, treat Must-fix as non-negotiable, and keep a Should-fix item only when there is a reason.

## Step 0. Size the job before editing

Estimate the target text size. Choose the strategy that matches. **Never attempt a full multi-pass edit of a long document in a single context** — attention decays across a long input and fixes silently get dropped. This is the single most common cause of "I only corrected 50 of 100."

| Size | Threshold | Strategy |
|------|-----------|----------|
| Short | up to ~600 chars | Single pass, then forced re-check of the original. |
| Medium | ~600–2,500 chars | Split into chunks; edit each chunk; re-check with a ledger. |
| Long | over ~2,500 chars or 40+ sentences | Fan out to subagents via the DSH `workflow`/`subagent` tools, one chunk per subagent, structured ledger output. |

If the DSH `workflow` tool is available and the text is Long, use it (see Step 6). If it is not available, fall back to manual chunking (see Step 5).

## Step 1. Scan (word level)

Flag every instance of:

- Filler phrases. Consult `references/replacements.md` for the lookup table.
- AI marker words: 依托, 赋能, 闭环, 抓手, 格局, 夯实, 扎实推进, 深入开展, 持续优化, 显著, 大幅.
- Overused vague intensifiers: 突出 (the most common offender in reports, often ten or more instances per file), 核心, 关键, 主导, 根本 when used as filler causal connectors.
- Value-judgment adjectives: 重要的, 著名的, 优良的, 完善的, 严格的, 充分的, 深刻的, 丰富的, 良好的, 优越的, 优异的, 独特的.
- Intensifier stacking: 非常, 极其, 极为, 极度, 急剧, 大幅, 持续, 不断, 严重 when used as generic emphasis without data backing.
- Vague attributions with no source: 专家认为, 研究表明, 据悉, 据了解, 数据显示.
- Arrow-symbol chains: (→, ⇒, ➡, ➤, ➜) used as flowchart connectors joining three or more items in prose, such as A→B→C→D. Replace with commas or a natural list.

For a Must-fix item, replace or delete immediately. Record each hit in the ledger (Step 4). Mark Should-fix items for the sentence pass.

For a token that might be a 专有名词 or fixed term (景观格局, 分布格局, 发展格局, 闭环控制…), do NOT auto-fix or auto-skip from a list. Decide by meaning using the surrounding context — see Step 4.5 (semantic triage). A hard-coded allowlist cannot cover every domain, so the judgment is semantic, not lookup.

## Step 2. Restructure (sentence level)

Target structural patterns:

- Mechanical enumeration: sequences of 首先/其次/第三/第四/最后. Break the sequence: expand one step, collapse the others.
- Double modifiers: A与B pairs doing the same job (验证与确认, 精准度与准确度). Keep one.
- 确保/保障 plus an abstract noun ending. Replace with a factual statement or delete.
- Self-praising paragraph closers. Delete the whole closing sentence.
- Em-dash overuse. More than two per thousand characters. Replace with a comma or a period.
- Heavy colon density. More than 1.5 per hundred characters. Restructure.

Rewrite sentence structure and vary length. Every two hundred characters should contain at least one sentence of twelve characters or fewer.

## Step 3. Reorganize (document level)

Check document-level patterns:

- Encyclopedia openings ("XX位于...是...的重要..."). Cut to what the reader needs.
- Policy slogan clusters. Replace with factual description.
- Echo conclusions. A conclusion must add new information, not restate the introduction.
- Uniform paragraph length. Vary paragraph size by at least twofold within the document.
- Genre-specific patterns. If the genre is known, load the matching file from `references/patterns/`.

Restructure paragraphs and sections for a natural rhythm.

## Step 4. Maintain a ledger — this closes the loop

Never finish without a ledger. The ledger is what makes omissions visible. Produce a table with a row per detected instance:

| Type | Original | Fixed | Disposition (fixed / kept / skipped) |

- Every Must-fix token you find gets a row.
- If you kept something, say why in the disposition.
- At the end, re-scan the ORIGINAL text with fresh eyes, not your edited output. Compare the ledger against the original. Anything you missed the first time is exactly what attention decay hides — add it.

Rule: do not report completion until the re-scan of the original adds zero new rows.

## Step 4.5 Semantic triage — 专有名词 vs AI word, by meaning

The scanner outputs candidates, not verdicts. For every candidate, decide its disposition **semantically** from its context, not from any hard-coded list:

- 专有名词 / fixed term → `kept` (景观格局, 分布格局, 发展格局, 食物链, 闭环控制…).
- Genuine AI usage → `fixed` (bare 格局 in "打开工作格局", 深化 as filler, 依托 where 通过 works).
- A general token that is a 专有名词 in this domain but AI filler in another → judge by THIS text's conventions.
- Unsure → `review (human)` and surface it. Do not guess to save work.

Use `detect.py --triage <file>` to get candidates with `context_before`/`context_after` and an `allowlist_hint`. The hint is advisory only — verify it against context. Full decision rules: `references/protocol.md` §3.5.

## Step 5. Long documents without the workflow tool

If `workflow` is unavailable but the text is Long:

1. Split the text at paragraph or section boundaries into chunks of roughly 500–800 characters. Do not split mid-sentence.
2. Process each chunk independently against Steps 1–4.
3. After every chunk, re-read that chunk's original once more and reconcile the ledger.
4. Concatenate the fixed chunks, then run a whole-document scan for cross-chunk issues (echo conclusions, uniform-length problems, symbols spanning a break).

## Step 6. Long documents with the workflow tool (preferred)

If the DSH `workflow` tool is available and the text is Long, do NOT write an orchestrator from scratch. Use the ready-to-run script at `scripts/workflow_deanti.js`:

1. Read `scripts/workflow_deanti.js` (or recall it) and put its body verbatim into the `workflow` tool's `script` parameter.
2. Pass the document as `args`, e.g. `{ "text": "<the full text>", "genre": "report", "chunkTarget": 700 }`.
3. The script already does the two DSH things that solve attention decay:
   - **Bounded context**: `pipeline` runs one subagent per chunk, each in its own context, so no single context holds the whole document while applying rules.
   - **Machine-checkable loop**: `opts.schema` forces every subagent to return `{ fixed_text, ledger }`; the script then validates programmatically that (a) no chunk was dropped, (b) no ledger row lacks a disposition, (c) — the hard gate — every `fixed` row's `original` is actually GONE from the output and every `kept` row's `original` is actually STILL PRESENT. It strips chunk-seam `…` markers and returns `{ assembled_text, merged_ledger, counts, validation }`.
4. Adjust `args.genre` to match the text. The per-chunk prompt already lists Must/Should rules and semantic triage (专有名词 keep, unsure -> `review (human)`); it explicitly tells the editor NOT to default every Should-fix to `kept` — only genuine 专有名词/固定搭配 stay, real AI-flavored phrasing gets fixed.
5. After the run, reconcile `validation.issues` if any — a `false-fixed` (claimed fixed but still present) or `false-kept` (kept but missing) row names the chunk and fragment; re-run that chunk. Feed the merged_ledger's `review (human)` rows to the human.

The earlier JSON in this step is now superseded by that script; keep it only if you must inline a minimal schema.

## Step 7. Verify

Audit before declaring done:

- All Must-fix patterns removed? Confirmed by re-scanning the ORIGINAL, not the output.
- Ledger present with no empty disposition?
- No intact 首先/其次/第三/第四/最后 sequence?
- No paragraph ends with a self-praising summary?
- No sentence opens with 值得注意的是 or 需要强调的是?
- No sentence ends with "反映了……的……"? Replace with a factual statement or delete.
- Em-dash count below two per thousand characters?
- All value-judgment adjectives justified or removed?
- 突出 count below five per thousand characters?
- No arrow-symbol chain of three or more items in prose?
- For Long docs: every chunk has a ledger and appears in the assembled output exactly once?
- Hard check passed: every `fixed` ledger row's `original` is absent from the assembled text, and every `kept` row's `original` is still present (this is the guard against "记了 fixed 但正文没改")
- No `…` seam marker leaked into the assembled text

## Five Universal Rules

### 1. Cut, do not soften
Filler adds nothing. Delete it.
> 值得注意的是 (delete)
> 需要强调的是 (delete)

### 2. State facts, not judgments
Let facts carry the weight. Strip the adjectives.
> 建立了完善的质控体系 → 建立了质控体系
> 重要的粮食产区 → 粮食产区
> 品质优良 → delete; the data speaks

Keep 显著 only when a significance test backs it (显著影响, p<0.05). Delete it when used as generic emphasis (显著改善, 显著提升). The test: if you cannot cite a significance test, it is filler.

### 3. Name specifically, do not gesture
> 专家认为 → name the expert, or delete
> 研究表明 → cite the study, or delete

### 4. Vary structure, do not template
Do not start three consecutive sentences the same way. Do not end three consecutive paragraphs with a summary. Avoid the 首先/其次/第三/第四/最后 pattern entirely.

### 5. Connect by meaning, not by marker
Kill connective words and let the logic carry the transition.
> 此外, 另外, 同时, 并且 → delete
> 因此, 所以 → cut by about 70%
> 然而, 但是 → cut by about 50%

## Genre Adaptation

When the genre is known, load the matching pattern file for genre-specific patterns:

| Genre | File | Key additions |
|-------|------|--------------|
| Government/technical report | `references/patterns/report.md` | encyclopedia openings, policy slogans, bureaucratic filler, 了-stacking |
| Academic paper | `references/patterns/academic.md` | "填补空白" claims, citation hallucinations, formulaic challenges |
| Narrative / general prose | (universal only) | focus on voice injection over pattern removal |

To activate, state the genre at the start. Load the file and merge it with the universal patterns.

## Boundaries

This skill does not:

- Rewrite content or alter factual meaning
- Fix grammar, spelling, or punctuation (a separate concern)
- Add new content or expand arguments
- Convert between languages
- Judge writing quality beyond the presence of AI patterns

If AI-pattern density exceeds roughly 40% of sentences, flag the text instead of attempting a full rewrite; the underlying content may need human restructuring first.

## Resources

Load on demand, not all at once:

- `references/protocol.md`: the execution protocol for chunking, ledger reconciliation, and failure retry.
- `references/principles.md`: why each pattern signals AI. Read when unsure about an edge case.
- `references/replacements.md`: quick lookup mapping an AI word to a natural alternative.
- `references/patterns/universal.md`: full universal catalog with signal levels and examples.
- `references/patterns/report.md`: government and technical report patterns.
- `references/patterns/academic.md`: academic paper patterns.
- `references/patterns-english.md`: English AI patterns (legacy, based on Wikipedia).
- `references/wikipedia-source.md`: source attribution.
- `scripts/detect.py`: scanner. Emits candidates `--triage` (with context), per-instance `--hits`, residual `--residual`, and chunk ranges `--chunks`. Scanner gives candidates with `allowlist_hint`; the verdict comes from semantic triage (Step 4.5).
- `scripts/workflow_deanti.js`: ready-to-run DSH `workflow` orchestrator for Long docs. Fans out chunks to subagents (bounded context) and machine-validates the ledger. Copy its body into the `workflow` tool's `script`; pass text as `args`.
