import uuid

from django.core.files.storage import FileSystemStorage
from django.core.paginator import PageNotAnInteger, EmptyPage, Paginator
from django.db.models import Q
from django.shortcuts import render
from getmac import get_mac_address
import re

from login.models import LoginInfo
from user.models import User


def hint_message(request, messages, redirect, id=None):
    messages = {
        "message": messages,
        "id": id,
        "redirect": redirect,
    }
    return render(request, "hint_message.html", messages)


def verify_network_address(request):
    ip = request.META.get("REMOTE_ADDR")
    mac = get_mac_address()
    network_address = LoginInfo.objects.filter(ip=ip, mac=mac).first()
    if network_address:
        if network_address.blacklist:
            return hint_message(request, "Your IP/MAC has been blocked.", "login:login")

    return True


def verify_username(request, username, redirect, id=""):
    if not username:
        return hint_message(request, "Username cannot empty.", "login:login")

    if len(username) > 150:
        return hint_message(request, "Username cannot exceed 150 characters.", redirect, id)

    pattern = r"^\S+$"
    if not re.match(pattern, username):
        return hint_message(request, "Username cannot contain spacing.", redirect, id)

    return True


def verify_password(request, password, confirm_password, redirect, id=""):
    if not password:
        return hint_message(request, "Password cannot empty.", "login:login")

    if not confirm_password:
        return hint_message(request, "Confirm password cannot empty.", "login:login")

    if len(password) < 8:
        return hint_message(request, "Password must be at least 8 characters.", redirect, id)

    if len(password) > 128:
        return hint_message(request, "Password cannot exceed 128 characters.", redirect, id)

    if password != confirm_password:
        return hint_message(request, "Passwords does not match.", redirect, id)

    return True


def verify_first_last_name(request, first_name, last_name, redirect, id=""):
    if not first_name:
        return hint_message(request, "First name cannot empty.", "login:login")

    if not last_name:
        return hint_message(request, "Last name cannot empty.", "login:login")

    if len(first_name) > 150:
        return hint_message(request, "First name cannot exceed 150 characters.", redirect, id)

    if len(last_name) > 150:
        return hint_message(request, "Last name cannot exceed 150 characters.", redirect, id)

    return True


def verify_phone(request, phone, redirect, id=""):
    if phone:
        pattern = r'^(?:\+?60|0)(1[0-9]{1}|[3-9])[0-9]{7,8}$'
        if not re.match(pattern, phone):
            return hint_message(request, "Invalid phone number.", redirect, id)

    return True


def verify_user_exists(request, username, email, phone, redirect, id=""):
    if id == "":
        user = User.objects.filter(Q(username=username) | Q(email=email) | Q(phone=phone, phone__isnull=False)).first()
    else:
        user = User.objects.filter(Q(username=username) | Q(email=email) | Q(phone=phone, phone__isnull=False)).exclude(
            id=id).first()

    if user:
        return hint_message(request, "Username, email or phone number already exists.", redirect, id)

    return True


def verify_image(request, image, redirect, id=""):
    if image:
        if not image.content_type.startswith("image/"):
            return hint_message(request, "Invalid file type. Please upload an image.", redirect, id)
        if image.size > 100 * 1024 * 1024:
            return hint_message(request, "File too large. Maximum size is 100MB.", redirect, id)

    return True

def get_data_by_page(data, page):
    paginator = Paginator(data, 10)
    page = page
    try:
        data = paginator.page(page)
    except PageNotAnInteger:
        data = paginator.page(1)
    except EmptyPage:
        data = paginator.page(paginator.num_pages)
    is_paginated = True if paginator.num_pages > 1 else False

    return [data, is_paginated]
