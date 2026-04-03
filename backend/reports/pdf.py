from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
import os

def generate_pdf_report(test_cases: list, url: str) -> str:

    os.makedirs("reports/output", exist_ok=True)
    filename = f"reports/output/qa_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    # ── Styles ──
    styles = getSampleStyleSheet()

    style_title = ParagraphStyle(
        "Title",
        fontSize=22,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#4B0082"),
        alignment=TA_CENTER,
        spaceAfter=6
    )
    style_subtitle = ParagraphStyle(
        "Subtitle",
        fontSize=11,
        fontName="Helvetica",
        textColor=colors.HexColor("#555555"),
        alignment=TA_CENTER,
        spaceAfter=4
    )
    style_section = ParagraphStyle(
        "Section",
        fontSize=13,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#4B0082"),
        spaceBefore=16,
        spaceAfter=6
    )
    style_body = ParagraphStyle(
        "Body",
        fontSize=10,
        fontName="Helvetica",
        textColor=colors.HexColor("#333333"),
        spaceAfter=4
    )
    style_tc_title = ParagraphStyle(
        "TCTitle",
        fontSize=11,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#1a1a2e"),
        spaceBefore=10,
        spaceAfter=4
    )

    # ── Stats ──
    total   = len(test_cases)
    passed  = sum(1 for t in test_cases if t.get("status","").lower() == "pass")
    failed  = sum(1 for t in test_cases if t.get("status","").lower() == "fail")
    pending = total - passed - failed
    pass_rate = f"{(passed/total*100):.1f}%" if total > 0 else "0%"

    elements = []

    # ── Header ──
    elements.append(Spacer(1, 0.3*inch))
    elements.append(Paragraph("🧪 QA Pilot", style_title))
    elements.append(Paragraph("Automated Test Execution Report", style_subtitle))
    elements.append(Spacer(1, 0.1*inch))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#4B0082")))
    elements.append(Spacer(1, 0.2*inch))

    # ── Meta Info Table ──
    meta_data = [
        ["Application URL", url],
        ["Test Date", datetime.now().strftime("%B %d, %Y %H:%M")],
        ["Tested By", "QA Pilot AI Agent"],
        ["Total Test Cases", str(total)],
        ["Report Generated", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
    ]
    meta_table = Table(meta_data, colWidths=[4*cm, 13*cm])
    meta_table.setStyle(TableStyle([
        ("FONTNAME",    (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTNAME",    (1,0), (1,-1), "Helvetica"),
        ("FONTSIZE",    (0,0), (-1,-1), 10),
        ("TEXTCOLOR",   (0,0), (0,-1), colors.HexColor("#4B0082")),
        ("TEXTCOLOR",   (1,0), (1,-1), colors.HexColor("#333333")),
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [colors.HexColor("#F3F0FF"), colors.white]),
        ("GRID",        (0,0), (-1,-1), 0.5, colors.HexColor("#DDDDDD")),
        ("PADDING",     (0,0), (-1,-1), 8),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 0.3*inch))

    # ── Summary Section ──
    elements.append(Paragraph("Executive Summary", style_section))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CCCCCC")))
    elements.append(Spacer(1, 0.1*inch))

    summary_data = [
        ["Total", "Passed", "Failed", "Pending", "Pass Rate"],
        [str(total), str(passed), str(failed), str(pending), pass_rate],
    ]
    summary_table = Table(summary_data, colWidths=[3.4*cm]*5)
    summary_table.setStyle(TableStyle([
        ("FONTNAME",    (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTNAME",    (0,1), (-1,1), "Helvetica-Bold"),
        ("FONTSIZE",    (0,0), (-1,-1), 12),
        ("ALIGN",       (0,0), (-1,-1), "CENTER"),
        ("VALIGN",      (0,0), (-1,-1), "MIDDLE"),
        ("BACKGROUND",  (0,0), (-1,0), colors.HexColor("#4B0082")),
        ("TEXTCOLOR",   (0,0), (-1,0), colors.white),
        ("BACKGROUND",  (0,1), (0,1), colors.HexColor("#E8E0F0")),
        ("BACKGROUND",  (1,1), (1,1), colors.HexColor("#C6EFCE")),
        ("BACKGROUND",  (2,1), (2,1), colors.HexColor("#FFC7CE")),
        ("BACKGROUND",  (3,1), (3,1), colors.HexColor("#FFEB9C")),
        ("BACKGROUND",  (4,1), (4,1), colors.HexColor("#E8E0F0")),
        ("TEXTCOLOR",   (1,1), (1,1), colors.HexColor("#375623")),
        ("TEXTCOLOR",   (2,1), (2,1), colors.HexColor("#9C0006")),
        ("TEXTCOLOR",   (3,1), (3,1), colors.HexColor("#7D6608")),
        ("TEXTCOLOR",   (4,1), (4,1), colors.HexColor("#4B0082")),
        ("GRID",        (0,0), (-1,-1), 0.5, colors.HexColor("#DDDDDD")),
        ("ROWHEIGHT",   (0,0), (-1,-1), 30),
        ("PADDING",     (0,0), (-1,-1), 8),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 0.3*inch))

    # ── Test Cases Section ──
    elements.append(Paragraph("Test Cases Detail", style_section))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CCCCCC")))
    elements.append(Spacer(1, 0.1*inch))

    if test_cases:
        # Table header
        tc_header = [["Test ID", "Description", "Expected", "Actual", "Status"]]
        tc_rows = []
        for tc in test_cases:
            status = tc.get("status", "Pending")
            tc_rows.append([
                tc.get("test_id", ""),
                Paragraph(tc.get("description", ""), style_body),
                Paragraph(tc.get("expected", "-"), style_body),
                Paragraph(tc.get("actual", "-"), style_body),
                status
            ])

        tc_table = Table(
            tc_header + tc_rows,
            colWidths=[2.5*cm, 5*cm, 4*cm, 4*cm, 2*cm]
        )

        tc_style = [
            ("FONTNAME",  (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE",  (0,0), (-1,-1), 9),
            ("BACKGROUND",(0,0), (-1,0), colors.HexColor("#4B0082")),
            ("TEXTCOLOR", (0,0), (-1,0), colors.white),
            ("ALIGN",     (0,0), (-1,-1), "CENTER"),
            ("VALIGN",    (0,0), (-1,-1), "MIDDLE"),
            ("GRID",      (0,0), (-1,-1), 0.5, colors.HexColor("#DDDDDD")),
            ("PADDING",   (0,0), (-1,-1), 6),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.HexColor("#F9F9F9"), colors.white]),
        ]

        # Color status cells
        for i, tc in enumerate(test_cases, 1):
            status = tc.get("status", "Pending").lower()
            if status == "pass":
                tc_style.append(("BACKGROUND", (4,i), (4,i), colors.HexColor("#C6EFCE")))
                tc_style.append(("TEXTCOLOR",  (4,i), (4,i), colors.HexColor("#375623")))
            elif status == "fail":
                tc_style.append(("BACKGROUND", (4,i), (4,i), colors.HexColor("#FFC7CE")))
                tc_style.append(("TEXTCOLOR",  (4,i), (4,i), colors.HexColor("#9C0006")))
            else:
                tc_style.append(("BACKGROUND", (4,i), (4,i), colors.HexColor("#FFEB9C")))
                tc_style.append(("TEXTCOLOR",  (4,i), (4,i), colors.HexColor("#7D6608")))

        tc_table.setStyle(TableStyle(tc_style))
        elements.append(tc_table)
    else:
        elements.append(Paragraph("No test cases recorded.", style_body))

    # ── Footer ──
    elements.append(Spacer(1, 0.4*inch))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#4B0082")))
    elements.append(Spacer(1, 0.1*inch))
    elements.append(Paragraph(
        f"Generated by QA Pilot AI Agent • {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        ParagraphStyle("Footer", fontSize=8, textColor=colors.HexColor("#999999"), alignment=TA_CENTER)
    ))

    doc.build(elements)
    return filename