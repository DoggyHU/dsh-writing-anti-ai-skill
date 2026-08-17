# Execution Protocol

The protocol that makes editing reliable on long documents. Named in the skill body; load it when the text is Medium or Long, or any time you need to guard against dropped fixes.

## Why this exists

A single pass over a long document in one context loses attention. The model sees the rules at the top of its context, the text fills the rest, and by the middle-to-end it is no longer comparing against the full rule set. Fixes get silently dropped. The ledger and the chunking below exist to make that failure visible and to bound it.

The core discipline: **re-scan the original, not your own output.** Self-checking edited text has confirmation bias; it confirms what you already changed and misses what you never saw.

## 1. Size decision

| Size | Estimate | Method |
|------|----------|--------|
| Short | up to ~600 chars | Single pass + one re-scan of the original. |
| Medium | ~600–2,500 chars | 3–5 chunks; independent per-chunk edits; ledger merge. |
| Long | over ~2,500 chars or 40+ sentences | Fan out with `workflow`/`subagent` if available; else manual chunking. Prefer `workflow`. |

Do not let any single editing context hold more than ~800 chars of target text while applying rules. Above that, attention decay starts dropping fixes.

## 2. Chunking rules

- Split at paragraph or section boundaries only. Never split mid-sentence.
- Aim for 500–800 characters per chunk.
- Keep tables and code blocks intact within one chunk wherever possible; a symbol chain spanning a break is a whole-document check, not a per-chunk one.
- Number the chunks so reassembly order is unambiguous: chunk_01, chunk_02, …

## 3. The ledger

One row per detected instance:

| Type | Original | Fixed | Disposition |
|------|----------|-------|-------------|
| Must-fix: filler | 值得注意的是 | (deleted) | fixed |
| Must-fix: arrow chain | A→B→C | A、B 到 C | fixed |
| Consider: rule of three | …X、Y、Z… | — | kept (natural) |

Disposition is one of: `fixed`, `kept (reason)`, `skipped (reason)`. Never leave it blank. A blank disposition is a missing accountability entry.

## 3.5 Semantic triage — decide 专有名词 vs AI word by meaning, not lookup

The scanner (`detect.py --triage`) outputs **candidates**, not verdicts. It cannot know every domain's 专有名词 (生态/规划/化学/计算机…), so a hard-coded allowlist can never be complete. Decide each candidate's disposition **semantically**, using the `context_before`/`context_after` the scanner attached:

- **专有名词 / 固定搭配 → keep.** e.g. "景观格局" (landscape pattern), "分布格局" (statistics), "发展格局" (policy term), "食物链", "闭环控制" (control theory). Judged by meaning + the field's conventions, not by any list.
- **Genuine AI usage → fix.** e.g. bare "打开工作格局", "深化" as filler, "依托" where 通过 works.
- **`allowlist_hint: true`** on a candidate is only a *nudge* that the token sits inside a known-common proper noun. Verify with context: it may be a false nudge (e.g. "格局" not actually part of "景观格局"). The hint is advisory, never final.
- When you are **unsure** whether a token is a proper noun or AI filler, mark it `review (human)` in the disposition and list it for human confirmation. Do not guess to reduce work.

For a medium/long document, you may hand the triage CSV to a subagent per chunk so each decision is made in a bounded context; collect the kept-set and the fixed-set separately, then merge into the ledger.

## 4. Reconciliation pass

After editing, always:

1. Take the ORIGINAL text again, not the edited output.
2. Scan it start to end against the pattern lists.
3. For every hit, confirm there is a ledger row.
4. Any hit found in this pass that has no row is a fix the first pass dropped. Add it and fix it.
5. Stop only when this re-scan adds zero new rows.

This is the whole point. The first scan finds most; the re-scan of the original catches what attention decay hid.

### 4.1 Hard verification (this is the guard against "记了 fixed 但正文没改")

A ledger row that claims `disposition: fixed` must be reflected in the text, not just in the ledger. Verify both directions:

- Every `fixed` row: its literal `original` must NOT still appear in the edited text. If it does, the change was claimed but not applied — treat as a dropped fix and re-run that chunk.
- Every `kept` row: its literal `original` SHOULD still appear. If it vanished, a `kept` item was accidentally changed — restore it.

The workflow script (`scripts/workflow_deanti.js`, §verify phase) implements this automatically: it strips seam markers, then for each chunk checks that `fixed` rows are absent from the output and `kept` rows are present. A false-`fixed` or false-`kept` row makes `validation.ok` false and lists the specific chunk and fragment. Do not trust a ledger that reports `fixed` without this check.

### 4.2 Seam markers

Chunk seams use `…` only as a context hint for the editor; they are stripped from the final output. If a `…` appears in the assembled text, the editor wrongly kept a seam marker — strip it and treat the chunk's fixed_text as containing a leak to fix.

## 5. Long-document workflow (preferred)

When `workflow` is available:

1. Split into named chunks; pass as `args`.
2. `pipeline(chunks, editStage)` where `editStage` is one subagent call per chunk, each inside its own context.
3. Give each subagent: the chunk text, the replacement tables, the universal pattern list, and a structured-output schema requesting `{ fixed_text, ledger }`.
4. Reassemble in chunk order; merge ledgers.
5. Reconciliation in the coordinator against the original chunks (each chunk processed once, every Must-fix has a row).

Each chunk in its own context bounds attention decay to ~800 chars. That, plus the shared ledger, is what fixes "I only corrected 50 of 100."

## 6. Failure retry

- If a subagent returns without `fixed_text` or with an empty `ledger`, treat it as not done. Re-run that chunk.
- If reconciliation finds a chunk with no ledger, re-run that chunk.
- If reassembly shows text missing from the original (a chunk was skipped), re-run the missing chunk.
- Do not report completion with any chunk unresolved.

## 7. Reporting

End with a short summary that names the numbers:

- Chunks processed / total
- Hits found / fixed / kept
- Second-pass additions (fixes the first pass missed)
- Whole-document checks passed

These numbers are the evidence that the work actually closed the loop. Without them, "done" means nothing here.
