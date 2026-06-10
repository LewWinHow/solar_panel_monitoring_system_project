# reports/utils.py
import io
from django.utils.timezone import localtime, is_naive, make_aware
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from solar_panel.models import SolarPanelReport, ContentOfSolarPanelReport

def generate_solar_report_report_pdf(id):
    report = SolarPanelReport.objects.get(id=id)
    content = ContentOfSolarPanelReport.objects.filter(solar_panel_report=report).first()

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Title
    p.setFont("Helvetica-Bold", 20)
    p.drawCentredString(width / 2, height - 2 * cm, "Solar Panel Monthly Report")

    # Info
    p.setFont("Helvetica", 12)
    y = height - 3.5 * cm
    p.drawString(2.5 * cm, y, f"Report ID: {report.id}")
    y -= 0.8 * cm
    p.drawString(2.5 * cm, y, f"Month/Year: {report.month}/{report.year}")

    if is_naive(report.generated_time):
        created_time = make_aware(report.generated_time)
    else:
        created_time = report.generated_time
    created_time_local = localtime(created_time)
    y -= 0.8 * cm
    p.drawString(2.5 * cm, y, f"Created Time: {created_time_local.strftime('%Y-%m-%d %H:%M:%S')}")

    # Summary
    y -= 1.5 * cm
    p.setFont("Helvetica-Bold", 14)
    p.drawString(2.5 * cm, y, "Summary")
    p.setFont("Helvetica", 12)
    y -= 0.8 * cm
    p.drawString(3 * cm, y, f"Total solar panels: {content.total_solar_panel}")
    y -= 0.6 * cm
    p.drawString(3 * cm, y, f"Damaged panels: {content.total_damage}")
    y -= 0.6 * cm
    p.drawString(3 * cm, y, f"Clean panels: {content.total_clean}")
    y -= 0.6 * cm
    p.drawString(3 * cm, y, f"Dusty panels: {content.total_dusty}")
    y -= 0.6 * cm
    p.drawString(3 * cm, y, f"Bird drop affected panels: {content.total_bird_drop}")

    # Footer
    p.setFont("Helvetica-Oblique", 10)
    p.drawRightString(width - 2 * cm, 1.5 * cm, "Page 1")

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer  # 返回 PDF 数据
