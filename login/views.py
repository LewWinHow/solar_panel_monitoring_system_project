import uuid
import random
import re
import string
from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.storage import FileSystemStorage
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.core.validators import validate_email
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q
from django.views import View
from django.utils.timezone import now
from user_agents import parse
from user.models import User
from login.models import LoginInfo, LoginRecord
from general_func import hint_message
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from getmac import get_mac_address
from .models import LoginInfo, LoginRecord, LoginReport
from general_func import *


def get_device_info(request):
    ua_str = request.META.get("HTTP_USER_AGENT", "")
    user_agent = parse(ua_str)

    info = {
        "is_mobile": user_agent.is_mobile,
        "is_tablet": user_agent.is_tablet,
        "is_pc": user_agent.is_pc,
        "system": user_agent.os.family,
        "browser": user_agent.browser.family,
        "device": user_agent.device.family,
    }

    return info


class Login(View):

    def get(self, request):
        return render(request, "login/login.html")

    def post(self, request):
        ip = request.META.get("REMOTE_ADDR")
        mac = get_mac_address()
        device = get_device_info(request)
        print(device)
        username = request.POST.get("username")

        login_info = LoginInfo.objects.filter(ip=ip, mac=mac).first()
        if login_info:
            if login_info.blacklist == 1:
                return hint_message(
                    request, "Your IP/MAC has been blocked.", "login:login"
                )
        else:
            login_info = LoginInfo(
                ip=ip,
                mac=mac,
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
                password=password,
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
                password=password,
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
        if verify_network_address(request) is not True:
            return verify_network_address(request)

        user = request.user
        permission = 1 if user.is_superuser else (2 if not user.is_superuser and user.is_staff else 3)
        if not user.is_superuser and not user.is_staff:
            return redirect("login:login")

        login_info_list = LoginInfo.objects.all()
        paginator = Paginator(login_info_list, 10)
        page = page
        try:
            login_info_list = paginator.page(page)
        except PageNotAnInteger:
            login_info_list = paginator.page(1)
        except EmptyPage:
            login_info_list = paginator.page(paginator.num_pages)
        is_paginated = True if paginator.num_pages > 1 else False
        return render(request, "login/login_info.html", {"permission":permission,"login_info_list": login_info_list,"is_paginated":is_paginated})


class RecordOfLogin(LoginRequiredMixin, View):
    def get(self, request,page=1):
        if verify_network_address(request) is not True:
            return verify_network_address(request)

        user = request.user
        permission = 1 if user.is_superuser else (2 if not user.is_superuser and user.is_staff else 3)
        if not user.is_superuser and not user.is_staff:
            return redirect("login:login")

        login_record_list = LoginRecord.objects.all()
        paginator = Paginator(login_record_list, 10)
        page = page
        try:
            login_record_list = paginator.page(page)
        except PageNotAnInteger:
            login_record_list = paginator.page(1)
        except EmptyPage:
            login_record_list = paginator.page(paginator.num_pages)
        is_paginated = True if paginator.num_pages > 1 else False
        return render(request, "login/login_record.html", {"permission":permission,"login_record_list": login_record_list,"is_paginated":is_paginated})


class ReportOfLogin(LoginRequiredMixin, View):
    def get(self, request):
        if verify_network_address(request) is not True:
            return verify_network_address(request)

        user = request.user
        permission = 1 if user.is_superuser else (2 if not user.is_superuser and user.is_staff else 3)
        if not user.is_superuser and not user.is_staff:
            return redirect("login:login")

        login_report_list = LoginReport.objects.all().order_by('-created_time')

        return render(request, "login/login_report.html", {
            "permission": permission,
            "login_report_list": login_report_list
        })

    def post(self, request):
        if verify_network_address(request) is not True:
            return verify_network_address(request)

        current_time = now()
        month = current_time.month
        year = current_time.year

        if LoginReport.objects.filter(month=month, year=year).exists():
            messages.error(request, f"❌ Report for {month}/{year} already exists.")
            return redirect("login:login_report")

        LoginReport.objects.create(
            month=month,
            year=year
        )

        messages.success(request, f"✅ Report for {month}/{year} generated successfully.")
        return redirect("login:login_report")
    
def view_login_report_pdf(request, report_id):
    report = get_object_or_404(LoginReport, id=report_id)

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    p.setFont("Helvetica-Bold", 20)
    p.drawCentredString(width / 2, height - 2 * cm, "Login Monthly Report")

    p.setFont("Helvetica", 12)
    y = height - 3.5 * cm
    p.drawString(2.5 * cm, y, f"Report ID: {report.id}")
    y -= 0.8 * cm
    p.drawString(2.5 * cm, y, f"Month/Year: {report.month}/{report.year}")

    if is_naive(report.created_time):
        created_time = make_aware(report.created_time)
    else:
        created_time = report.created_time

    created_time_local = localtime(created_time)
    y -= 0.8 * cm
    p.drawString(2.5 * cm, y, f"Created Time: {created_time_local.strftime('%Y-%m-%d %H:%M:%S')}")

    total_login = LoginRecord.objects.filter(
        recorded_time__year=report.year, recorded_time__month=report.month
    ).count()
    failed_login = LoginRecord.objects.filter(
        recorded_time__year=report.year, recorded_time__month=report.month, status=0
    ).count()
    successful_login = LoginRecord.objects.filter(
        recorded_time__year=report.year, recorded_time__month=report.month, status=1
    ).count()

    y -= 1.5 * cm
    p.setFont("Helvetica-Bold", 14)
    p.drawString(2.5 * cm, y, "Summary")

    p.setFont("Helvetica", 12)
    y -= 0.8 * cm
    p.drawString(3 * cm, y, f"Total login attempts: {total_login}")
    y -= 0.6 * cm
    p.drawString(3 * cm, y, f"Successful logins: {successful_login}")
    y -= 0.6 * cm
    p.drawString(3 * cm, y, f"Failed logins: {failed_login}")

    p.setFont("Helvetica-Oblique", 10)
    p.drawRightString(width - 2 * cm, 1.5 * cm, "Page 1")

    p.showPage()
    p.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f"LoginReport-{report.id}.pdf")


class LoginBlacklist(LoginRequiredMixin, View):
    def get(self, request, id):
        if verify_network_address(request) is not True:
            return verify_network_address(request)

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
        if verify_network_address(request) is not True:
            return verify_network_address(request)

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
        if verify_network_address(request) is not True:
            return verify_network_address(request)
        user = request.user
        if not user.is_superuser:
            return redirect("login:login")
        login_record = LoginRecord.objects.filter(id=id).first()
        if not login_record:
            return hint_message(request, "Login info not found.", "login:login_info")
        login_record.delete()
        return redirect("login:login_record")
