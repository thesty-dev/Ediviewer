"""Flask web application for EDIFACT file viewer."""

import io
import os
import sys
from datetime import datetime

# Ensure the directory containing app.py is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, jsonify, send_file
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)

from edifact_parser import parse_edifact

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB


def _parse_from_request(req):
    if "file" in req.files and req.files["file"].filename:
        content = req.files["file"].read().decode("utf-8", errors="replace")
    else:
        content = req.form.get("text", "")
    if not content.strip():
        raise ValueError("Leerer Inhalt")
    return parse_edifact(content)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/parse", methods=["POST"])
def parse():
    if "file" not in request.files and "text" not in request.form:
        return jsonify({"error": "Keine Datei oder Text übermittelt"}), 400
    try:
        result = _parse_from_request(request)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Fehler beim Parsen: {str(e)}"}), 500


@app.route("/export/pdf", methods=["POST"])
def export_pdf():
    try:
        data = _parse_from_request(request)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    buf = io.BytesIO()
    _build_pdf(buf, data)
    buf.seek(0)

    filename = f"edifact_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    return send_file(
        buf,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename,
    )


# ── PDF builder ──────────────────────────────────────────────────────────────

_DARK = colors.HexColor("#1a1d27")
_ACCENT = colors.HexColor("#5b8dee")
_GREEN = colors.HexColor("#2dd4a0")
_YELLOW = colors.HexColor("#f0c040")
_PURPLE = colors.HexColor("#7c6af7")
_LIGHT = colors.HexColor("#e2e8f0")
_MUTED = colors.HexColor("#94a3b8")
_BORDER = colors.HexColor("#2e3347")
_SURFACE = colors.HexColor("#232635")

_SERVICE_TAGS = {"UNA", "UNB", "UNZ", "UNG", "UNE", "UNH", "UNT"}


def _tag_color(tag: str) -> colors.Color:
    if tag in _SERVICE_TAGS:
        return _YELLOW
    if tag == "BGM":
        return _GREEN
    if tag == "DTM":
        return _ACCENT
    if tag == "NAD":
        return _PURPLE
    return _MUTED


def _build_pdf(buf: io.BytesIO, data: dict):
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.8 * cm,
        bottomMargin=1.5 * cm,
    )

    styles = getSampleStyleSheet()
    base = styles["Normal"]

    def style(**kw):
        s = ParagraphStyle("_", parent=base, **kw)
        return s

    title_s = style(fontSize=18, textColor=_ACCENT, spaceAfter=4,
                    fontName="Helvetica-Bold")
    sub_s = style(fontSize=9, textColor=_MUTED, spaceAfter=12)
    label_s = style(fontSize=8, textColor=_MUTED, fontName="Helvetica-Bold",
                    spaceAfter=2)
    raw_s = style(fontSize=7, textColor=_MUTED, fontName="Courier",
                  wordWrap="CJK")
    tag_s = style(fontSize=11, fontName="Helvetica-Bold")
    name_s = style(fontSize=9, textColor=_MUTED)
    cell_key_s = style(fontSize=8, textColor=_MUTED, fontName="Helvetica-Bold")
    cell_val_s = style(fontSize=8, textColor=_LIGHT, fontName="Courier")

    story = []

    # Title
    story.append(Paragraph("EDIFACT Viewer – Export", title_s))
    story.append(Paragraph(
        f"Erstellt am {datetime.now().strftime('%d.%m.%Y %H:%M')}  ·  "
        f"{data['segment_count']} Segmente",
        sub_s,
    ))

    # Separator info
    seps = data["separators"]
    sep_rows = [
        ["Segment", repr(seps["segment"])],
        ["Datenelement", repr(seps["data"])],
        ["Komponente", repr(seps["component"])],
        ["Release", repr(seps["release"])],
    ]
    sep_table = Table(
        [[Paragraph(k, cell_key_s), Paragraph(v, cell_val_s)] for k, v in sep_rows],
        colWidths=[4 * cm, 3 * cm],
    )
    sep_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), _SURFACE),
        ("TEXTCOLOR", (0, 0), (-1, -1), _LIGHT),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [_SURFACE, _DARK]),
        ("GRID", (0, 0), (-1, -1), 0.3, _BORDER),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(sep_table)
    story.append(Spacer(1, 0.5 * cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=_BORDER))
    story.append(Spacer(1, 0.3 * cm))

    # Segments
    for i, seg in enumerate(data["segments"], 1):
        tag = seg["tag"]
        tc = _tag_color(tag)

        # Header row: index + tag + name
        hdr = Table(
            [[
                Paragraph(f"#{i}", style(fontSize=8, textColor=_MUTED)),
                Paragraph(tag, style(fontSize=11, textColor=tc,
                                     fontName="Helvetica-Bold")),
                Paragraph(seg["name"], name_s),
            ]],
            colWidths=[1 * cm, 2 * cm, None],
        )
        hdr.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), _SURFACE),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LINEBELOW", (0, 0), (-1, -1), 0.5, _BORDER),
        ]))
        story.append(hdr)

        # RAW line
        story.append(Spacer(1, 2))
        story.append(Paragraph(f"RAW: {seg['raw']}", raw_s))
        story.append(Spacer(1, 4))

        # Qualifier description
        if seg.get("qualifier_desc"):
            story.append(Paragraph(
                f"Qualifier: {seg['qualifier']} – {seg['qualifier_desc']}",
                style(fontSize=8, textColor=_ACCENT),
            ))
            story.append(Spacer(1, 4))

        # Elements table
        elem_rows = []
        for ei, comps in enumerate(seg["elements"], 1):
            non_empty = [c for c in comps if c.strip()]
            if not non_empty:
                continue
            pos = f"DE{ei:02d}"
            val = "  ·  ".join(
                f"{ci+1}: {c}" for ci, c in enumerate(comps) if c.strip()
            )
            elem_rows.append([
                Paragraph(pos, cell_key_s),
                Paragraph(val, cell_val_s),
            ])

        if elem_rows:
            t = Table(elem_rows, colWidths=[1.5 * cm, None])
            t.setStyle(TableStyle([
                ("ROWBACKGROUNDS", (0, 0), (-1, -1), [_DARK, _SURFACE]),
                ("GRID", (0, 0), (-1, -1), 0.3, _BORDER),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]))
            story.append(t)

        story.append(Spacer(1, 0.35 * cm))

    def _page(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(_MUTED)
        canvas.drawRightString(
            A4[0] - 1.5 * cm,
            0.8 * cm,
            f"Seite {doc.page}  ·  EDIFACT Viewer",
        )
        canvas.restoreState()

    doc.build(story, onFirstPage=_page, onLaterPages=_page)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
