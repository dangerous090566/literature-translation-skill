# Translation and Fidelity Policy

## Source hierarchy

Use the highest-authority source available:

1. The exact user-designated LaTeX revision.
2. Official publisher or venue source for the target revision.
3. Official arXiv or author repository source aligned to the target PDF.
4. User-provided PDF, reconstructed with explicit caveats.

Record a version marker such as a filename, commit, arXiv version, timestamp, or checksum. If the PDF and LaTeX disagree, stop treating them as interchangeable: use the designated artifact for content and the other only for comparison.

## Fidelity rules

- Preserve propositions, evidence, qualifications, negation, modality, numerical values, units, and comparison direction.
- Preserve paragraph roles and local argument order unless Chinese grammar requires sentence reordering inside the paragraph.
- Do not improve the science, repair unsupported reasoning, or add explanations in the translated body. Put translator notes outside the manuscript unless the user explicitly requests annotations.
- Keep citations attached to the claims they support. Do not move a citation across paragraph boundaries for stylistic convenience.
- Keep abbreviations consistent. Introduce `中文（English, ABBR）` only when useful, then use the established short form.
- Preserve deliberate distinctions such as proposed/baseline, liable/non-liable, open-loop/closed-loop, and observed/estimated.

## Protected LaTeX content

Do not translate or normalize these without a concrete reason:

- command names and arguments that are identifiers;
- `\label`, `\ref`, `\eqref`, `\autoref`, `\cref`, and citation keys;
- bibliography database entries unless bibliography localization is requested;
- math variables, operators, subscripts, superscripts, units, and equation labels;
- filenames, paths, URLs, model checkpoints, dataset splits, and command-line flags;
- source code, pseudocode identifiers, configuration keys, and API names.

Translate visible prose inside commands such as headings, captions, footnotes, table cells, and algorithm descriptions. Distinguish visible text from machine-stable arguments before editing custom macros.

## Equations and quantitative claims

- Copy equations structurally; translate only surrounding prose and textual annotations such as `\text{loss}` when a Chinese rendering is unambiguous and does not affect conventions.
- Verify every quantity, sign, inequality, interval, percentage, unit, and table value against the source.
- Preserve equation order and labels. If line wrapping changes, retain mathematical grouping and alignment semantics.
- Treat decimal separators, minus signs, multiplication symbols, and scientific notation as data, not typography.

## Figures, tables, and algorithms

- Preserve figure/table identity, order, caption-to-label association, and in-text references.
- Translate captions and table headers. Keep metric abbreviations alongside Chinese labels when needed, such as `驾驶分数（DS）`.
- Do not redraw or OCR text inside raster figures unless requested. Report retained English figure text.
- Preserve table values and emphasis such as bold/underline that conveys best or second-best results.
- Preserve algorithm inputs, outputs, step order, variables, and control flow. Translate only descriptive prose and comments.

## PDF-only reconstruction

When no source files exist:

1. Extract text and page images using an available PDF workflow.
2. Build a page-to-structure map covering headings, paragraphs, equations, figures, tables, footnotes, and references.
3. Mark uncertain OCR, reading order, symbols, and hyphenation. Never guess silently.
4. Reconstruct labels and citation keys as local implementation details, while preserving displayed numbering and reference relationships.
5. Compare every reconstructed page visually with the source PDF.
6. Describe the deliverable as reconstructed, not source-aligned.

For scanned PDFs, distinguish OCR confidence from translation confidence. A fluent translation of uncertain OCR is still uncertain.

## Semantic review checklist

- No paragraph, caption, footnote, table row, algorithm step, or appendix item is missing.
- Negation and modality match the source.
- All numbers, units, symbols, dataset splits, and baseline names match.
- Pronoun and referent resolution remains correct after Chinese sentence reordering.
- Contributions and limitations retain their original strength.
- Terminology is consistent across prose, tables, captions, and appendices.
- Translator notes and unresolved passages are explicit and outside the source-authored claims.
