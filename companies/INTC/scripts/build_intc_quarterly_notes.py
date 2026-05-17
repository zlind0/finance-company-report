#!/usr/bin/env python3
"""Build per-filing quarterly notes for Intel from SEC filing text."""

from __future__ import annotations

from pathlib import Path
import re

from bs4 import BeautifulSoup


BASE_DIR = Path(__file__).resolve().parent.parent / "raw_reports"
OUT_PATH = Path(__file__).resolve().parent.parent / "intc_quarterly_notes.md"


TOPIC_PATTERNS = {
    "盈利逻辑线索": [
        r"net revenue",
        r"gross margin",
        r"operating income",
        r"operating loss",
        r"net income",
        r"net loss",
        r"pricing",
        r"mix",
        r"demand",
        r"segment",
    ],
    "利润改善动作": [
        r"cost reduction",
        r"restructuring",
        r"efficiency",
        r"productivity",
        r"optimization",
        r"yield",
        r"node",
        r"euV",
        r"roadmap",
        r"capital allocation",
        r"share repurchase",
    ],
    "新增或上升风险": [
        r"risk factor",
        r"geopolitical",
        r"china",
        r"competition",
        r"market share",
        r"litigation",
        r"supply chain",
        r"customer concentration",
        r"export control",
        r"execution risk",
    ],
    "战略变化与竞争关系": [
        r"strategy",
        r"idM 2\.0",
        r"foundry",
        r"ai pc",
        r"data center",
        r"advanced packaging",
        r"amd",
        r"nvidia",
        r"tsmc",
        r"samsung",
        r"qualcomm",
        r"arm",
    ],
}


def sort_key(name: str) -> str:
    return name.split("_", 1)[1].replace(".html", "")


def load_lines(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8", errors="ignore") as handle:
        soup = BeautifulSoup(handle.read(), "html.parser")

    for tag in soup(["script", "style"]):
        tag.decompose()

    text = soup.get_text(separator="\n", strip=True)
    lines = []
    for raw in text.split("\n"):
        line = re.sub(r"\s+", " ", raw.strip())
        if line:
            lines.append(line)
    return lines


def pick_lines(lines: list[str], patterns: list[str], limit: int = 4) -> list[str]:
    picked: list[str] = []
    seen = set()
    compiled = [re.compile(pat, flags=re.IGNORECASE) for pat in patterns]

    for idx, line in enumerate(lines):
        if len(line) < 25:
            continue
        if len(line) > 280:
            continue
        if not any(regex.search(line) for regex in compiled):
            continue

        normalized = line.lower()
        if normalized in seen:
            continue
        seen.add(normalized)

        # Include one line before/after for minimal context when possible.
        context = [line]
        if idx > 0 and 20 <= len(lines[idx - 1]) <= 160:
            context.insert(0, lines[idx - 1])
        if idx + 1 < len(lines) and 20 <= len(lines[idx + 1]) <= 180:
            context.append(lines[idx + 1])

        merged = " | ".join(context)
        if merged.lower() in seen:
            continue
        picked.append(merged)
        if len(picked) >= limit:
            break

    return picked


def filing_title(name: str) -> str:
    form, date = name.replace(".html", "").split("_", 1)
    return f"{form} filed {date}"


def build_notes() -> None:
    files = sorted([p for p in BASE_DIR.iterdir() if p.suffix == ".html"], key=lambda p: sort_key(p.name))

    lines_out = [
        "# INTC 季度与年度财报逐份要点索引",
        "",
        "- 样本范围：companies/INTC/raw_reports 下全部 10-Q 与 10-K",
        f"- 文件总数：{len(files)}",
        "- 用途：为深度研报提供逐份证据回溯，避免遗漏单季度逻辑变化",
        "",
    ]

    for file_path in files:
        lines = load_lines(file_path)
        lines_out.append(f"## {filing_title(file_path.name)}")
        lines_out.append(f"- 文本行数（清洗后）：{len(lines)}")

        for topic, patterns in TOPIC_PATTERNS.items():
            lines_out.append(f"### {topic}")
            picks = pick_lines(lines, patterns, limit=5)
            if not picks:
                lines_out.append("- 未检索到明确句子，建议人工复核原文。")
            else:
                for item in picks:
                    # Escape dollar sign to avoid markdown math conflicts.
                    safe_item = item.replace("$", "\\$")
                    lines_out.append(f"- {safe_item}")
            lines_out.append("")

    OUT_PATH.write_text("\n".join(lines_out), encoding="utf-8")
    print(f"Done. Wrote filing notes to {OUT_PATH}")


if __name__ == "__main__":
    build_notes()
