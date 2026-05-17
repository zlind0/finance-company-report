#!/usr/bin/env python3
"""Extract profitability, strategy, risk, and competition evidence from Intel SEC filings."""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
import csv
import re

from bs4 import BeautifulSoup


BASE_DIR = Path(__file__).resolve().parent.parent / "raw_reports"
OUT_PATH = Path(__file__).resolve().parent.parent / "intc_extracted.txt"
SUMMARY_CSV = Path(__file__).resolve().parent.parent / "intc_filing_summary.csv"

CONTEXT_WINDOW = 4
MAX_LINES_PER_CATEGORY = 180

KEYWORDS = {
    "revenue_profitability": [
        "revenue",
        "net revenue",
        "gross margin",
        "gross profit",
        "operating income",
        "operating loss",
        "net income",
        "net loss",
        "earnings per share",
        "diluted eps",
        "non-gaap",
        "profitability",
        "margin",
    ],
    "segment_mix": [
        "client computing group",
        "ccg",
        "data center",
        "dcaI",
        "datacenter",
        "network and edge",
        "nex",
        "intel foundry",
        "all other",
        "mobileye",
        "altera",
        "programmable solutions",
        "internet of things",
        "iot",
        "segment",
    ],
    "cost_and_cash": [
        "cost of sales",
        "cost of revenue",
        "research and development",
        "marketing, general and administrative",
        "restructuring",
        "impairment",
        "inventory",
        "cash flow",
        "capital expenditures",
        "capex",
        "liquidity",
        "capital resources",
        "depreciation",
        "amortization",
        "free cash flow",
    ],
    "strategy_execution": [
        "strategy",
        "idM 2.0",
        "idm 2.0",
        "five nodes in four years",
        "18a",
        "20a",
        "angstrom",
        "packaging",
        "advanced packaging",
        "euV",
        "ecosystem",
        "roadmap",
        "execution",
        "launch",
        "product leadership",
        "ai pc",
        "gaudi",
        "core ultra",
        "granite rapids",
        "sierra forest",
        "lunar lake",
    ],
    "competition": [
        "competition",
        "competitive",
        "amd",
        "nvidia",
        "qualcomm",
        "arm",
        "apple",
        "tsmc",
        "samsung",
        "broadcom",
        "marvell",
        "market share",
        "pricing pressure",
    ],
    "risk_factors": [
        "risk factor",
        "risk factors",
        "geopolitical",
        "china",
        "export control",
        "supply chain",
        "cybersecurity",
        "litigation",
        "regulation",
        "tariff",
        "macro",
        "inflation",
        "interest rate",
        "customer concentration",
        "execution risk",
    ],
}

SECTION_HINTS = [
    "management's discussion and analysis",
    "results of operations",
    "liquidity and capital resources",
    "risk factors",
    "business",
    "overview",
]


def filing_sort_key(name: str) -> str:
    return name.split("_", 1)[1].replace(".html", "")


def filing_label(name: str) -> str:
    form_type, filing_date = name.replace(".html", "").split("_", 1)
    if form_type == "10-K":
        return f"FY{int(filing_date[:4]) - 1} Annual (10-K filed {filing_date})"
    return f"Quarterly (10-Q filed {filing_date})"


def clean_lines(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8", errors="ignore") as handle:
        soup = BeautifulSoup(handle.read(), "html.parser")

    for tag in soup(["script", "style"]):
        tag.decompose()

    text = soup.get_text(separator="\n", strip=True)
    raw_lines = [line.strip() for line in text.split("\n")]
    lines = []
    for line in raw_lines:
        if not line:
            continue
        # Compress extreme whitespace while preserving sentence text.
        compact = re.sub(r"\s+", " ", line)
        if compact:
            lines.append(compact)
    return lines


def collect_category_indices(lines: list[str]) -> tuple[dict[str, set[int]], set[int]]:
    per_category: dict[str, set[int]] = {key: set() for key in KEYWORDS}
    global_indices: set[int] = set()

    for i, line in enumerate(lines):
        lower_line = line.lower()
        for category, words in KEYWORDS.items():
            if any(word.lower() in lower_line for word in words):
                start = max(0, i - CONTEXT_WINDOW)
                end = min(len(lines), i + CONTEXT_WINDOW + 1)
                indices = set(range(start, end))
                per_category[category].update(indices)
                global_indices.update(indices)

    return per_category, global_indices


def collect_section_highlights(lines: list[str], max_take: int = 45) -> list[str]:
    highlights: list[str] = []
    lowered = [line.lower() for line in lines]

    for hint in SECTION_HINTS:
        for idx, lower_line in enumerate(lowered):
            if hint in lower_line:
                start = idx
                end = min(len(lines), idx + max_take)
                block = lines[start:end]
                highlights.append(f"[SECTION:{hint}]")
                highlights.extend(block)
                highlights.append("...")
                break

    # Deduplicate while preserving order.
    seen = set()
    deduped: list[str] = []
    for item in highlights:
        if item in seen:
            continue
        seen.add(item)
        deduped.append(item)
    return deduped


def render_indices(lines: list[str], indices: set[int], cap: int) -> list[str]:
    selected = sorted(indices)
    output: list[str] = []
    prev = -1
    for idx in selected[:cap]:
        if prev >= 0 and idx > prev + 1:
            output.append("...")
        output.append(lines[idx])
        prev = idx
    if len(selected) > cap:
        output.append(f"[... truncated, {len(selected) - cap} more lines ...]")
    return output


def main() -> None:
    all_files = sorted([p for p in BASE_DIR.iterdir() if p.suffix == ".html"], key=lambda p: filing_sort_key(p.name))

    summary_rows = []
    with OUT_PATH.open("w", encoding="utf-8") as out:
        for path in all_files:
            lines = clean_lines(path)
            per_category_indices, global_indices = collect_category_indices(lines)
            section_highlights = collect_section_highlights(lines)

            separator = "=" * 100
            out.write("\n" + separator + "\n")
            out.write(f"FILE: {filing_label(path.name)}\n")
            out.write(f"FILENAME: {path.name}\n")
            out.write(f"PATH: {path}\n")
            out.write(separator + "\n")

            counts = Counter({category: len(indices) for category, indices in per_category_indices.items()})
            out.write("CATEGORY_COUNTS:\n")
            for category, count in counts.most_common():
                out.write(f"- {category}: {count}\n")
            out.write(f"- total_unique_matched_lines: {len(global_indices)}\n")
            out.write(f"- total_document_lines: {len(lines)}\n")

            out.write("\nKEY_SECTION_HIGHLIGHTS:\n")
            for item in section_highlights[:280]:
                out.write(item + "\n")

            for category in KEYWORDS:
                out.write(f"\n[{category}]\n")
                excerpt = render_indices(lines, per_category_indices[category], MAX_LINES_PER_CATEGORY)
                for line in excerpt:
                    out.write(line + "\n")

            out.write("\n[GLOBAL_MATCHED_EXCERPT]\n")
            global_excerpt = render_indices(lines, global_indices, cap=420)
            for line in global_excerpt:
                out.write(line + "\n")

            summary_rows.append(
                {
                    "filename": path.name,
                    "filing_label": filing_label(path.name),
                    "form": path.name.split("_", 1)[0],
                    "filing_date": path.name.split("_", 1)[1].replace(".html", ""),
                    "document_lines": len(lines),
                    "matched_unique_lines": len(global_indices),
                    **{f"cnt_{category}": len(indices) for category, indices in per_category_indices.items()},
                }
            )

    if summary_rows:
        fieldnames = list(summary_rows[0].keys())
        with SUMMARY_CSV.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(summary_rows)

    print(f"Done. Extracted {len(all_files)} filings to {OUT_PATH}")
    print(f"Summary CSV written to {SUMMARY_CSV}")


if __name__ == "__main__":
    main()
