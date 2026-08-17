#!/usr/bin/env python3
"""Data-driven AI-pattern detector for Chinese text.

词表/白名单不再硬编码在代码里，而是从数据文件加载，加词、加专有名词白名单、加文体只改数据，不动代码。

Usage:
    python detect.py <file.typ|file.txt|file.md>                 # summary report
    python detect.py --hits <file> [out.csv]                     # per-instance candidate CSV
    python detect.py --triage <file> [out.csv]                   # candidates w/ context for semantic review
    python detect.py --residual <original> <edited> [out.csv]    # hits left in edited text
    python detect.py --chunks <file> [min]                       # print line ranges per chunk

Options:
    --data <dir>      pattern data dir (default: ../references)
    --allowlist <file>  hint JSON (default: ../references/allowlist.json)

DESIGN: this scanner produces CANDIDATES, not verdicts. It cannot know every
domain's 专有名词 (生态/规划/化学/计算机...), so it extracts each match with a
context window and an allowlist_hint, and leaves the 保留/修复 decision to the
SEMANTIC-triage step (the LLM reasoning over the context) described in
SKILL.md / references/protocol.md, then to human review where confidence is low.
The allowlist JSON is a small HINT list of known false positives, never an
authoritative skip — an unbounded hard-coded allowlist would become a dictionary
and cannot generalize to arbitrary domains.

Pure standard library — no dependencies.
"""

import re
import sys
import csv
import json
from pathlib import Path

# Force UTF-8 on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

_DEFAULT_DATA_DIR = Path(__file__).resolve().parent.parent / "references"


# ── Data loading (patterns + whitelist) ──────────────────────────────

class PatternSet:
    """Loaded, data-driven pattern set. Adding a category or a word = edit JSON.

    The allowlist is NOT an authoritative "skip" list. It is a small set of
    known high-frequency false positives (领域专有名词/固定搭配) used only to
    ATTACH a hint to a candidate: when a token sits inside one of these terms,
    the candidate gets `allowlist_hint: true` and the semantic-triage step (the
    model) leans toward keeping it. The scanner never skips on the allowlist —
    an unbounded hard-coded allowlist cannot cover every domain (城市规划/化学/
   计算机...), so the final judgment belongs to semantic reasoning, not lookup.
    """

    def __init__(self, categories: list[dict], structural: dict, allowlist: list[dict]):
        self.categories = categories
        self.structural = structural or {}
        self.allowlist = [a.get("term", "") for a in allowlist if a.get("term")]
        # Longer whitelist terms win over shorter substrings (景观格局 > 格局)
        self.allowlist.sort(key=len, reverse=True)

    @classmethod
    def load(cls, data_dir: Path, allowlist_file: Path) -> "PatternSet":
        with open(data_dir / "patterns_data.json", encoding="utf-8") as f:
            data = json.load(f)
        allow = []
        if allowlist_file.exists():
            with open(allowlist_file, encoding="utf-8") as f:
                allow = json.load(f).get("allowlist", [])
        return cls(data.get("categories", []), data.get("structural", {}), allow)

    def enabled_categories(self, genre: str | None = None) -> list[dict]:
        out = []
        for c in self.categories:
            if c.get("file") and c["file"] != genre:
                continue
            out.append(c)
        return out

    def matches_allowlist_term(self, start: int, end: int, full_text: str) -> bool:
        """True if the match overlaps any known-allowlisted term.

        Only a hint: the semantic-triage step decides. See class docstring.
        """
        n = len(full_text)
        for term in self.allowlist:
            term_len = len(term)
            for p in range(max(0, start - term_len + 1), min(end, n - term_len + 1)):
                if full_text[p:p + term_len] == term:
                    return True
        return False


def load_patterns(data_dir: Path | None = None, allowlist_file: Path | None = None) -> PatternSet:
    data_dir = data_dir or _DEFAULT_DATA_DIR
    allowlist_file = allowlist_file or (data_dir / "allowlist.json")
    return PatternSet.load(data_dir, allowlist_file)


# ── Markup stripping ─────────────────────────────────────────────────

def strip_typst_markup(text: str) -> str:
    """Crude Typst markup stripper — removes directives, headings, code blocks."""
    text = re.sub(r"#\w+\([^)]*\)", "", text)
    text = re.sub(r"#\w+\[[^\]]*\]", "", text)
    text = re.sub(r"^=+\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"#figure\(.*?\)", "", text, flags=re.DOTALL)
    text = re.sub(r"#table\(.*?\)", "", text, flags=re.DOTALL)
    return text


def split_sentences(text: str) -> list[str]:
    sentences = re.split(r"[。！？\n]", text)
    return [s.strip() for s in sentences if s.strip() and len(s.strip()) > 2]


def count_patterns(text: str, patterns: list[str]) -> dict[str, int]:
    counts = {}
    for p in patterns:
        c = text.count(p)
        if c > 0:
            counts[p] = c
    return counts


# ── Hit collection (with whitelist + position, for the ledger) ───────

def collect_hits(text: str, ps: PatternSet | None = None, genre: str | None = None) -> list[dict]:
    """Return per-instance CANDIDATE rows with context, for semantic triage.

    The scanner makes NO final judgment — it cannot know every domain's专有
    名词. It extracts each match plus a context window and a allowlist_hint,
    and leaves the 保留/修复 decision to the semantic-triage step (the model)
    in the SKILL/protocol, then to human review where confidence is low.

    Each row: {category, type, pattern, snippet, line, char,
               context_before, context_after, allowlist_hint}.
    """
    ps = ps or load_patterns()
    hits: list[dict] = []
    lines = text.splitlines()

    def locate(offset: int) -> tuple[int, int]:
        consumed = 0
        for idx, ln in enumerate(lines, 1):
            if consumed + len(ln) + 1 > offset:
                return idx, offset - consumed + 1
            consumed += len(ln) + 1
        return len(lines), max(1, offset - consumed + 1)

    def add(cat_label: str, type_name: str, pattern: str, matches: list[tuple[str, int]]):
        seen = set()
        for raw, pos in matches:
            if pos in seen:
                continue
            seen.add(pos)
            line, char = locate(pos)
            snippet = raw if len(raw) <= 40 else raw[:40] + "…"
            # context window: W chars before and after, clipped to line-ish span
            w = 18
            before = text[max(0, pos - w):pos].replace("\n", " ")
            after = text[pos + len(raw):pos + len(raw) + w].replace("\n", " ")
            hits.append({
                "category": cat_label,
                "type": type_name,
                "pattern": pattern,
                "snippet": snippet,
                "line": line,
                "char": char,
                "context_before": before,
                "context_after": after,
                "allowlist_hint": ps.matches_allowlist_term(pos, pos + len(raw), text),
            })

    for c in ps.enabled_categories(genre):
        level = c.get("level", "Must-fix")
        ptype = c["id"]
        kind = c.get("kind", "literal")
        items = c.get("items", [])

        if kind == "pairs":
            for a, b in items:
                matches = [(m.group(0), m.start()) for m in re.finditer(re.escape(a), text)]
                add(level, ptype, f"{a}->{b}", matches)
            continue

        for p in items:
            if kind == "regex":
                matches = [(m.group(0), m.start()) for m in re.finditer(p, text)]
            else:
                matches = [(m.group(0), m.start()) for m in re.finditer(re.escape(p), text)]
            add(level, ptype, p, matches)

    hits.sort(key=lambda h: (h["line"], h["char"]))
    return hits


def write_hits_csv(hits: list[dict], out: str) -> None:
    with open(out, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "category", "type", "pattern", "snippet", "line", "char",
                "context_before", "context_after", "allowlist_hint",
            ],
        )
        writer.writeheader()
        writer.writerows(hits)


def residual_hits(original_text: str, edited_text: str, ps: PatternSet | None = None) -> list[dict]:
    """Hits still present in edited text. Residuals = fixes dropped or never applied."""
    return collect_hits(edited_text, ps)


# ── Chunking (for subagent fan-out planning) ─────────────────────────

def chunk_lines(text: str, target: int = 800) -> list[tuple[int, int]]:
    """Return (start_line, end_line) ranges of roughly `target` chars each."""
    lines = text.splitlines()
    ranges: list[tuple[int, int]] = []
    start = 0
    cur_chars = 0
    for i, ln in enumerate(lines, 1):
        cur_chars += len(ln) + 1
        if cur_chars < target:
            continue
        if i == len(lines) or (lines[i - 1] == "" and cur_chars - len(ln) >= target * 0.6):
            ranges.append((start, i))
            start = i
            cur_chars = 0
    if start < len(lines):
        ranges.append((start, len(lines)))
    return ranges


# ── Summary report ───────────────────────────────────────────────────

def analyze_file(filepath: str, ps: PatternSet | None = None, genre: str | None = None) -> dict:
    """Run full analysis on a file. Returns a report dict."""
    ps = ps or load_patterns()
    path = Path(filepath)
    raw = path.read_text(encoding="utf-8")
    text = strip_typst_markup(raw) if path.suffix == ".typ" else raw

    sentences = split_sentences(text)
    total_chars = len(text)
    total_sentences = len(sentences)
    if total_sentences == 0:
        return {"error": "No sentences found."}

    sent_lengths = [len(s) for s in sentences]
    avg_len = sum(sent_lengths) / len(sent_lengths)
    max_len = max(sent_lengths)
    min_len = min(sent_lengths)

    # Per-category counts (whitelist-aware, derived from the same hits the ledger uses)
    flags = {}
    for hit in collect_hits(text, ps, genre):
        label = hit["type"]
        flags.setdefault(label, {})
        flags[label][hit["pattern"]] = flags[label].get(hit["pattern"], 0) + 1

    structural = ps.structural or {}
    em_dash_syms = structural.get("em_dash_symbols", ["——", "—"])
    colon_syms = structural.get("colon_symbols", ["："])
    em_dash_count = sum(text.count(s) for s in em_dash_syms)
    colon_count = sum(text.count(s) for s in colon_syms)
    le_count = text.count("了")

    enum_hits = []
    for marker in (flags_keys := _enum_markers(ps)) or []:
        pattern = rf"(?:[。：]|^|\n)\s*{marker}[，、,]"
        matches = re.findall(pattern, text, re.MULTILINE)
        if matches:
            enum_hits.append((marker, len(matches)))

    total_red_flags = sum(sum(v.values()) if isinstance(v, dict) else v for v in flags.values())
    flag_density = total_red_flags / (total_chars / 100) if total_chars > 0 else 0

    ratio = max_len / max(min_len, 1) if max_len and min_len else 1
    variance_score = min(10, ratio * 2)
    em_dash_density = em_dash_count / (total_chars / 1000) if total_chars > 0 else 0
    colon_density = colon_count / (total_chars / 100) if total_chars > 0 else 0
    em_dash_score = max(0, 10 - em_dash_density * 5)
    colon_score = max(0, 10 - colon_density * 7)

    ai_index = (
        min(50, flag_density * 15)
        + min(25, max(0, (10 - variance_score) * 2.5))
        + min(15, max(0, (10 - em_dash_score) * 1.5))
        + min(10, max(0, (10 - colon_score) * 1.0))
    )

    return {
        "file": filepath,
        "total_chars": total_chars,
        "total_sentences": total_sentences,
        "sent_lengths": {
            "avg": round(avg_len, 1), "max": max_len, "min": min_len,
            "ratio": round(ratio, 1),
        },
        "flags": flags,
        "structural": {
            "em_dash_count": em_dash_count,
            "em_dash_per_1000": round(em_dash_density, 1),
            "colon_count": colon_count,
            "colon_per_100": round(colon_density, 1),
            "le_sentence_ends": le_count,
            "enumeration_markers": enum_hits,
        },
        "scores": {
            "variance": round(variance_score, 1),
            "em_dash": round(em_dash_score, 1),
            "colon": round(colon_score, 1),
        },
        "ai_index": round(ai_index, 1),
        "verdict": (
            "[OK] Clean — low AI signal" if ai_index < 20
            else "[~] Mild — some AI patterns present" if ai_index < 40
            else "[!] Heavy — significant AI patterns detected"
        ),
    }


def _enum_markers(ps: PatternSet) -> list[str]:
    for c in ps.categories:
        if c.get("id") == "enum":
            return c.get("items", []) or []
    return ["首先", "其次", "第三", "第四", "最后", "第一", "第二"]


def print_report(report: dict) -> None:
    if "error" in report:
        print(f"Error: {report['error']}")
        return
    print(f"\n{'='*60}")
    print(f"  AI Pattern Detection Report")
    print(f"  File: {report['file']}")
    print(f"  Characters: {report['total_chars']} | Sentences: {report['total_sentences']}")
    print(f"{'='*60}")

    print(f"\n── Sentence Rhythm ──")
    sl = report["sent_lengths"]
    print(f"  Avg {sl['avg']} | Range {sl['min']}-{sl['max']} | Ratio {sl['ratio']}:1")
    print(f"  Score: {report['scores']['variance']}/10")

    print(f"\n── Structural Markers ──")
    st = report["structural"]
    print(f"  Em-dashes: {st['em_dash_count']} ({st['em_dash_per_1000']}/1000)  Score: {report['scores']['em_dash']}/10")
    print(f"  Colons: {st['colon_count']} ({st['colon_per_100']}/100)  Score: {report['scores']['colon']}/10")
    print(f"  Enumeration markers: {st['enumeration_markers'] or 'none'}")

    print(f"\n── Flagged Patterns ──")
    total = 0
    for label, items in report["flags"].items():
        if not items:
            continue
        n = sum(items.values()) if isinstance(items, dict) else items
        total += n if isinstance(n, int) else 0
        print(f"  [{label}] ({n} hits)")
        if isinstance(items, dict):
            for pattern, count in sorted(items.items(), key=lambda x: -x[1]):
                print(f"    - {pattern[:44]}: {count}")

    print(f"\n── Overall ──")
    print(f"  AI Flavor Index: {report['ai_index']}/100  ({report['verdict']})")
    print(f"  Total flags: {total}\n")


def _parse_data_args(args: list[str]):
    """Extract --data/--allowlist overrides; returns (cleaned_args, data_dir, allowlist)."""
    data_dir = None
    allowlist = None
    out = []
    i = 0
    while i < len(args):
        if args[i] == "--data" and i + 1 < len(args):
            data_dir = Path(args[i + 1]); i += 2; continue
        if args[i] == "--allowlist" and i + 1 < len(args):
            allowlist = Path(args[i + 1]); i += 2; continue
        out.append(args[i]); i += 1
    return out, data_dir, allowlist


if __name__ == "__main__":
    args, data_dir, allowlist = _parse_data_args(sys.argv[1:])
    ps = load_patterns(data_dir, allowlist)

    if args[0:1] == ["--triage"]:
        # Emit candidates with context for SEMANTIC triage by the model (or human).
        # The scanner never decides 保留/修复 — it gives context and a hint.
        if len(args) < 2:
            print("Usage: python detect.py --triage <file> [out.csv]"); sys.exit(1)
        path = Path(args[1])
        if not path.exists():
            print(f"File not found: {path}"); sys.exit(1)
        text = path.read_text(encoding="utf-8")
        if path.suffix == ".typ":
            text = strip_typst_markup(text)
        hits = collect_hits(text, ps)
        out = args[2] if len(args) > 2 else (path.stem + "_triage.csv")
        write_hits_csv(hits, out)
        hinted = sum(1 for h in hits if h["allowlist_hint"])
        print(f"Wrote {len(hits)} candidates to {out} ({hinted} flagged with allowlist_hint, review these via semantics)")
        sys.exit(0)

    if args[0:1] == ["--hits"]:
        if len(args) < 2:
            print("Usage: python detect.py --hits <file> [out.csv]"); sys.exit(1)
        path = Path(args[1])
        if not path.exists():
            print(f"File not found: {path}"); sys.exit(1)
        text = path.read_text(encoding="utf-8")
        if path.suffix == ".typ":
            text = strip_typst_markup(text)
        hits = collect_hits(text, ps)
        out = args[2] if len(args) > 2 else (path.stem + "_hits.csv")
        write_hits_csv(hits, out)
        print(f"Wrote {len(hits)} hit rows to {out}")
        sys.exit(0)

    if args[0:1] == ["--residual"]:
        if len(args) < 3:
            print("Usage: python detect.py --residual <original> <edited> [out.csv]"); sys.exit(1)
        orig, edit = Path(args[1]), Path(args[2])
        if not orig.exists() or not edit.exists():
            print("Both files must exist."); sys.exit(1)
        hits = residual_hits(orig.read_text(encoding="utf-8"), edit.read_text(encoding="utf-8"), ps)
        out = args[3] if len(args) > 3 else (edit.stem + "_residual_hits.csv")
        write_hits_csv(hits, out)
        print(f"Residual hits remaining in edited text: {len(hits)} -> {out}")
        sys.exit(0)

    if args[0:1] == ["--chunks"]:
        if len(args) < 2:
            print("Usage: python detect.py --chunks <file> [target_chars]"); sys.exit(1)
        path = Path(args[1])
        if not path.exists():
            print(f"File not found: {path}"); sys.exit(1)
        target = int(args[2]) if len(args) > 2 else 800
        for i, (a, b) in enumerate(chunk_lines(path.read_text(encoding="utf-8"), target), 1):
            print(f"chunk_{i:02d} lines {a + 1}..{b}")
        sys.exit(0)

    if len(args) < 1:
        print("Usage: python detect.py <file>"); sys.exit(1)

    filepath = args[0]
    if not Path(filepath).exists():
        print(f"File not found: {filepath}"); sys.exit(1)
    report = analyze_file(filepath, ps)
    print_report(report)
