import io

from django.shortcuts import get_object_or_404
from django.utils.timezone import localtime, is_naive, make_aware
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm

from login.models import LoginReport, TotalContentOfLoginReport, BlacklistContentOfLoginReport


def generate_login_report_pdf(id):
    report = get_object_or_404(LoginReport, id=id)
    total_content = TotalContentOfLoginReport.objects.filter(login_report=report).first()
    blacklist_contents = BlacklistContentOfLoginReport.objects.filter(login_report=report).all()

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # 标题
    p.setFont("Helvetica-Bold", 20)
    p.drawCentredString(width / 2, height - 2 * cm, "Login Monthly Report")

    # 基本信息
    p.setFont("Helvetica", 12)
    y = height - 3.5 * cm
    p.drawString(2.5 * cm, y, f"Report ID: {report.id}")
    y -= 0.8 * cm
    p.drawString(2.5 * cm, y, f"Month/Year: {report.month}/{report.year}")

    # 生成时间
    if is_naive(report.generated_time):
        created_time = make_aware(report.generated_time)
    else:
        created_time = report.generated_time

    created_time_local = localtime(created_time)
    y -= 0.8 * cm
    p.drawString(2.5 * cm, y, f"Created Time: {created_time_local.strftime('%Y-%m-%d %H:%M:%S')}")

    # 统计摘要
    y -= 1.5 * cm
    p.setFont("Helvetica-Bold", 14)
    p.drawString(2.5 * cm, y, "Summary")

    p.setFont("Helvetica", 12)
    y -= 0.8 * cm
    p.drawString(3 * cm, y, f"Total login attempts: {total_content.total_login_count}")
    y -= 0.6 * cm
    p.drawString(3 * cm, y, f"Successful logins: {total_content.total_login_successful}")
    y -= 0.6 * cm
    p.drawString(3 * cm, y, f"Failed logins: {total_content.total_login_failed}")

    # 黑名单表格
    y -= 1.5 * cm
    p.setFont("Helvetica-Bold", 14)
    p.drawString(2.5 * cm, y, "Blacklisted IP Addresses")

    y -= 0.8 * cm
    p.setFont("Helvetica-Bold", 12)
    p.drawString(3 * cm, y, "Login Info ID")
    p.drawString(6 * cm, y, "IP Address")
    p.drawString(10 * cm, y, "System")
    p.drawString(14 * cm, y, "Device")
    p.drawString(18 * cm, y, "BOT")

    p.setStrokeColor(colors.black)
    p.setLineWidth(0.5)

    for blacklist_content in blacklist_contents:
        y -= 0.6 * cm
        if y < 2 * cm:  # 如果接近底部，新建页面
            p.showPage()
            y = height - 2 * cm
            p.setFont("Helvetica-Bold", 12)
            p.drawString(3 * cm, y, "Login Info ID")
            p.drawString(6 * cm, y, "IP Address")
            p.drawString(10 * cm, y, "System")
            p.drawString(14 * cm, y, "Device")
            p.drawString(18 * cm, y, "BOT")
            y -= 0.6 * cm

        login_info = blacklist_content.login_info
        p.setFont("Helvetica", 12)
        p.drawString(3 * cm, y, str(login_info.id))
        p.drawString(6 * cm, y, login_info.ip)
        p.drawString(10 * cm, y, login_info.system)
        p.drawString(14 * cm, y, login_info.device)
        p.drawString(18 * cm, y, ("Yes" if login_info.is_bot else "None"))

    # 页脚页码
    p.setFont("Helvetica-Oblique", 10)
    p.drawRightString(width - 2 * cm, 1.5 * cm, "Page 1")

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer