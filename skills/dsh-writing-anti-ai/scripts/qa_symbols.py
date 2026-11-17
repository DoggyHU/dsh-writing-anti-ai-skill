# -*- coding: utf-8 -*-
"""qa_symbols.py — 交付前符号硬门。

用途：在改写完成后，对全文做一次「零容忍」符号扫描。任何方向的箭头、状态 emoji、
勾叉、角括号都必须为零；装饰符号（✦ ★ ◆ 等版式用）单列为提醒，不阻断。

为什么单独成一个脚本：SKILL 里的 detect.py 是"扫描 + 打分"，它的职责是给改写提供
候选；本脚本的职责是**验收**——一条都不许漏，漏了就不许交稿。两者不要混。

用法：
    python qa_symbols.py <文件或目录> [--json] [--include-code] [--strict]

退出码：发现致命符号 → 1；只有提醒项 → 0；--strict 时提醒项也算失败。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# ---- 箭头：左右上下、斜向、空心、实心、长箭头、双箭头、ASCII 变体 ----
ARROWS = set(
    "→←↑↓↔↕↖↗↘↙↚↛↜↝↞↟↠↡↢↣↤↥↦↧↨↩↪↫↬↭↮↯↰↱↲↳↴↵↶↷↸↹↺↻↼↽↾↿⇀⇁⇂⇃⇄⇅⇆⇇⇈⇉⇊⇋⇌⇍⇎⇏"
    "⇐⇑⇒⇓⇔⇕⇖⇗⇘⇙⇚⇛⇜⇝⇞⇟⇠⇡⇢⇣⇤⇥⇦⇧⇨⇩⇪⇫⇬⇭⇮⇯⇰⇱⇲⇳⇴⇵⇶⇷⇸⇹⇺⇻⇼⇽⇾⇿"
    "➔➜➝➞➟➠➡➢➣➤➥➦➧➨➩➪➫➬➭➮➯➱➲➳➴➵➶➷➸➹➺➻➼➽➾⟰⟱⟵⟶⟷⟸⟹⟺⟻⟼⟽⟾⟿"
    "⤀⤁⤂⤃⤄⤅⤆⤇⤈⤉⤊⤋⤌⤍⤎⤏⤐⤑⤒⤓⤔⤕⤖⤗⤘⤙⤚⤛⤜⤝⤞⤟⤠⤡⤢⤣⤤⤥⤦⤧⤨⤩⤪⤫⤬⤭⤮⤯"
    "⤰⤱⤲⤳⤴⤵⤶⤷⤸⤹⤺⤻⤼⤽⤾⤿⥀⥁⥂⥃⥄⥅⥆⥇⥈⥉⭅⭆⮕⬀⬁⬂⬃⬄⬅⬆⬇⬈⬉⬊⬋⬌⬍"
    "🡐🡑🡒🡓🡔🡕🡖🡗🡘🡙🡚🡛🡜🡝🡞🡟🡠🡡🡢🡣🡤🡥🡦🡧🡨🡩🡪🡫🡬🡭🡮🡯🡰🡱🡲🡳🡴🡵🡶🡷🡸🡹🡺🡻🡼🡽🡾🡿"
)

# ASCII 箭头：仅在正文里算，代码块内不算
ASCII_ARROW_RE = re.compile(r"(?:-{1,2}>|<{1,2}-|=+>|<+=|=>|<=|←→|→←)")
# 但 "=>"/"<=" 也常出现在代码里；代码块默认被剔除。

STATUS_EMOJI = set("✅❌⚠️⚠🔴🟠🟡🟢🔵🟣⚫⚪⭐🌟💡📌🔔")
CHECK_MARKS = set("✔✓√✖✗✘△▲")
# × 是歧义符号：作判定标记要改，作乘号（3000元/㎡ × 面积）是真排版。
# 全判死会让带乘号的稿子永远过不了门，于是单列一档：默认只提醒，--strict 才判失败。
AMBIG = set("×")
CORNER = set("「」『』")
# 装饰/版式符号：提醒级，不算致命（用户没要求清零）
DECOR = set("✦✧★☆◆◇■□●○▲▼▽▪▫◼◻◾◽")

FENCE_RE = re.compile(r"```.*?```", re.S)
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")


def strip_code(text: str) -> str:
    text = FENCE_RE.sub(lambda m: "\n" * m.group(0).count("\n"), text)
    return INLINE_CODE_RE.sub(lambda m: " " * len(m.group(0)), text)


def scan(path: Path, include_code: bool = False) -> dict:
    raw = path.read_text(encoding="utf-8", errors="replace")
    text = raw if include_code else strip_code(raw)
    lines = text.splitlines()

    hits = {"arrow": [], "emoji": [], "check": [], "corner": [], "ambiguous": [], "decor": []}
    for i, line in enumerate(lines, 1):
        for ch in line:
            if ch in ARROWS:
                hits["arrow"].append({"line": i, "char": ch, "text": line.strip()[:120]})
            elif ch in STATUS_EMOJI:
                hits["emoji"].append({"line": i, "char": ch, "text": line.strip()[:120]})
            elif ch in CHECK_MARKS:
                hits["check"].append({"line": i, "char": ch, "text": line.strip()[:120]})
            elif ch in AMBIG:
                hits["ambiguous"].append({"line": i, "char": ch, "text": line.strip()[:120]})
            elif ch in CORNER:
                hits["corner"].append({"line": i, "char": ch, "text": line.strip()[:120]})
            elif ch in DECOR:
                hits["decor"].append({"line": i, "char": ch, "text": line.strip()[:120]})
        for m in ASCII_ARROW_RE.finditer(line):
            hits["arrow"].append({"line": i, "char": m.group(0), "text": line.strip()[:120]})

    total = {k: len(v) for k, v in hits.items()}
    return {"file": str(path), "chars": len(raw), "hits": hits, "counts": total}


def fmt(res: dict) -> str:
    c = res["counts"]
    fatal = c["arrow"] + c["emoji"] + c["check"] + c["corner"]
    out = [f"\n{'='*58}", f"  符号硬门  {Path(res['file']).name}  ({res['chars']} 字符)"]
    out.append(f"{'='*58}")
    names = {"arrow": "箭头（全部方向）", "emoji": "状态 emoji", "check": "勾叉",
             "corner": "角括号「」", "ambiguous": "×（乘号还是判定标记，看语境）",
             "decor": "装饰符号（提醒）"}
    for k in ("arrow", "emoji", "check", "corner", "ambiguous", "decor"):
        out.append(f"  {names[k]}: {c[k]}")
        for h in res["hits"][k][:8]:
            out.append(f"    L{h['line']}  {h['char']}   {h['text']}")
        if c[k] > 8:
            out.append(f"    … 另有 {c[k]-8} 处")
    out.append(f"\n  结论：致命 {fatal} 处 —— " + ("不通过（不许交稿）" if fatal else "通过"))
    if c["ambiguous"]:
        out.append(f"  提醒：{c['ambiguous']} 处 × 需人工确认是乘号（保留）还是判定标记（改成“不符合”）")
    return "\n".join(out)


def main() -> int:
    # 中文 Windows 控制台默认 GBK，撞上箭头/emoji 会 UnicodeEncodeError 直接崩——
    # 偏偏命中时才崩，等于把报告吞掉。强制 UTF-8 输出，编不出来的字符降级成 ?。
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    ap = argparse.ArgumentParser(description="交付前符号硬门：箭头/emoji/勾叉/角括号必须为零")
    ap.add_argument("target", help="文件或目录")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--include-code", action="store_true", help="代码块也扫（默认跳过）")
    ap.add_argument("--strict", action="store_true", help="装饰符号也判失败")
    args = ap.parse_args()

    p = Path(args.target)
    files = [p] if p.is_file() else sorted(
        q for q in p.rglob("*") if q.suffix.lower() in {".md", ".txt", ".html", ".typ"}
    )
    if not files:
        print(f"没有可扫描的文件：{p}")
        return 1

    results = [scan(f, args.include_code) for f in files]
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for r in results:
            print(fmt(r))

    fatal = sum(r["counts"]["arrow"] + r["counts"]["emoji"] + r["counts"]["check"]
                + r["counts"]["corner"] for r in results)
    ambig = sum(r["counts"]["ambiguous"] for r in results)
    decor = sum(r["counts"]["decor"] for r in results)
    if fatal:
        return 1
    if args.strict and (ambig or decor):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
