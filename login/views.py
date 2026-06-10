import random
import string
from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.views import View
from login.models import TotalContentOfLoginReport, BlacklistContentOfLoginReport
from .models import LoginRecord, LoginReport
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from django.http import FileResponse
from django.utils.timezone import localtime, make_aware, is_naive
from reportlab.lib.units import cm
from utils.general_function import *





class Login(View):

    def get(self, request):
        return render(request, "login/login.html")

    def post(self, request):
        ip = request.META.get("REMOTE_ADDR")
        device_info = get_device_info(request)
        system = device_info["system"]
        device = device_info["device"]
        is_bot = device_info["is_bot"]
        username = request.POST.get("username")

        login_info = LoginInfo.objects.filter(ip=ip).first()
        if login_info:
            if is_bot:
                login_info.blacklist = 1
                login_info.save()
        else:
            if is_bot:
                login_info = LoginInfo(
                    ip=ip,
                    system=system,
                    device=device,
                    is_bot=is_bot,
                    blacklist=1,
                )
            else:
                login_info = LoginInfo(
                    ip=ip,
                    system=system,
                    device=device,
                    is_bot=is_bot,
                )
            login_info.save()

        pattern = r"^\S+$"
        if not re.match(pattern, username):
            return hint_message(request, "Invalid username.", "login:login")

        password = request.POST.get("password")

        if len(password) < 8:
            return hint_message(
                request, "Password must be at least 8 characters.", "login:login"
            )

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            login_info.failed_count = 0
            login_info.save()
            login_record = LoginRecord(
                login_info_id=login_info.id,
                username=username,
                status=1,
                recorded_time=datetime.now(),
            )
            login_record.save()
            return hint_message(
                request, "Login successful!", "solar_panel:solar_panel_info"
            )
        else:
            login_info.failed_count += 1
            login_info.save()
            if login_info.failed_count > 5:
                login_info.blacklist = 1
                login_info.save()

            login_record = LoginRecord(
                login_info_id=login_info.id,
                username=username,
                status=0,
                recorded_time=datetime.now(),
            )
            login_record.save()
            return hint_message(
                request, "Invalid username or password.", "login:login"
            )


class ForgotPassword(View):
    def get(self, request):
        return render(request, "login/forgot_password.html")

    def post(self, request):
        email = request.POST.get("email")
        user = User.objects.filter(email=email).first()
        if not user:
            return hint_message(
                request, "Email does not exist.", "login:forgot_password"
            )

        captcha_input = request.POST.get("captcha")
        captcha_generated = request.POST.get("hide_captcha")

        if captcha_input == captcha_generated:
            verification_code = "".join(
                random.choices(string.ascii_letters + string.digits, k=6)
            )
            request.session["email"] = email
            request.session["verification_code"] = verification_code

            send_mail(
                "Password Reset Verification Code",
                f"Your verification code is {verification_code}",
                "xiaohao6070@gmail.com",
                [email],
                fail_silently=False,
            )

            return hint_message(
                request,
                "Verification code sent to your email!",
                "login:verification_code",
            )
        else:
            return hint_message(
                request, "Captcha does not match.", "login:forgot_password"
            )


class VerificationCode(View):
    def get(self, request):
        email = request.session.get("email")
        verification_code = request.session.get("verification_code")
        if email is None or verification_code is None:
            return redirect("login:login")
        return render(request, "login/verification_code.html")

    def post(self, request):
        verification_code_input = request.POST.get("verification_code")
        verification_code_generated = request.session.get("verification_code")
        if verification_code_input == verification_code_generated:
            request.session["reset_password"] = True
            return hint_message(
                request, "Verification code correct!", "login:reset_password"
            )
        else:
            return hint_message(
                request, "Verification code does not match.", "login:verification_code"
            )


class ResetPassword(View):
    def get(self, request):
        email = request.session.get("email")
        reset_password = request.session.get("reset_password")
        if email is None or reset_password is None:
            return redirect("login:login")
        return render(request, "login/reset_password.html")

    def post(self, request):
        email = request.session.get("email")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if new_password == confirm_password:
            user = User.objects.filter(email=email).first()
            user.set_password(new_password)
            user.save()
            return hint_message(request, "Reset Password Successful!", "login:login")
        else:
            return hint_message(
                request, "Passwords do not match.", "login:reset_password"
            )


class Logout(View):
    def get(self, request):
        logout(request)
        return redirect("login:login")


class InfoOfLogin(LoginRequiredMixin, View):
    def get(self, request, page=1):


        user = request.user
        permission = 1 if user.is_superuser else (2 if not user.is_superuser and user.is_staff else 3)
        if not user.is_superuser and not user.is_staff:
            return redirect("login:login")

        login_info_list = LoginInfo.objects.all()
        login_info_list = get_data_by_page(login_info_list, page)[0]
        is_paginated = get_data_by_page(login_info_list, page)[1]
        return render(request, "login/login_info.html",
                      {"permission": permission, "login_info_list": login_info_list, "is_paginated": is_paginated})

    def post(self, request, page=1):


        user = request.user
        permission = 1 if user.is_superuser else (2 if not user.is_superuser and user.is_staff else 3)
        if not user.is_superuser and not user.is_staff:
            return redirect("login:login")

        filter_select = request.POST.get("filter_select") or None
        filter_input = request.POST.get("filter_input") or None
        blacklist_select = request.POST.get("blacklist_select") or None
        login_info_list = LoginInfo.objects.all()
        order_by = request.POST.get("order_by") or None

        if filter_select:
            if filter_select == "1":
                login_info_list = LoginInfo.objects.all()
            elif filter_select == "2":
                if filter_input:
                    login_info_list = LoginInfo.objects.filter(id=filter_input).all()
            elif filter_select == "3":
                if blacklist_select:
                    login_info_list = LoginInfo.objects.filter(blacklist=blacklist_select).all()

        if order_by and order_by == "2":
            login_info_list = login_info_list.order_by("-id")
        else:
            login_info_list = login_info_list.order_by("id")

        login_info_list = get_data_by_page(login_info_list, page)[0]
        is_paginated = get_data_by_page(login_info_list, page)[1]
        return render(request, "login/login_info.html",
                      {"permission": permission, "login_info_list": login_info_list,
                       "is_paginated": is_paginated, "filter_select": filter_select, "filter_input": filter_input,
                       "blacklist_select": blacklist_select, "order_by": order_by})


class RecordOfLogin(LoginRequiredMixin, View):
    def get(self, request, page=1):


        user = request.user
        permission = 1 if user.is_superuser else (2 if not user.is_superuser and user.is_staff else 3)
        if not user.is_superuser and not user.is_staff:
            return redirect("login:login")

        login_record_list = LoginRecord.objects.all()
        login_record_list = get_data_by_page(login_record_list, page)[0]
        is_paginated = get_data_by_page(login_record_list, page)[1]
        return render(request, "login/login_record.html",
                      {"permission": permission, "login_record_list": login_record_list, "is_paginated": is_paginated})

    def post(self, request, page=1):


        user = request.user
        permission = 1 if user.is_superuser else (2 if not user.is_superuser and user.is_staff else 3)
        if not user.is_superuser and not user.is_staff:
            return redirect("login:login")

        filter_select = request.POST.get("filter_select") or None
        filter_input = request.POST.get("filter_input") or None
        filter_input_second = request.POST.get("filter_input_second") or None
        status_select = request.POST.get("status_select") or None
        login_record_list = LoginRecord.objects.all()
        order_by = request.POST.get("order_by") or None

        if filter_select:
            if filter_select == "1":
                login_record_list = LoginRecord.objects.all()
            elif filter_select == "2":
                if filter_input:
                    login_record_list = LoginRecord.objects.filter(id=filter_input).all()
            elif filter_select == "3":
                if filter_input:
                    login_record_list = LoginRecord.objects.filter(login_info_id=filter_input).all()
            elif filter_select == "4":
                if status_select:
                    login_record_list = LoginRecord.objects.filter(status=status_select).all()
            elif filter_select == "5":
                if filter_input and filter_input_second:
                    login_record_list = LoginRecord.objects.filter(recorded_time__gte=filter_input,
                                                                         recorded_time__lte=filter_input_second).all()
                elif filter_input and filter_input_second is None:
                    login_record_list = LoginRecord.objects.filter(recorded_time__gte=filter_input).all()
                elif filter_input is None and filter_input_second:
                    login_record_list = LoginRecord.objects.filter(
                        recorded_time__lte=filter_input_second).all()

        if order_by and order_by == "2":
            login_record_list = login_record_list.order_by("-id")
        else:
            login_record_list = login_record_list.order_by("id")

        login_record_list = get_data_by_page(login_record_list, page)[0]
        is_paginated = get_data_by_page(login_record_list, page)[1]
        return render(request, "login/login_record.html",
                      {"permission": permission, "login_record_list": login_record_list,
                       "is_paginated": is_paginated, "filter_select": filter_select, "filter_input": filter_input,
                       "filter_input_second": filter_input_second, "status_select": status_select,
                       "order_by": order_by})


class ReportOfLogin(LoginRequiredMixin, View):
    def get(self, request,page=1):


        user = request.user
        permission = 1 if user.is_superuser else (2 if not user.is_superuser and user.is_staff else 3)
        if not user.is_superuser and not user.is_staff:
            return redirect("login:login")

        login_report_list = LoginReport.objects.all()
        login_report_list = get_data_by_page(login_report_list,page=1)[0]
        is_paginated = get_data_by_page(login_report_list, page)[1]
        dic = {"apple":5,"banana":5}

        return render(request, "login/login_report.html", {
            "permission": permission,
            "login_report_list": login_report_list,"is_paginated": is_paginated,
        })

    def post(self, request, page=1):


        user = request.user
        permission = 1 if user.is_superuser else (2 if user.is_staff else 3)
        filter_select = request.POST.get("filter_select") or None
        filter_input = request.POST.get("filter_input") or None
        login_report_list = LoginReport.objects.all()
        order_by = request.POST.get("order_by") or None

        if filter_select:
            if filter_select == "1":
                login_report_list = LoginReport.objects.all()
            elif filter_select == "2":
                if filter_input:
                    login_report_list = LoginReport.objects.filter(id=filter_input).all()
            elif filter_select == "3":
                if filter_input:
                    login_report_list = LoginReport.objects.filter(month=filter_input).all()
            elif filter_select == "4":
                if filter_input:
                    login_report_list = LoginReport.objects.filter(year=filter_input).all()

        if order_by and order_by == "2":
            login_report_list = login_report_list.order_by("-id")
        else:
            login_report_list = login_report_list.order_by("id")

        login_report_list = get_data_by_page(login_report_list, page)[0]
        is_paginated = get_data_by_page(login_report_list, page)[1]
        return render(request, "login/login_report.html",
                      {"permission": permission, "login_report_list": login_report_list,
                       "is_paginated": is_paginated, "filter_select": filter_select, "filter_input": filter_input,
                       "order_by": order_by})


class LoginReportPDFView(View):
    def get(self, request, id, download=0):
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
            p.drawString(18 * cm, y, ("Yes"if login_info.is_bot else "None"))

        # 页脚页码
        p.setFont("Helvetica-Oblique", 10)
        p.drawRightString(width - 2 * cm, 1.5 * cm, "Page 1")

        p.showPage()
        p.save()
        buffer.seek(0)
        if download == 0:
            return FileResponse(buffer, as_attachment=False, filename=f"LoginReport-{report.id}.pdf")
        else:
            return FileResponse(buffer, as_attachment=True, filename=f"LoginReport-{report.id}.pdf")

class LoginBlacklist(LoginRequiredMixin, View):
    def get(self, request, id):


        user = request.user
        if not user.is_superuser and not user.is_staff:
            return redirect("login:login")

        login_info = LoginInfo.objects.filter(id=id).first()
        if login_info:
            if login_info.blacklist:
                login_info.blacklist = False
                login_info.save()
            else:
                login_info.blacklist = True
                login_info.save()
            return redirect("login:login_info")
        else:
            return hint_message(request, "Login info not found.", "login:login_info")


class DeleteLoginInfo(LoginRequiredMixin, View):
    def get(self, request, id):


        user = request.user
        if not user.is_superuser:
            return redirect("login:login")

        login_info = LoginInfo.objects.filter(id=id).first()

        if not login_info:
            return hint_message(request, "Login info not found.", "login:login_info")

        login_info.delete()
        return redirect("login:login_info")


class DeleteLoginRecord(LoginRequiredMixin, View):
    def get(self, request, id):

        user = request.user
        if not user.is_superuser:
            return redirect("login:login")
        login_record = LoginRecord.objects.filter(id=id).first()
        if not login_record:
            return hint_message(request, "Login info not found.", "login:login_info")
        login_record.delete()
        return redirect("login:login_record")


class DeleteLoginReport(LoginRequiredMixin, View):
    def get(self, request, id):


        user = request.user
        if not user.is_superuser:
            return redirect("login:login")

        login_report = LoginReport.objects.filter(id=id).first()
        if not login_report:
            return hint_message(request, "Login report not found.", "login:login_report")

        login_report.delete()
        return redirect("login:login_report")