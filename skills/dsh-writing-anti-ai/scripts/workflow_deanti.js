// writing-anti-ai — DSH workflow orchestrator (attention-safe long-doc edit)
//
// WHY THIS SCRIPT EXISTS
// Attention decay on a long document is the "I only fixed 50 of 100" problem.
// This orchestrator solves it with the two DSH workflow mechanisms:
//   1. BOUNDED CONTEXT — split the document into ~500-800 char chunks, each
//      edited by its own subagent in its own context, so no single context
//      holds the whole document while applying rules.
//   2. STRUCTURED, MACHINE-CHECKABLE LOOP — `opts.schema` forces every subagent
//      to return fixed_text + ledger; this script VALIDATES programmatically
//      (no dropped chunk, no empty disposition, AND no "fixed claimed but not
//      applied" — every `fixed` ledger row must be reflected in the text).
//
// USING IT
// Pass the target text as args, e.g. { "text": "...", "genre": "report", "chunkTarget": 700 }.
// The model-facing workflow tool supplies this file's body verbatim as `script`.
// You may edit meta.name/description; keep the structure below.

const CHUNK_TARGET = (args && args.chunkTarget) || 700
const GENRE = (args && args.genre) || null

function chunkText(text, target) {
  const raw = text.split(/(?<=\n)\n+/)
  const chunks = []
  let cur = ''
  const push = () => { if (cur.trim()) chunks.push(cur.trim()); cur = '' }
  for (const para of raw) {
    if ((cur + '\n' + para).length > target && cur) push()
    cur = cur ? cur + '\n' + para : para
  }
  push()
  return chunks
}

// The seam marker is injected ONLY as a context hint so the editor sees the
// neighboring text around a break; the returned fixed_text MUST NOT include it.
const SEAM = '\u2026' // …
function seamPad(chunk, i, chunks) {
  let out = chunk
  if (i > 0) out = SEAM + out
  if (i < chunks.length - 1) out = out + SEAM
  return out
}
function stripSeam(s) {
  return s.split(SEAM).join('').trim()
}

phase('chunking')
log(`splitting ${(args && args.text || '').length} chars into chunks near ${CHUNK_TARGET}`)
const chunks = chunkText(args.text || '', CHUNK_TARGET)
log(`created ${chunks.length} chunks`)
phase('deanti-chunk-edit')

// Per-chunk editing done by an independent subagent (bounded context).
const perChunk = await pipeline(
  chunks.map((c, i) => ({ i, c })),
  async (item) => {
    const chunk = seamPad(item.c, item.i, chunks)
    const prompt = `去AI味，只改这一个片段，返回结构化结果。

规则（Must-fix 一律改，Should-fix 应改尽量改，Consider 记入 ledger 通常保留）:
- Filler phrases: 值得注意的是/需要强调的是/需要指出的是/众所周知/换句话说/总体而言/在……的背景下 等 -> 删
- AI marker words: 依托/赋能/闭环/抓手/格局/夯实/扎实推进/深入开展/持续优化/显著/大幅 等 -> 换通俗词（在专有名词里的不计，如 景观格局/分布格局/发展格局）
- Value-judgment adjectives: 重要的/著名的/完善的/显著的/关键的 等(非技术术语) -> 删
- Vague attributions: 专家认为/研究表明/据了解/数据显示(无来源) -> 写具体来源或删
- Arrow chains A->B->C -> 逗号/到/再到；单个箭头也改，不限于 3+ 串联
- 状态 emoji(✅❌⚠️)、勾叉(√✓✖)、角括号「」-> 换成对应中文词或标准引号“”
- 黑话: 商业闭环/能力沉淀/拉通/底层逻辑/顶层设计/降本增效/全链路/组合拳 等 -> 换成具体说法
- 翻案腔(先造靶子再打倒): "不是A而是B"、"看似A实则B" -> 正面直说 B，依据放旁边
- Should-fix: 首先/其次/第三(机械枚举) -> 拆节奏; 双重修饰(A与B同义) -> 留一个;
- Consider: rule-of-three/同义词替换(同一事物不同说法) -> 记入 ledger，通常保留

语义三审(不要查表，用知识判断): 专有名词/固定搭配(景观格局、分布格局、发展格局、食物链、闭环控制…) -> ledger 记 kept，不改。
Should-fix 不要一律 kept：只要语义上确实是 AI 味，就改（fixed）；只有语义上确实是专有名词/固定搭配才 kept。真拿不准 -> ledger 记 review (human)，不改。

【硬性要求】fixed_text 必须是那个片段的纯文本改写，绝对禁止在其中包含任何 JSON 结构、双引号键名（如 "fixed_text"、"ledger"）、花括号 { }，也不要以"返回："等行为语言开头。fixed_text 只能是可直接拼进文档的正文。
片段开头/结尾的占位符 … 只是相邻片的提示，不要在返回的 fixed_text 里保留它。
只改下面这一个片段，不要增减该片段之外的内容，保留事实、数字、专有名词、文献引用与 § 编号与 Markdown 标题层级。

片段[${item.i}]：
${chunk}

返回严格 JSON，schema:
{ "fixed_text": string, "ledger": [ { "type": string, "original": string, "fixed": string|"", "disposition": "fixed"|"kept"|"skipped"|"review (human)" } ] }
每个改了或判定保留的命中都必须在 ledger 里有一行。凡是 disposition=fixed 的，fixed_text 里必须确实不再保留 literal 原文；凡是 disposition=kept 的，原文保持原样。`
    const res = await agent(prompt, {
      label: `chunk-${item.i}`,
      phase: 'deanti-chunk-edit',
      schema: {
        type: 'object',
        additionalProperties: false,
        properties: {
          fixed_text: { type: 'string' },
          ledger: {
            type: 'array',
            items: {
              type: 'object',
              additionalProperties: false,
              properties: {
                type: { type: 'string' },
                original: { type: 'string' },
                fixed: { type: 'string' },
                disposition: { type: 'string', enum: ['fixed', 'kept', 'skipped', 'review (human)'] }
              },
              required: ['type', 'original', 'disposition']
            }
          }
        },
        required: ['fixed_text', 'ledger']
      }
    })
    if (!res) return { i: item.i, ok: false }
    return { i: item.i, ok: true, ...res }
  }
)

phase('assembly')
// Assemble in order; any failed chunk must be surfaced, never silently dropped.
const byIndex = {}
for (const r of perChunk) if (r && r.ok) byIndex[r.i] = r
const assembled = []
for (let i = 0; i < chunks.length; i++) {
  assembled.push(byIndex[i] ? stripSeam(byIndex[i].fixed_text) : null)
}
const missing = chunks.map((_c, i) => i).filter(i => !byIndex[i])
const mergedLedger = []
for (let i = 0; i < chunks.length; i++) {
  if (byIndex[i] && Array.isArray(byIndex[i].ledger)) mergedLedger.push(...byIndex[i].ledger)
}
phase('verify')
// Machine-checkable loop: the whole point of DSH structured output.
const issues = []
if (missing.length) issues.push(`missing chunks: ${missing.join(',')}`)

// (a) every ledger row has a disposition
const empties = mergedLedger.filter((l) => !l.disposition)
if (empties.length) issues.push(`${empties.length} ledger rows lack a disposition`)

// (b) HARD CHECK — a row claiming `fixed` must be reflected in the text:
//     the literal `original` must NOT still appear in the assembled output.
//     This catches "记了 fixed 但正文没改" — the exact silent-drop failure.
for (let i = 0; i < chunks.length; i++) {
  const r = byIndex[i]
  if (!r || !Array.isArray(r.ledger)) continue
  const fixedRows = r.ledger.filter((l) => l.disposition === 'fixed')
  const assembledChunk = stripSeam(r.fixed_text)
  for (const row of fixedRows) {
    const orig = (row.original || '').trim()
    if (!orig) continue
    if (assembledChunk.includes(orig)) {
      issues.push(`chunk ${i}: claimed fixed '${orig.slice(0, 25)}' but still present`)
    }
  }
}

// (c) kept rows must NOT have been silently changed — the original should remain.
for (let i = 0; i < chunks.length; i++) {
  const r = byIndex[i]
  if (!r || !Array.isArray(r.ledger)) continue
  const keptRows = r.ledger.filter((l) => l.disposition === 'kept')
  const assembledChunk = stripSeam(r.fixed_text)
  for (const row of keptRows) {
    const orig = (row.original || '').trim()
    if (orig && !assembledChunk.includes(orig)) {
      issues.push(`chunk ${i}: kept '${orig.slice(0, 25)}' but missing from output`)
    }
  }
}

const fixes = mergedLedger.filter((l) => l.disposition === 'fixed')
const reviews = mergedLedger.filter((l) => l.disposition === 'review (human)')
log(`chunks=${chunks.length} fixed=${fixes.length} reviews=${reviews.length} issues=${issues.length}`)

return {
  chunks: chunks.length,
  missing,
  assembled_text: assembled.join('\n'),
  merged_ledger: mergedLedger,
  counts: {
    fixed: fixes.length,
    kept: mergedLedger.filter((l) => l.disposition === 'kept').length,
    skipped: mergedLedger.filter((l) => l.disposition === 'skipped').length,
    review_human: reviews.length
  },
  validation: { issues, ok: issues.length === 0 }
}
