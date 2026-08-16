---
name: literature-translation
description: Translate academic papers, theses, preprints, and technical reports into polished Chinese from LaTeX or PDF while preserving claims, equations, citations, figures, tables, labels, and compilability. Use when Codex must translate or align academic literature, create a Chinese LaTeX/PDF edition, reconstruct a paper from PDF, or audit an existing translation for structural fidelity, terminology consistency, and build quality. Do not use for inventing new claims or substantively rewriting the source.
---

# Literature Translation

Produce a faithful Chinese scholarly artifact, not merely translated prose. Treat the identified source version as authoritative and keep every factual claim, qualifier, number, citation, equation, and structural relationship traceable to it.

## Core workflow

1. Establish scope and source authority.
   - Identify the exact paper version, desired output language, deliverables, and whether the result should be Chinese-only or bilingual.
   - Prefer official or user-provided LaTeX. Use PDF as a visual reference when both exist.
   - When only a PDF exists, state that the LaTeX is reconstructed and use the PDF workflow in [references/translation-policy.md](references/translation-policy.md).
   - Do not silently combine different revisions of a paper.

2. Inventory before editing.
   - Preserve the source tree and create a separate target such as `main_zh.tex` or a separate output directory.
   - For a LaTeX project, run `python scripts/project_inventory.py <source>` to identify root files, dependencies, structural anchors, and likely build inputs.
   - Resolve ambiguous root documents or missing includes before translating. Never infer missing experimental results.

3. Translate with protected structure.
   - Read [references/translation-policy.md](references/translation-policy.md) for fidelity, PDF-only reconstruction, equations, citations, tables, algorithms, and figure rules.
   - Read [references/terminology.md](references/terminology.md) for terminology-heavy AI, robotics, control, or autonomous-driving papers, or whenever terminology consistency matters.
   - Translate complete paragraphs and preserve their rhetorical role. Use idiomatic, restrained academic Chinese without strengthening or weakening claims.
   - Keep LaTeX commands, labels, cite keys, file paths, code, variables, units, model names, dataset names, and metric abbreviations unchanged unless a scoped compatibility fix is required.
   - Translate headings, prose, captions, table headers, algorithm descriptions, footnotes, and appendices. Translate text embedded inside figures only when explicitly requested and editable source assets are available.

4. Build using the project-native toolchain.
   - Inspect local build files first: `latexmkrc`, `Makefile`, CI configuration, class files, and author notes.
   - Follow [references/latex-build-and-qa.md](references/latex-build-and-qa.md) for engine selection, bibliography passes, log checks, and safe Chinese support.
   - Prefer `latexmk` when available. Use `xelatex` or `lualatex` for Chinese unless the authoritative template requires another engine.
   - For a portable Chinese PDF, use an explicitly selected project-local Unicode OpenType/TrueType CJK font when the default CJK font path produces legacy CID fonts. Do not accept viewer-dependent font fallback.
   - Make the smallest compatibility change possible; do not replace an official venue template merely to obtain Chinese output.

5. Audit structural fidelity.
   - Run `python scripts/audit_translation.py --source <source> --target <target>` on the source and translated root files or project directories.
   - Resolve every missing label, reference target, citation key, included file, and graphics path. Investigate environment or section-count differences rather than automatically forcing counts to match.
   - Treat the audit as a guardrail, not a semantic proof. Manually compare claims, negation, conditions, quantities, units, and limitations.

6. Render and visually verify.
   - Run `python scripts/check_pdf_fonts.py <final.pdf> --json`. Resolve every unembedded CJK font and every CJK Type 0 font lacking `/ToUnicode` before delivery.
   - Render the final PDF with two independent engines when Chinese text is present, preferably Poppler and PyMuPDF. A single renderer can hide missing CMaps through local font fallback.
   - Inspect at minimum the title/abstract, a dense equation page, a figure/table-heavy page, the bibliography, and appendices when present.
   - Check overflow, missing glyphs, broken cross-references, float drift, clipped tables, caption separation, and figures entering the bibliography.
   - If source and target pagination differ, compare by structural anchors rather than page number alone.

7. Deliver with an audit trail.
   - Report the exact source version and whether the translation was source-aligned or PDF-reconstructed.
   - Link the translated `.tex`, compiled PDF, and any copied or localized assets.
   - State the build command, structural-audit result, pages visually checked, remaining warnings, and terminology or figure-text caveats.

## Non-negotiable rules

- Never overwrite the only copy of the source.
- Never fabricate text, citations, equations, figures, tables, or results that are absent from the source.
- Never drop content because extraction or compilation is difficult; mark unresolved material and continue with traceable placeholders.
- Never translate identifiers that must remain machine-stable, including `\label`, cite keys, command names, filenames, URLs, dataset splits, and code symbols.
- Never claim equivalence based only on successful compilation. Compilation, structural audit, semantic review, and visual inspection are separate checks.
- Never deliver a Chinese PDF that depends on a reader's system font fallback or external Adobe CMap/language packs. Require embedded CJK fonts, `/ToUnicode`, and successful cross-renderer screenshots.
- Preserve uncertainty. Words such as “may,” “approximately,” “under this assumption,” and negative constructions are meaning-bearing.

## Bundled resources

- `scripts/project_inventory.py`: read-only LaTeX project inventory and root-file detection.
- `scripts/audit_translation.py`: read-only source/translation structural comparison with JSON output support.
- `scripts/check_pdf_fonts.py`: verify embedded fonts and Unicode mappings needed for portable Chinese PDF rendering and extraction.
- `references/translation-policy.md`: detailed fidelity and PDF-reconstruction rules.
- `references/latex-build-and-qa.md`: build, log, and visual-QA procedure.
- `references/terminology.md`: bilingual terminology policy and consistency rules.
