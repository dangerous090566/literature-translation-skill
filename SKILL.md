---
name: literature-translation
description: Translate academic literature, especially papers with LaTeX source or PDFs, into polished Chinese while preserving scholarly structure, citations, figures, tables, equations, and compilability. Use when the user asks to parse a paper into LaTeX, translate paper source, make a Chinese version of an English manuscript, align a translation with an original PDF/TEX, or produce a compiled Chinese PDF from academic source files.
---

# Literature Translation

## Overview

Use this skill to produce a faithful, readable Chinese version of academic literature. Prefer translating from the original `.tex` source when available; use PDF extraction only as a fallback or for verification.

## Core Workflow

1. Identify the source of truth.
   - Prefer official LaTeX source from arXiv, publisher supplements, project repositories, or user-provided `.tex`.
   - If only a PDF is available, extract text and structure carefully, but state that the result is reconstructed rather than source-aligned.
   - If both PDF and LaTeX exist, use LaTeX as the editing base and use the PDF for visual/semantic verification.

2. Preserve the scholarly artifact.
   - Keep document structure, section order, labels, citations, equations, figures, tables, algorithms, and appendices aligned with the original.
   - Do not casually merge, remove, renumber, or reorder figures/tables.
   - Preserve `\label`, `\ref`, `\cite`, `\bibliography`, mathematical notation, and package-level semantics unless compilation requires a scoped fix.

3. Translate into idiomatic Chinese.
   - Translate paragraph by paragraph, not sentence-fragment by sentence-fragment.
   - Make Chinese prose natural for a technical reader while preserving the original claims, scope, limitations, and experimental results.
   - Keep tone academic, precise, and restrained.
   - Avoid literal English word order when it makes Chinese awkward.

4. Keep suitable technical terms in English.
   - Do not force every professional term into Chinese.
   - Preserve widely used terms such as `backbone`, `benchmark`, `token`, `adapter`, `prompt`, `fine-tuning`, `zero-shot`, `closed-loop`, `open-loop`, `end-to-end`, `agent`, `pipeline`, and model/dataset names when Chinese translation would be less precise.
   - On first use, optionally write `中文解释（English term）` when it improves readability; afterwards use the shorter dominant form.
   - Load [references/terminology.md](references/terminology.md) when handling terminology-heavy papers or when the user asks for term consistency.

5. Compile and verify.
   - For LaTeX deliverables, compile with the appropriate engine, usually `xelatex` for Chinese.
   - Run bibliography and repeated LaTeX passes until references stabilize.
   - Render or inspect the compiled PDF when layout matters. Check title page, dense figure/table pages, appendix pages, and bibliography pages.
   - Fix obvious issues such as missing fonts, undefined references, figure/table floats entering the bibliography, broken captions, or Chinese text overflow.

## LaTeX Translation Rules

- Prefer creating a separate Chinese file such as `main_zh.tex` instead of overwriting the original source.
- Use a Chinese-capable class or package, for example `ctexart`, `ctexrep`, `ctexbook`, or `ctex` with the original conference class when compatible.
- Keep original figures and bibliography files unless the user asks to localize figure text or references.
- Translate captions, section titles, abstract, body text, table headers, algorithm descriptions, and appendix prose.
- Preserve code blocks, commands, paths, dataset identifiers, model names, metric names, and proper nouns unless a standard Chinese name is clearly established.
- When the source contains generated or placeholder data, do not invent missing results. Mark uncertainty plainly.

## Quality Bar

The final translation should let a Chinese technical reader understand the paper without needing to constantly look back at the English version, while still preserving important English terminology used by the field.

Before final delivery, report:

- Source used: official LaTeX, reconstructed PDF text, or mixed.
- Deliverables: `.tex`, compiled `.pdf`, and any copied assets.
- Validation: compile commands, warnings that remain, and pages visually checked.
- Translation caveats: terms intentionally left in English, incomplete source sections, or figures whose internal English labels were preserved.
