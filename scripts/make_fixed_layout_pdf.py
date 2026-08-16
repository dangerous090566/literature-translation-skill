#!/usr/bin/env python3
"""Create a reader-proof fixed-layout compatibility PDF.

The output intentionally contains one page-sized raster image per page and no
text layer. Use it only when immutable appearance is more important than text
selection, search, links, and accessibility.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def load_pymupdf():
    try:
        import pymupdf
    except ImportError as exc:  # pragma: no cover - exercised by CLI environments
        raise SystemExit("PyMuPDF is required: python -m pip install pymupdf") from exc
    return pymupdf


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def validate_options(dpi: int, jpeg_quality: int) -> None:
    if dpi < 150:
        raise ValueError("DPI must be at least 150 for readable academic text.")
    if not 1 <= jpeg_quality <= 100:
        raise ValueError("JPEG quality must be between 1 and 100.")


def has_two_column_evidence(page: Any) -> bool:
    """Return whether body text blocks occupy both sides of a visible gutter."""
    width = float(page.rect.width)
    height = float(page.rect.height)
    left = right = 0
    for block in page.get_text("blocks"):
        x0, y0, x1, y1 = map(float, block[:4])
        block_width = x1 - x0
        if y1 < 0.15 * height or y0 > 0.95 * height or block_width > 0.62 * width:
            continue
        center = (x0 + x1) / 2
        if center < 0.47 * width and x1 < 0.55 * width:
            left += 1
        elif center > 0.53 * width and x0 > 0.45 * width:
            right += 1
    return left > 0 and right > 0


def create_fixed_layout(
    source_path: Path,
    output_path: Path,
    *,
    dpi: int = 300,
    jpeg_quality: int = 96,
) -> dict[str, Any]:
    validate_options(dpi, jpeg_quality)
    source = source_path.resolve(strict=True)
    output = output_path.resolve()
    if source == output:
        raise ValueError("Source and output paths must be different.")
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite existing output: {output}")
    if not output.parent.is_dir():
        raise FileNotFoundError(f"Output directory does not exist: {output.parent}")

    pymupdf = load_pymupdf()
    src = pymupdf.open(source)
    if len(src) == 0:
        src.close()
        raise ValueError("Source PDF has no pages.")

    source_sizes = [
        (round(page.rect.width, 3), round(page.rect.height, 3)) for page in src
    ]
    two_column_pages = [
        number
        for number, page in enumerate(src, start=1)
        if has_two_column_evidence(page)
    ]

    fixed = pymupdf.open()
    for source_page in src:
        pixmap = source_page.get_pixmap(
            dpi=dpi,
            colorspace=pymupdf.csRGB,
            alpha=False,
        )
        jpeg = pixmap.tobytes("jpeg", jpg_quality=jpeg_quality)
        page = fixed.new_page(width=source_page.rect.width, height=source_page.rect.height)
        page.insert_image(page.rect, stream=jpeg, keep_proportion=False)

    metadata = dict(src.metadata)
    subject = metadata.get("subject", "").strip()
    metadata["subject"] = (
        subject + "; fixed-layout compatibility edition (viewer reflow disabled)"
    ).strip("; ")
    fixed.set_metadata(metadata)
    fixed.save(output, garbage=4, deflate=True, clean=True)
    fixed.close()
    src.close()

    check = pymupdf.open(output)
    output_sizes = [
        (round(page.rect.width, 3), round(page.rect.height, 3)) for page in check
    ]
    images_per_page = [len(page.get_images(full=True)) for page in check]
    image_dimensions = sorted(
        {
            (image[2], image[3])
            for page in check
            for image in page.get_images(full=True)
        }
    )
    extracted_chars = sum(len(page.get_text()) for page in check)
    result = {
        "source": str(source),
        "source_sha256": sha256(source),
        "output": str(output),
        "output_sha256": sha256(output),
        "bytes": output.stat().st_size,
        "pages": len(check),
        "page_sizes_match": source_sizes == output_sizes,
        "page_sizes_pt": sorted(set(output_sizes)),
        "images_per_page": images_per_page,
        "image_dimensions_px": image_dimensions,
        "extractable_text_chars": extracted_chars,
        "source_pages_with_two_column_evidence": two_column_pages,
        "dpi": dpi,
        "jpeg_quality": jpeg_quality,
    }
    check.close()

    if not result["page_sizes_match"]:
        raise RuntimeError("Output page sizes do not match the source.")
    if any(count != 1 for count in images_per_page):
        raise RuntimeError("Every output page must contain exactly one image.")
    if extracted_chars != 0:
        raise RuntimeError("Fixed-layout output unexpectedly contains extractable text.")
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--dpi", type=int, default=300)
    parser.add_argument("--jpeg-quality", type=int, default=96)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = create_fixed_layout(
        args.source,
        args.output,
        dpi=args.dpi,
        jpeg_quality=args.jpeg_quality,
    )
    print(json.dumps(result, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
