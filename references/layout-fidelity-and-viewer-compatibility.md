# Layout Fidelity and Viewer Compatibility

## Define the fidelity target

Separate three concerns:

1. **Content fidelity**: claims, equations, figures, tables, citations, and numbering remain traceable.
2. **Page-layout fidelity**: paper size, margins, columns, title block, venue boilerplate, float placement, page numbering, and bibliography flow match the designated source.
3. **Viewer fidelity**: the exact delivered PDF renders consistently without stale caching, font fallback, mobile reflow, liquid mode, or accessibility reformatting.

When the user says “preserve the original format,” “keep the typesetting,” or “only translate,” require all three. Do not interpret the request as permission to reflow the paper into a new single-column template.

## Inventory the source layout

Before translating or rebuilding, record:

- page count, page boxes, orientation, and displayed page-number range;
- column count, column widths, gutter, margins, and baseline font size;
- full-width title/author/abstract regions and venue boilerplate;
- each figure/table page and whether the float spans one or two columns;
- the page and column where major sections and references start and end;
- deliberate blank areas, footnotes, headers, footers, and appendices.

Render source contact sheets and retain a page-to-anchor map. For PDF-only reconstruction, prefer the venue's authentic class/style files when they match the designated revision, but never import content from a different revision silently.

## Accept or reject the translated layout

Render the translated PDF and compare it page-by-page with the source contact sheets. When exact pagination is required, treat page count, page size, column structure, page numbers, float pages, and bibliography start/end as acceptance criteria. Adjust Chinese font metrics, leading, float barriers, and reference spacing without replacing the venue template.

Compilation success is not visual acceptance. Reject a build that is single-column, moves wide tables onto different pages without need, drops venue boilerplate, changes the paper size, or expands pagination substantially when the user asked for the original format.

## Diagnose a “single-column” or stale delivery report

Do not immediately blame the reader. Check the exact artifact the user received:

1. Resolve the delivered path and compute its hash, byte size, page count, and page boxes.
2. Reopen that path and render it with two independent engines. Do not substitute `main.pdf` when a differently named file was delivered.
3. Inspect text-block bounding boxes on a representative body page. A two-column page should show separate left and right x-coordinate clusters with a gutter between them.
4. Compare the exact-delivery screenshots with the source and the last verified build.
5. If the bytes are correct but the user's view differs, check same-name cache, mobile/liquid/reflow mode, accessibility reading mode, browser PDF replacement, and reader-specific font fallback.

After replacing a delivered artifact, use a new versioned filename. Reusing the same filename can keep an old preview alive even when the file on disk changed.

## Choose the output strategy

Use this hierarchy:

1. **Searchable vector PDF (default)**: preserve selectable text, links, accessibility, and sharp zooming. Embed Unicode CJK fonts with `/ToUnicode`, then verify the exact delivered filename in two renderers.
2. **Versioned vector PDF**: if caching is suspected, write a new immutable filename such as `_original_layout_v2.pdf` and verify that file directly.
3. **Fixed-layout compatibility PDF (last resort)**: when a reader continues to reflow correctly rendered pages and visual identity is the user's priority, run:

```powershell
python scripts/make_fixed_layout_pdf.py translated.pdf translated_original_layout_v2.pdf
```

The script renders each verified page at 300 DPI and stores it as one page-sized image. This prevents all text reflow and font substitution. It also removes text selection, search, links, and most accessibility semantics. Keep the searchable vector PDF and editable source alongside it, use a distinct filename, and state the tradeoff explicitly.

## Validate a fixed-layout compatibility PDF

Require all of the following:

- source and output page counts and page sizes match;
- each output page contains exactly one full-page image at the requested resolution;
- the output has no extractable text layer, confirming that reflow is impossible;
- two independent renderers reproduce all pages without clipping or corruption;
- full-size checks cover the title page, a dense body page, a figure/table page, the bibliography transition, and the last page;
- the report records DPI, compression quality, file size, hash, and the loss of search/copy/accessibility.
