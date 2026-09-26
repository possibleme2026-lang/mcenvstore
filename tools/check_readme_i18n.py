#!/usr/bin/env python3
"""Bilingual README structure guard.

Compares README.md (English, primary) against README.zh-CN.md (Chinese) on
*structure* only -- never on wording, since the two languages are supposed to
differ. Catches the failure mode that human review always misses: one side
silently loses a whole section, a code block, or a link.

Checks, in order:
  1. heading count + per-level nesting shape
  2. fenced code block count (and that fences are balanced)
  3. table row count per table
  4. outbound link set (bidirectional diff)
  5. every relative link actually exists on disk
  6. cross-links present in both directions (language switch line)

Pure standard library. No dependencies. Runs in CI with no install step.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EN = ROOT / "README.md"
ZH = ROOT / "README.zh-CN.md"

errors: list[str] = []
notes: list[str] = []


def read(path: Path) -> str:
    if not path.exists():
        errors.append(f"missing file: {path.name}")
        return ""
    return path.read_text(encoding="utf-8")


def strip_code_fences(text: str) -> str:
    """Remove fenced code blocks so their contents never pollute structural counts."""
    return re.sub(r"^```.*?^```", "", text, flags=re.S | re.M)


# ---------------------------------------------------------------- 1. headings
HEADING = re.compile(r"^(#{1,6})\s+(.*)$", re.M)


def headings(text: str) -> list[tuple[int, str]]:
    return [(len(m.group(1)), m.group(2).strip()) for m in HEADING.finditer(strip_code_fences(text))]


def check_headings(en: str, zh: str) -> None:
    he, hz = headings(en), headings(zh)
    if len(he) != len(hz):
        errors.append(f"heading count differs: EN={len(he)} ZH={len(hz)}")
        # Show which ones are unmatched to make the fix obvious.
        for i, (lv, title) in enumerate(he):
            if i >= len(hz):
                errors.append(f"  EN-only heading: {'#' * lv} {title}")
        for i, (lv, title) in enumerate(hz):
            if i >= len(he):
                errors.append(f"  ZH-only heading: {'#' * lv} {title}")
    # Nesting shape: the sequence of levels must match, even if titles differ.
    lv_e = [lv for lv, _ in he]
    lv_z = [lv for lv, _ in hz]
    if lv_e != lv_z:
        errors.append(f"heading nesting shape differs:\n    EN={lv_e}\n    ZH={lv_z}")
    elif len(he) == len(hz):
        notes.append(f"headings: {len(he)} each, levels match")


# ------------------------------------------------------------ 2. code fences
FENCE = re.compile(r"^```", re.M)


def check_fences(en_raw: str, zh_raw: str) -> None:
    ne, nz = len(FENCE.findall(en_raw)), len(FENCE.findall(zh_raw))
    for name, n in (("README.md", ne), ("README.zh-CN.md", nz)):
        if n % 2:
            errors.append(f"{name}: unbalanced code fences ({n} markers, expected even)")
    if ne != nz:
        errors.append(f"code fence markers differ: EN={ne} ZH={nz}")
    else:
        notes.append(f"code fences: {ne} markers each")


# ------------------------------------------------------------------ 3. tables
def table_rows(text: str) -> list[int]:
    """Row count for each markdown table, in document order."""
    counts: list[int] = []
    current = 0
    in_table = False
    for line in strip_code_fences(text).splitlines():
        is_row = line.strip().startswith("|") and line.strip().endswith("|")
        if is_row:
            if not in_table:
                in_table = True
                current = 0
            if not re.fullmatch(r"\|[\s:|-]+\|", line.strip()):
                current += 1  # skip the |---|---| separator
        else:
            if in_table:
                counts.append(current)
                in_table = False
    if in_table:
        counts.append(current)
    return counts


def check_tables(en: str, zh: str) -> None:
    te, tz = table_rows(en), table_rows(zh)
    if len(te) != len(tz):
        errors.append(f"table count differs: EN={len(te)} ZH={len(tz)}")
    elif te != tz:
        errors.append(f"table row counts differ: EN={te} ZH={tz}")
    else:
        notes.append(f"tables: {len(te)} each, rows match {te}")


# ------------------------------------------------------------------- 4. links
LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def links(text: str) -> set[str]:
    return {m.group(1).strip() for m in LINK.finditer(strip_code_fences(text))}


def slugify(title: str) -> str:
    """Approximate GitHub's heading -> anchor conversion.

    Mirrors github-slugger: lowercase, trim, drop everything that is not a word
    character / space / hyphen, then replace **each** space with a hyphen.
    Spaces are NOT collapsed, so "Status & known limitations" -> the "&" is
    dropped leaving two spaces -> "status--known-limitations" (two hyphens).

    CJK characters are word characters and are preserved, which is why a Chinese
    heading yields a Chinese anchor -- anchors are language-specific and must be
    validated per-file, never cross-compared.
    """
    s = title.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s, flags=re.UNICODE)
    return s.replace(" ", "-")


def anchors(text: str) -> set[str]:
    return {slugify(title) for _, title in headings(text)}


def check_links(en: str, zh: str) -> None:
    le, lz = links(en), links(zh)

    # Anchors are language-specific -> compare per-file against that file's own headings.
    for name, ls, text in (("README.md", le, en), ("README.zh-CN.md", lz, zh)):
        for target in sorted(x for x in ls if x.startswith("#")):
            if target[1:] not in anchors(text):
                errors.append(f"{name}: anchor {target} does not match any heading")

    # Everything else must match across the two languages.
    def comparable(ls: set[str]) -> set[str]:
        return {x for x in ls if not x.startswith("#") and not x.startswith("README")}

    ce, cz = comparable(le), comparable(lz)
    only_en = ce - cz
    only_zh = cz - ce
    if only_en:
        errors.append(f"links only in EN: {sorted(only_en)}")
    if only_zh:
        errors.append(f"links only in ZH: {sorted(only_zh)}")
    if not only_en and not only_zh:
        n_anchor = len({x for x in le if x.startswith('#')})
        notes.append(f"links: {len(ce)} shared targets, {n_anchor} anchors validated per-file")

    # 5. relative links must resolve on disk
    for target in sorted(le | lz):
        if target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        path = (ROOT / target.split("#", 1)[0]).resolve()
        if not path.exists():
            errors.append(f"dead relative link -> {target}")

    # 6. both files must link to each other (the language switch line)
    if "README.zh-CN.md" not in en:
        errors.append("README.md does not link to README.zh-CN.md")
    if "README.md" not in zh:
        errors.append("README.zh-CN.md does not link to README.md")


# ---------------------------------------------------------------------- main
def main() -> int:
    en_raw, zh_raw = read(EN), read(ZH)
    if errors:
        for e in errors:
            print(f"FAIL  {e}")
        return 1

    check_headings(en_raw, zh_raw)
    check_fences(en_raw, zh_raw)
    check_tables(en_raw, zh_raw)
    check_links(en_raw, zh_raw)

    for n in notes:
        print(f"ok    {n}")

    if errors:
        print()
        for e in errors:
            print(f"FAIL  {e}")
        return 1

    print()
    print("bilingual README structure OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
