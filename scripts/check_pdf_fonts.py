#!/usr/bin/env python3
"""Check whether a PDF's CJK fonts are portable across readers."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

try:
    from pypdf import PdfReader
except ImportError as exc:  # pragma: no cover - exercised by CLI environments
    raise SystemExit("pypdf is required: python -m pip install pypdf") from exc


CJK_ORDERINGS = {"GB1", "CNS1", "Japan1", "Korea1"}
CJK_NAME_MARKERS = (
    "cjk",
    "fandol",
    "noto",
    "sourcehan",
    "song",
    "hei",
    "kai",
    "fang",
    "simsun",
    "simhei",
    "simkai",
    "yahei",
    "ming",
)


def resolve(value: Any) -> Any:
    return value.get_object() if hasattr(value, "get_object") else value


def analyze_font(font: Mapping[str, Any]) -> dict[str, Any]:
    descendants = resolve(font.get("/DescendantFonts", []))
    descendant = resolve(descendants[0]) if descendants else {}
    descriptor = {}
    descriptor_ref = descendant.get("/FontDescriptor") or font.get("/FontDescriptor")
    if descriptor_ref:
        descriptor = resolve(descriptor_ref)

    base_font = str(font.get("/BaseFont", ""))
    descendant_base_font = str(descendant.get("/BaseFont", ""))
    ordering = str(resolve(descendant.get("/CIDSystemInfo", {})).get("/Ordering", ""))
    searchable_name = f"{base_font} {descendant_base_font}".lower()
    is_cjk = ordering in CJK_ORDERINGS or any(marker in searchable_name for marker in CJK_NAME_MARKERS)
    embedded = any(descriptor.get(key) for key in ("/FontFile", "/FontFile2", "/FontFile3"))
    has_to_unicode = bool(font.get("/ToUnicode"))

    issues = []
    if is_cjk and not embedded:
        issues.append("cjk-font-not-embedded")
    if is_cjk and not has_to_unicode:
        issues.append("cjk-font-missing-tounicode")

    return {
        "subtype": str(font.get("/Subtype", "")),
        "base_font": base_font,
        "descendant_base_font": descendant_base_font,
        "cid_ordering": ordering,
        "is_cjk": is_cjk,
        "embedded": embedded,
        "to_unicode": has_to_unicode,
        "issues": issues,
    }


def inspect_pdf(path: Path) -> dict[str, Any]:
    reader = PdfReader(path)
    fonts = []
    seen: set[tuple[int, int] | str] = set()
    for page_number, page in enumerate(reader.pages, start=1):
        resources = resolve(page.get("/Resources", {}))
        for resource_name, font_ref in resolve(resources.get("/Font", {})).items():
            key: tuple[int, int] | str
            if hasattr(font_ref, "idnum"):
                key = (font_ref.idnum, font_ref.generation)
            else:
                key = f"direct:{page_number}:{resource_name}"
            if key in seen:
                continue
            seen.add(key)
            result = analyze_font(resolve(font_ref))
            result.update({"first_page": page_number, "resource": str(resource_name)})
            fonts.append(result)

    issues = [
        {"font": font["base_font"], "code": issue, "first_page": font["first_page"]}
        for font in fonts
        for issue in font["issues"]
    ]
    return {
        "pdf": str(path.resolve()),
        "page_count": len(reader.pages),
        "font_count": len(fonts),
        "cjk_font_count": sum(font["is_cjk"] for font in fonts),
        "status": "fail" if issues else "pass",
        "issues": issues,
        "fonts": fonts,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path, help="PDF to inspect")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    report = inspect_pdf(args.pdf)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"{report['status'].upper()}: {report['pdf']}")
        for issue in report["issues"]:
            print(f"- {issue['code']}: {issue['font']} (first page {issue['first_page']})")
    return 1 if report["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
