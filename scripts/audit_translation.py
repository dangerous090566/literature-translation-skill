#!/usr/bin/env python3
"""Compare structural anchors in source and translated LaTeX."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path


IGNORED_DIRS = {".git", ".hg", ".svn", "build", "dist", "out", "node_modules", "__pycache__"}
ARCHIVE_PREFIXES = ("archive", "old_version", "old-version")
ENCODINGS = ("utf-8-sig", "utf-8", "gb18030", "latin-1")

SET_PATTERNS = {
    "labels": re.compile(r"\\label\s*\{([^{}]+)\}"),
    "reference_targets": re.compile(r"\\(?:ref|eqref|autoref|cref|Cref)\s*\{([^{}]+)\}"),
    "citation_keys": re.compile(
        r"\\(?:cite|citep|citet|citealp|citeauthor|citeyear|parencite|textcite|autocite|footcite|supercite|nocite)"
        r"\s*(?:\[[^\]]*\]\s*)*\{([^{}]+)\}"
    ),
    "included_files": re.compile(r"\\(?:input|include)\s*\{([^{}]+)\}"),
    "bibliography_files": re.compile(r"\\(?:bibliography|addbibresource)\s*\{([^{}]+)\}"),
    "graphics_paths": re.compile(r"\\includegraphics\s*(?:\[[^\]]*\]\s*)?\{([^{}]+)\}"),
}

COUNT_PATTERNS = {
    "parts": re.compile(r"\\part\*?\s*\{"),
    "chapters": re.compile(r"\\chapter\*?\s*\{"),
    "sections": re.compile(r"\\section\*?\s*\{"),
    "subsections": re.compile(r"\\subsection\*?\s*\{"),
    "subsubsections": re.compile(r"\\subsubsection\*?\s*\{"),
    "figures": re.compile(r"\\begin\s*\{figure\*?\}"),
    "tables": re.compile(r"\\begin\s*\{table\*?\}"),
    "equations": re.compile(r"\\begin\s*\{equation\*?\}"),
    "align_blocks": re.compile(r"\\begin\s*\{align\*?\}"),
    "algorithms": re.compile(r"\\begin\s*\{algorithm\*?\}"),
    "captions": re.compile(r"\\caption\s*(?:\[[^\]]*\]\s*)?\{"),
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


def read_text(path: Path) -> str:
    data = path.read_bytes()
    for encoding in ENCODINGS:
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise UnicodeError(f"Unable to decode {path}")


def discover_files(path: Path) -> list[Path]:
    path = path.resolve()
    if path.is_file():
        if path.suffix.lower() != ".tex":
            raise ValueError(f"Expected a .tex file: {path}")
        return [path]
    if not path.is_dir():
        raise FileNotFoundError(path)
    return sorted(
        item
        for item in path.rglob("*.tex")
        if not any(
            part in IGNORED_DIRS or part.lower().startswith(ARCHIVE_PREFIXES)
            for part in item.relative_to(path).parts[:-1]
        )
    )


def split_values(values: list[str]) -> list[str]:
    return [item.strip() for value in values for item in value.split(",") if item.strip()]


def analyze_path(path: Path) -> dict:
    files = discover_files(path)
    sets = {name: set() for name in SET_PATTERNS}
    occurrences = {name: Counter() for name in SET_PATTERNS}
    counts = Counter()

    for file_path in files:
        text = strip_comments(read_text(file_path))
        for name, pattern in SET_PATTERNS.items():
            values = split_values(pattern.findall(text))
            sets[name].update(values)
            occurrences[name].update(values)
        for name, pattern in COUNT_PATTERNS.items():
            counts[name] += len(pattern.findall(text))

    return {
        "path": str(path.resolve()),
        "tex_file_count": len(files),
        "sets": {name: sorted(values) for name, values in sets.items()},
        "duplicates": {
            name: sorted(value for value, count in values.items() if count > 1)
            for name, values in occurrences.items()
        },
        "counts": dict(sorted(counts.items())),
    }


def add_issue(issues: list[dict], severity: str, code: str, message: str, details: list[str] | None = None) -> None:
    issue = {"severity": severity, "code": code, "message": message}
    if details:
        issue["details"] = details
    issues.append(issue)


def compare_analyses(source: dict, target: dict) -> dict:
    issues: list[dict] = []
    source_sets = {name: set(values) for name, values in source["sets"].items()}
    target_sets = {name: set(values) for name, values in target["sets"].items()}

    critical_sets = (
        "labels",
        "reference_targets",
        "citation_keys",
        "included_files",
        "bibliography_files",
        "graphics_paths",
    )
    for name in critical_sets:
        missing = sorted(source_sets[name] - target_sets[name])
        extra = sorted(target_sets[name] - source_sets[name])
        if missing:
            add_issue(issues, "error", f"missing-{name}", f"Target is missing {len(missing)} source {name.replace('_', ' ')}.", missing)
        if extra:
            add_issue(issues, "warning", f"extra-{name}", f"Target adds {len(extra)} {name.replace('_', ' ')} not present in source.", extra)

    unresolved = sorted(target_sets["reference_targets"] - target_sets["labels"])
    if unresolved:
        add_issue(issues, "error", "unresolved-target-references", "Target references labels that are not defined in the audited target.", unresolved)

    duplicate_labels = target["duplicates"].get("labels", [])
    if duplicate_labels:
        add_issue(issues, "error", "duplicate-target-labels", "Target defines duplicate labels.", duplicate_labels)

    count_keys = sorted(set(source["counts"]) | set(target["counts"]))
    for name in count_keys:
        source_count = source["counts"].get(name, 0)
        target_count = target["counts"].get(name, 0)
        if source_count != target_count:
            add_issue(
                issues,
                "warning",
                f"count-mismatch-{name}",
                f"{name}: source={source_count}, target={target_count}.",
            )

    severity_counts = Counter(issue["severity"] for issue in issues)
    status = "fail" if severity_counts["error"] else "review" if severity_counts["warning"] else "pass"
    return {
        "status": status,
        "summary": {"errors": severity_counts["error"], "warnings": severity_counts["warning"]},
        "source": source,
        "target": target,
        "issues": issues,
        "limitations": "Structural comparison does not prove semantic fidelity or visual correctness.",
    }


def render_text(report: dict) -> str:
    lines = [
        f"Status: {report['status']}",
        f"Errors: {report['summary']['errors']}; warnings: {report['summary']['warnings']}",
    ]
    for issue in report["issues"]:
        lines.append(f"[{issue['severity'].upper()}] {issue['code']}: {issue['message']}")
        lines.extend(f"  - {detail}" for detail in issue.get("details", []))
    lines.append("Note: " + report["limitations"])
    return "\n".join(lines)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path, help="Source .tex file or project directory")
    parser.add_argument("--target", required=True, type=Path, help="Translated .tex file or project directory")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    parser.add_argument("--fail-on", choices=("error", "warning", "never"), default="error")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        report = compare_analyses(analyze_path(args.source), analyze_path(args.target))
    except (FileNotFoundError, ValueError, UnicodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2) if args.json else render_text(report))
    if args.fail_on == "never":
        return 0
    if args.fail_on == "warning":
        return 1 if report["summary"]["errors"] or report["summary"]["warnings"] else 0
    return 1 if report["summary"]["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
