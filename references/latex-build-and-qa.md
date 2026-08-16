# LaTeX Build and QA

## Build selection

Inspect the project before choosing commands. Prefer, in order:

1. The repository's documented build command or CI job.
2. `latexmk` configuration supplied by the project.
3. A minimal `latexmk` command using the required engine.
4. Manual engine and bibliography passes when no build orchestration exists.

Typical Chinese builds:

```powershell
latexmk -xelatex -interaction=nonstopmode -halt-on-error main_zh.tex
```

```powershell
xelatex -interaction=nonstopmode -halt-on-error main_zh.tex
biber main_zh
xelatex -interaction=nonstopmode -halt-on-error main_zh.tex
xelatex -interaction=nonstopmode -halt-on-error main_zh.tex
```

Use `bibtex` instead of `biber` when the project uses BibTeX. Do not switch bibliography systems casually.

## Chinese support

- Prefer the existing class and add the smallest compatible Chinese layer, commonly `ctex` with XeLaTeX or LuaLaTeX.
- Use `ctexart`, `ctexrep`, or `ctexbook` only when replacing the document class does not violate an authoritative template.
- Prefer fonts available on the current system and avoid hard-coding a machine-specific font unless required.
- Prefer a project-local, redistributable Unicode CJK OpenType/TrueType font for final delivery when reproducibility matters. Explicit `fontspec`/`xeCJK` selection is safer than a viewer-dependent fallback or a legacy CMap-only font definition.
- Check the compiled font objects, not only the LaTeX log. A CJK Type 0 font can be embedded yet still render or extract incorrectly in some readers when `/ToUnicode` is absent and the reader cannot load an external `Adobe-GB1`/`Adobe-CNS1`/`Adobe-Japan1`/`Adobe-Korea1` map.
- Preserve the original class, geometry, bibliography style, and venue boilerplate when preparing a source-aligned edition.

Run the bundled portability check on every final Chinese PDF:

```powershell
python scripts/check_pdf_fonts.py path/to/final.pdf --json
```

Treat an unembedded CJK font or a CJK font without `/ToUnicode` as a delivery-blocking error. If the default `ctex` fontset fails this check, select a project-local Unicode font explicitly and rebuild; do not patch screenshots or rely on the local viewer's fallback.

## Log checks

Search the final log for at least:

- `Undefined control sequence`
- `LaTeX Error`
- `Citation.*undefined`
- `Reference.*undefined`
- `There were undefined references`
- `Rerun to get cross-references right`
- `Overfull \\hbox` and `Overfull \\vbox`
- missing characters or fonts
- multiply defined labels

A build that produces a PDF can still be invalid. Resolve errors first, then undefined citations/references, then layout warnings affecting readability.

## Structural audit

Run the bundled comparison after translation:

```powershell
python scripts/audit_translation.py --source path/to/source.tex --target path/to/main_zh.tex
```

Use `--json` for machine-readable results and `--fail-on warning` for stricter automation. Directory inputs compare all `.tex` files recursively while ignoring common build and version-control directories.

The audit detects missing labels, reference targets, citation keys, included files, graphics paths, and structural count differences. It cannot determine whether Chinese prose is semantically faithful.

## Visual QA

If the user requires the original layout or reports viewer-dependent reflow, read [layout-fidelity-and-viewer-compatibility.md](layout-fidelity-and-viewer-compatibility.md) and verify the exact delivered pathname with a versioned-output strategy.

Render the final PDF to images when PDF tooling is available. Inspect:

- title, authors, abstract, and keywords;
- the first page of each major section;
- pages dense with equations, figures, tables, algorithms, or footnotes;
- pages near forced breaks or float barriers;
- the last body page, bibliography, and appendices.

Compare against the source by section, figure/table number, equation label, and caption—not only by page number. Chinese changes line length and pagination.

When “preserve original format” is explicit, also compare page size, column count, title/author geometry, venue boilerplate, page-number range, full-width float pages, and bibliography start/end. Treat a single-column reflow or stale same-name preview as a failed delivery even if the intermediate PDF was correct.

Look for clipped glyphs, font fallback, punctuation at line starts, excessive whitespace, float drift, split captions, tables exceeding columns, figures entering references, orphan headings, and bibliography corruption.

For Chinese output, render with two independent engines, preferably Poppler (`pdftoppm`) and PyMuPDF. Compare at least the title page, one dense body page, one figure/table page, and the bibliography. If one renderer drops Chinese, shows boxes, or substitutes unrelated glyphs, fail the PDF even when another renderer looks correct. Record renderer stderr because missing CMap/language-pack messages can reveal a portability defect that a fallback-capable renderer conceals.

## Final cleanup

- Keep the source and translated roots distinct.
- Do not delete auxiliary files unless the user requests cleanup and the target is explicit.
- Deliver only intended source, PDF, bibliography, class/style, and asset files; exclude secrets, local caches, and unrelated build products.
- Record the exact command used and any remaining non-fatal warning.
