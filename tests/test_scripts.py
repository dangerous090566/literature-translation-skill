from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


inventory_module = load_module("project_inventory", ROOT / "scripts" / "project_inventory.py")
audit_module = load_module("audit_translation", ROOT / "scripts" / "audit_translation.py")


class ProjectInventoryTests(unittest.TestCase):
    def test_finds_root_and_dependencies(self):
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            (project / "main.tex").write_text(
                r"""\documentclass{article}
\begin{document}
\input{method}
\includegraphics{figure}
\bibliography{refs}
\end{document}
""",
                encoding="utf-8",
            )
            (project / "method.tex").write_text(r"\section{Method}\label{sec:method}", encoding="utf-8")
            (project / "figure.png").write_bytes(b"png")
            (project / "refs.bib").write_text("", encoding="utf-8")

            report = inventory_module.inventory(project)

            self.assertEqual(report["root_candidates"], ["main.tex"])
            self.assertEqual(report["tex_file_count"], 2)
            self.assertEqual(report["missing_dependencies"], [])
            self.assertEqual(report["aggregate_counts"]["sections"], 1)

    def test_ignores_commented_dependencies(self):
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            (project / "main.tex").write_text(
                "\\documentclass{article}\n% \\input{removed}\n\\begin{document}Done\\end{document}\n",
                encoding="utf-8",
            )

            report = inventory_module.inventory(project)

            self.assertEqual(report["missing_dependencies"], [])


class TranslationAuditTests(unittest.TestCase):
    def test_passes_equivalent_structure(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source.tex"
            target = root / "target.tex"
            source.write_text(
                r"\section{Method}\label{sec:m} See \ref{sec:m}. Result \cite{k1}. \bibliography{refs}",
                encoding="utf-8",
            )
            target.write_text(
                r"\section{方法}\label{sec:m} 见 \ref{sec:m}。结果见 \cite{k1}。\bibliography{refs}",
                encoding="utf-8",
            )

            report = audit_module.compare_analyses(
                audit_module.analyze_path(source), audit_module.analyze_path(target)
            )

            self.assertEqual(report["status"], "pass")
            self.assertEqual(report["summary"], {"errors": 0, "warnings": 0})

    def test_reports_missing_anchor_and_count_change(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source.tex"
            target = root / "target.tex"
            source.write_text(
                r"\section{Method}\label{sec:m} See \ref{sec:m}. Result \cite{k1}. \bibliography{refs}",
                encoding="utf-8",
            )
            target.write_text(r"\section{方法}。", encoding="utf-8")

            report = audit_module.compare_analyses(
                audit_module.analyze_path(source), audit_module.analyze_path(target)
            )

            self.assertEqual(report["status"], "fail")
            codes = {issue["code"] for issue in report["issues"]}
            self.assertIn("missing-labels", codes)
            self.assertIn("missing-reference_targets", codes)
            self.assertIn("missing-citation_keys", codes)
            self.assertIn("missing-bibliography_files", codes)



if __name__ == "__main__":
    unittest.main()
