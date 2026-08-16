#!/usr/bin/env python3
"""Read-only inventory for a LaTeX paper project."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable


IGNORED_DIRS = {".git", ".hg", ".svn", "build", "dist", "out", "node_modules", "__pycache__"}
ARCHIVE_PREFIXES = ("archive", "old_version", "old-version")
ENCODINGS = ("utf-8-sig", "utf-8", "gb18030", "latin-1")

COMMAND_PATTERNS = {
    "labels": re.compile(r"\\label\s*\{([^{}]+)\}"),
    "references": re.compile(r"\\(?:ref|eqref|autoref|cref|Cref)\s*\{([^{}]+)\}"),
    "citations": re.compile(
        r"\\(?:cite|citep|citet|citealp|citeauthor|citeyear|parencite|textcite|autocite|footcite|supercite|nocite)"
        r"\s*(?:\[[^\]]*\]\s*)*\{([^{}]+)\}"
    ),
    "inputs": re.compile(r"\\(?:input|include)\s*\{([^{}]+)\}"),
    "bibliographies": re.compile(r"\\(?:bibliography|addbibresource)\s*\{([^{}]+)\}"),
    "graphics": re.compile(r"\\includegraphics\s*(?:\[[^\]]*\]\s*)?\{([^{}]+)\}"),
}

COUNT_PATTERNS = {
    "sections": re.compile(r"\\(?:part|chapter|section|subsection|subsubsection)\*?\s*\{"),
    "figures": re.compile(r"\\begin\s*\{figure\*?\}"),
    "tables": re.compile(r"\\begin\s*\{table\*?\}"),
    "equation_blocks": re.compile(r"\\begin\s*\{(?:equation\*?|align\*?|gather\*?|multline\*?)\}"),
    "algorithms": re.compile(r"\\begin\s*\{algorithm\*?\}"),
}


def strip_comments(text: str) -> str:
    lines: list[str] = []
    for line in text.splitlines():
        escaped = False
        kept: list[str] = []
        for char in line:
            if char == "%" and not escaped:
                break
            kept.append(char)
            if char == "\\":
                escaped = not escaped
            else:
                escaped = False
        lines.append("".join(kept))
    return "\n".join(lines)


def read_tex(path: Path) -> tuple[str, str]:
    data = path.read_bytes()
    for encoding in ENCODINGS:
        try:
            return data.decode(encoding), encoding
        except UnicodeDecodeError:
            continue
    raise UnicodeError(f"Unable to decode {path}")


def is_ignored(path: Path, root: Path) -> bool:
    try:
        parts = path.relative_to(root).parts[:-1]
    except ValueError:
        return False
    return any(part in IGNORED_DIRS or part.lower().startswith(ARCHIVE_PREFIXES) for part in parts)


def discover_tex_files(source: Path) -> tuple[Path, list[Path]]:
    source = source.resolve()
    if source.is_file():
        if source.suffix.lower() != ".tex":
            raise ValueError(f"Expected a .tex file: {source}")
        return source.parent, [source]
    if not source.is_dir():
        raise FileNotFoundError(source)
    files = sorted(path for path in source.rglob("*.tex") if not is_ignored(path, source))
    return source, files


def split_values(values: Iterable[str]) -> list[str]:
    output: list[str] = []
    for value in values:
        output.extend(item.strip() for item in value.split(",") if item.strip())
    return output


def dependency_exists(base: Path, value: str, extensions: tuple[str, ...]) -> bool | None:
    if "\\" in value or "#" in value:
        return None
    candidate = base / value
    if candidate.suffix:
        return candidate.exists()
    return any(candidate.with_suffix(extension).exists() for extension in extensions)


def inventory(source: Path) -> dict:
    root, tex_files = discover_tex_files(source)
    file_reports: list[dict] = []
    included_tex: set[str] = set()

    for path in tex_files:
        raw, encoding = read_tex(path)
        text = strip_comments(raw)
        commands = {
            key: split_values(pattern.findall(text))
            for key, pattern in COMMAND_PATTERNS.items()
        }
        included_tex.update(Path(value).with_suffix("").as_posix() for value in commands["inputs"])
        dependencies: list[dict] = []
        for value in commands["inputs"]:
            dependencies.append({"kind": "tex", "value": value, "exists": dependency_exists(path.parent, value, (".tex",))})
        for value in commands["bibliographies"]:
            dependencies.append({"kind": "bibliography", "value": value, "exists": dependency_exists(path.parent, value, (".bib",))})
        for value in commands["graphics"]:
            dependencies.append(
                {
                    "kind": "graphic",
                    "value": value,
                    "exists": dependency_exists(path.parent, value, (".pdf", ".png", ".jpg", ".jpeg", ".eps", ".svg")),
                }
            )

        file_reports.append(
            {
                "path": path.relative_to(root).as_posix(),
                "encoding": encoding,
                "bytes": path.stat().st_size,
                "is_document": bool(re.search(r"\\documentclass(?:\[[^\]]*\])?\s*\{", text)),
                "has_begin_document": bool(re.search(r"\\begin\s*\{document\}", text)),
                "counts": {key: len(pattern.findall(text)) for key, pattern in COUNT_PATTERNS.items()},
                "anchors": {
                    "labels": len(commands["labels"]),
                    "references": len(commands["references"]),
                    "citation_keys": len(commands["citations"]),
                },
                "dependencies": dependencies,
            }
        )

    roots = [report["path"] for report in file_reports if report["is_document"] or report["has_begin_document"]]
    if not roots:
        roots = [
            report["path"]
            for report in file_reports
            if Path(report["path"]).with_suffix("").as_posix() not in included_tex
        ]

    aggregate = Counter()
    for report in file_reports:
        aggregate.update(report["counts"])
        aggregate.update(report["anchors"])

    missing = [
        {"file": report["path"], **dependency}
        for report in file_reports
        for dependency in report["dependencies"]
        if dependency["exists"] is False
    ]
    return {
        "source": str(source.resolve()),
        "project_root": str(root),
        "tex_file_count": len(file_reports),
        "root_candidates": roots,
        "aggregate_counts": dict(sorted(aggregate.items())),
        "missing_dependencies": missing,
        "files": file_reports,
    }


def render_text(report: dict) -> str:
    lines = [
        f"Project: {report['project_root']}",
        f"TeX files: {report['tex_file_count']}",
        "Root candidates: " + (", ".join(report["root_candidates"]) or "none"),
        "Counts: " + ", ".join(f"{key}={value}" for key, value in report["aggregate_counts"].items()),
    ]
    if report["missing_dependencies"]:
        lines.append("Missing dependencies:")
        lines.extend(
            f"  - {item['file']}: {item['kind']} {item['value']}"
            for item in report["missing_dependencies"]
        )
    else:
        lines.append("Missing dependencies: none detected")
    return "\n".join(lines)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="LaTeX root file or project directory")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        report = inventory(args.source)
    except (FileNotFoundError, ValueError, UnicodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2) if args.json else render_text(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
