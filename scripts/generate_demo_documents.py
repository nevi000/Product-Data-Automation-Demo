"""Regenerate the bundled fictional demo documents.

    python scripts/generate_demo_documents.py

Reads the canonical extraction fixtures from
`app/services/extraction/documents.py` and renders each one into a file under
`demo_data/documents/`. The PDFs are written with a tiny hand-rolled PDF writer
(no dependency). The `.jpg` needs Pillow — only to *regenerate* the asset; the
committed file has no runtime dependency.

Everything rendered here is invented. No employer data, prompts or layouts.
"""

from __future__ import annotations

import sys
from io import BytesIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.services.extraction.documents import (
    DEMO_DOCUMENTS,
    DOCUMENTS_DIR,
    DemoDocument,
)

# --------------------------------------------------------------- layout model

def _lines(doc: DemoDocument) -> list[tuple[str, str]]:
    """(style, text) rows, top to bottom. style in {h1, meta, rule, h2, kv, note}."""
    rows: list[tuple[str, str]] = [
        ("h1", f"{doc.supplier_name} - {doc.kind}"),
        ("meta", f"Document {doc.doc_number}    Date {doc.doc_date}"),
        ("meta", "FICTIONAL DEMO DOCUMENT - invented data, not from any real supplier"),
        ("rule", ""),
    ]
    for line in doc.lines:
        rows.append(("h2", f"Pos {line.position:>3}   {line.source_reference or '-'}   {line.model_name}"))
        if line.color_name:
            colour = line.color_name + (f" ({line.color_code})" if line.color_code else "")
            rows.append(("kv", f"Colour        {colour}"))
        if line.sizes:
            rows.append(("kv", f"Sizes         {', '.join(line.sizes)}"))
        if line.ean_by_size:
            eans = "  ".join(f"{s}:{e}" for s, e in line.ean_by_size.items())
            rows.append(("kv", f"EAN / size    {eans}"))
        elif line.ean:
            rows.append(("kv", f"EAN           {line.ean}"))
        if line.material:
            rows.append(("kv", f"Material      {line.material}"))
        if line.care_instructions:
            rows.append(("kv", f"Care          {line.care_instructions}"))
        price = []
        if line.purchase_price:
            price.append(f"Wholesale {line.purchase_price.currency} {line.purchase_price.amount}")
        if line.suggested_retail_price:
            p = line.suggested_retail_price
            price.append(f"RRP {p.currency} {p.amount}")
        if price:
            rows.append(("kv", "Price         " + "    ".join(price)))
        rows.append(("gap", ""))
    rows.append(("note", f"{doc.product_count} line items - end of document"))
    return rows


# ------------------------------------------------------------------- pdf writer

def _esc(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _content_stream(rows: list[tuple[str, str]]) -> str:
    styles = {  # font, size, leading
        "h1": ("F2", 17, 24), "meta": ("F1", 9, 13), "rule": (None, 0, 10),
        "h2": ("F2", 11, 18), "kv": ("F3", 8.5, 12.5), "gap": (None, 0, 7),
        "note": ("F1", 9, 16),
    }
    out = ["BT", "56 782 Td"]
    y = 782
    for style, text in rows:
        font, size, leading = styles[style]
        if style == "rule":
            out.append("ET")
            out.append(f"56 {y - 3} m 539 {y - 3} l 0.75 w 0.7 0.7 0.7 RG S")
            out.append("BT")
            out.append(f"56 {y - leading} Td")
            y -= leading
            continue
        if font is None:
            out.append(f"0 -{leading} Td")
            y -= leading
            continue
        grey = "0.35 0.35 0.4" if style in ("meta", "note") else "0.1 0.12 0.16"
        out.append(f"/{font} {size} Tf {grey} rg")
        out.append(f"({_esc(text)}) Tj")
        out.append(f"0 -{leading} Td")
        y -= leading
    out.append("ET")
    return "\n".join(out)


def build_pdf(rows: list[tuple[str, str]]) -> bytes:
    content = _content_stream(rows).encode("latin-1", "replace")
    page = (
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842]"
        b" /Resources << /Font << /F1 4 0 R /F2 5 0 R /F3 6 0 R >> >>"
        b" /Contents 7 0 R >>"
    )
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        page,
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>",
        b"<< /Length %d >>\nstream\n%s\nendstream" % (len(content), content),
    ]
    buf = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = []
    for i, body in enumerate(objects, start=1):
        offsets.append(len(buf))
        buf += b"%d 0 obj\n%s\nendobj\n" % (i, body)
    xref_pos = len(buf)
    buf += b"xref\n0 %d\n" % (len(objects) + 1)
    buf += b"0000000000 65535 f \n"
    for off in offsets:
        buf += b"%010d 00000 n \n" % off
    buf += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (
        len(objects) + 1,
        xref_pos,
    )
    return bytes(buf)


# ------------------------------------------------------------------- jpg writer

def build_jpg(rows: list[tuple[str, str]]) -> bytes:
    from PIL import Image, ImageDraw, ImageFont

    def font(size: int, bold: bool = False, mono: bool = False) -> ImageFont.FreeTypeFont:
        names = (
            ["consola.ttf", "DejaVuSansMono.ttf"] if mono
            else (["arialbd.ttf", "DejaVuSans-Bold.ttf"] if bold else ["arial.ttf", "DejaVuSans.ttf"])
        )
        for n in names:
            try:
                return ImageFont.truetype(n, size)
            except OSError:
                continue
        return ImageFont.load_default()

    styles = {
        "h1": (font(30, bold=True), 44, (26, 30, 40)),
        "meta": (font(15), 22, (110, 114, 128)),
        "h2": (font(18, bold=True), 30, (26, 30, 40)),
        "kv": (font(14, mono=True), 22, (40, 44, 54)),
        "gap": (None, 12, None),
        "rule": (None, 18, None),
        "note": (font(15), 28, (110, 114, 128)),
    }
    x, top = 72, 64
    W = 1180

    # measure to size the canvas to the content
    y = top
    for style, _ in rows:
        y += styles[style][1]
    H = max(560, y + 88)

    img = Image.new("RGB", (W, H), (247, 246, 243))
    d = ImageDraw.Draw(img)
    y = top
    for style, text in rows:
        f, lead, colour = styles[style]
        if style == "rule":
            d.line([(x, y + 4), (W - 72, y + 4)], fill=(210, 210, 214), width=2)
        elif f is not None:
            d.text((x, y), text, font=f, fill=colour)
        y += lead

    d.rectangle([20, 20, W - 20, H - 20], outline=(224, 223, 219), width=2)

    out = BytesIO()
    img.save(out, format="JPEG", quality=86)
    return out.getvalue()


# ------------------------------------------------------------------------ main

def main() -> None:
    DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
    for demo in DEMO_DOCUMENTS.values():
        rows = _lines(demo)
        if demo.media_type == "application/pdf":
            data = build_pdf(rows)
        elif demo.media_type == "image/jpeg":
            data = build_jpg(rows)
        else:
            raise SystemExit(f"unsupported media type: {demo.media_type}")
        demo.path.write_bytes(data)
        print(f"wrote {demo.path.relative_to(DOCUMENTS_DIR.parent.parent)} ({len(data)} bytes)")


if __name__ == "__main__":
    main()
