import django
import os

# 设置 DJANGO_SETTINGS_MODULE 为你的项目的 settings 模块路径
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'solar_panel_monitoring_system_project.settings')
django.setup()
from datetime import datetime
from solar_panel.models import SolarPanelReport, SolarPanelRecord, SolarPanel, ContentOfSolarPanelReport
from login.models import LoginReport, LoginRecord, LoginInfo, BlacklistContentOfLoginReport, TotalContentOfLoginReport
from utils.generate_solar_panel_report_pdf import generate_solar_report_report_pdf
from utils.generate_login_report_pdf import generate_login_report_pdf
from utils.send_email import send_email_with_solar_panel_report_pdf, send_email_with_login_report_pdf


def auto_generate_report():
    # while True:
    time_now = datetime.now()
    # if time_now.day == 1 and time_now.minute == 0 and time_now.second == 0 and time_now.microsecond == 0:
    if time_now.day == 1:
        year = time_now.year
        month = time_now.month
        day = time_now.day
        last_month = datetime(year, month, day)
        first_month = datetime(year, month - 1, day)

        solar_panel_report = SolarPanelReport(year=year, month=month - 1)
        solar_panel_report.save()
        total_solar_panel = SolarPanel.objects.all().count()
        solar_panel_record_list = SolarPanelRecord.objects.filter(recorded_time__gte=first_month,
                                                                  recorded_time__lt=last_month).all()
        total_damage = solar_panel_record_list.filter(damage=1).count()
        total_clean = solar_panel_record_list.filter(cleanliness=1).count()
        total_dusty = solar_panel_record_list.filter(cleanliness=2).count()
        total_bird_drop = solar_panel_record_list.filter(cleanliness=3).count()
        content_of_solar_panel_report = ContentOfSolarPanelReport(solar_panel_report_id=solar_panel_report.id,
                                                                  total_solar_panel=total_solar_panel,
                                                                  total_damage=total_damage, total_clean=total_clean,
                                                                  total_dusty=total_dusty,
                                                                  total_bird_drop=total_bird_drop)
        content_of_solar_panel_report.save()

        login_report = LoginReport(year=year, month=month - 1)
        login_report.save()
        login_record_list = LoginRecord.objects.filter(recorded_time__gte=first_month,
                                                       recorded_time__lt=last_month).all()
        total_login_count = login_record_list.count()
        total_login_successful = login_record_list.filter(status=1).count()
        total_login_failed = login_record_list.filter(status=0).count()
        total_content_of_login_report = TotalContentOfLoginReport(login_report_id=login_report.id,
                                                                  total_login_count=total_login_count,
                                                                  total_login_successful=total_login_successful,
                                                                  total_login_failed=total_login_failed)
        blacklist_login_info_list = LoginInfo.objects.filter(blacklist=1).all()
        for blacklist_login_info in blacklist_login_info_list:
            blacklist_content_of_login_report = BlacklistContentOfLoginReport(login_report_id=login_report.id,
                                                                              blacklist_login_info_id=blacklist_login_info.id)
            blacklist_content_of_login_report.save()
        total_content_of_login_report.save()

        solar_panel_report_pdf = generate_solar_report_report_pdf(solar_panel_report.id)
        login_report_pdf = generate_login_report_pdf(login_report.id)
        send_email_with_solar_panel_report_pdf(solar_panel_report.id, solar_panel_report_pdf, "xiaohao6070@gmail.com")
        send_email_with_login_report_pdf(login_report.id, login_report_pdf, "xiaohao6070@gmail.com")


if __name__ == '__main__':
    auto_generate_report()
