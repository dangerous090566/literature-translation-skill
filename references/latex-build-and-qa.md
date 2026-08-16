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
- Preserve the original class, geometry, bibliography style, and venue boilerplate when preparing a source-aligned edition.

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

Render the final PDF to images when PDF tooling is available. Inspect:

- title, authors, abstract, and keywords;
- the first page of each major section;
- pages dense with equations, figures, tables, algorithms, or footnotes;
- pages near forced breaks or float barriers;
- the last body page, bibliography, and appendices.

Compare against the source by section, figure/table number, equation label, and caption—not only by page number. Chinese changes line length and pagination.

Look for clipped glyphs, font fallback, punctuation at line starts, excessive whitespace, float drift, split captions, tables exceeding columns, figures entering references, orphan headings, and bibliography corruption.

## Final cleanup

- Keep the source and translated roots distinct.
- Do not delete auxiliary files unless the user requests cleanup and the target is explicit.
- Deliver only intended source, PDF, bibliography, class/style, and asset files; exclude secrets, local caches, and unrelated build products.
- Record the exact command used and any remaining non-fatal warning.
