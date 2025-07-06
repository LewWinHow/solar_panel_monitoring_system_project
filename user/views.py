import os
import re
import uuid
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator
from django.core.validators import validate_email
from django.db.models import Q
from django.shortcuts import render, redirect
from django.template.context_processors import request
from django.views import View
from getmac import get_mac_address
from solar_panel_monitoring_system_project import settings
from user.models import User
from general_func import *

class Register(View):
    def get(self, request):
        return render(request, "user/register_add_edit_info_user.html", {"permission":None,"page":"register"})

    def post(self, request):
        username = request.POST.get("username") or None
        if verify_username(request, username, "login:register") is not True:
            return verify_username(request, username, "login:register")

        password = request.POST.get("password") or None
        confirm_password = request.POST.get("confirm_password") or None
        if verify_password(request, password, confirm_password, "login:register") is not True:
            return verify_password(request, password, confirm_password, "login:register")

        first_name = request.POST.get("first_name") or None
        last_name = request.POST.get("last_name") or None
        if verify_first_last_name(request, first_name, last_name, "login:register") is not True:
            return verify_first_last_name(request, first_name, last_name, "login:register")

        birthday = request.POST.get("birthday") or None
        gender = request.POST.get("gender") or None
        phone = request.POST.get("phone") or None

        if verify_phone(request, phone, "login:register") is not True:
            return verify_phone(request, phone, "login:register")

        if phone:
            if phone[0] != "6":
                phone = "6" + phone

        email = request.POST.get("email") or None
        if validate_email(email) is False:
            return hint_message(request, "Invalid email.", "login:register")

        if verify_user_exists(request, username, email, phone, "login:register") is not True:
            return verify_user_exists(request, username, email, phone, "login:register")

        image_url = None
        profile = request.FILES.get("profile") or None
        if verify_image(request, profile, "login:register") is not True:
            return verify_image(request, profile, image_url, "login:register")

        if profile:
            fs = FileSystemStorage()
            image_new_name = f"{uuid.uuid4()}.{profile.name.split('.')[-1]}"
            filename = fs.save(image_new_name, profile)
            image_url = fs.url(filename)

        user = User(
            username=username,
            first_name=first_name,
            last_name=last_name,
            birthday=birthday,
            gender=gender,
            phone=phone,
            email=email,
            is_superuser=False,
            is_staff=False,
            is_active=True,
            profile=image_url,
        )
        user.set_password(password)
        user.save()
        return hint_message(request, "Register successful!", "login:login")

class UserList(LoginRequiredMixin, View):

    def get(self, request,page=1):
        if verify_network_address(request) is not True:
            return verify_network_address(request)

        user = request.user
        permission = 1 if user.is_superuser else (2 if not user.is_superuser and user.is_staff else 3)
        if not user.is_superuser and not user.is_staff:
            return redirect("login:login")

        user_list = User.objects.all()
        paginator = Paginator(user_list, 10)
        page = page
        try:
            user_list = paginator.page(page)
        except PageNotAnInteger:
            user_list = paginator.page(1)
        except EmptyPage:
            user_list = paginator.page(paginator.num_pages)
        is_paginated = True if paginator.num_pages > 1 else False
        return render(request, "user/user_list.html", {"permission":permission,"user_list": user_list,"is_paginated":is_paginated})

    def post(self, request):
        if verify_network_address(request) is not True:
            return verify_network_address(request)

        user = request.user
        permission = 1 if user.is_superuser else (2 if not user.is_superuser and user.is_staff else 3)
        if not user.is_superuser or not user.is_staff:
            return redirect("login:login")

        users = User.objects.all()

        return render(request, "user/user_list.html", {"permission":permission,"users": users})


class AddUser(LoginRequiredMixin, View):

    def get(self, request):
        if verify_network_address(request) is not True:
            return verify_network_address(request)

        user = request.user
        permission  = 1 if user.is_superuser else (2 if not user.is_superuser and user.is_staff else 3)
        if not user.is_superuser:
            return redirect("login:login")

        return render(request, "user/register_add_edit_info_user.html", {"permission":permission,"page":"add_user"})

    def post(self, request):
        if verify_network_address(request) is not True:
            return verify_network_address(request)

        user = request.user
        if not user.is_superuser:
            return redirect("login:login")

        username = request.POST.get("username") or None
        if verify_username(request, username, "user:add_user") is not True:
            return verify_username(request, username, "user:add_user")

        password = request.POST.get("password") or None
        confirm_password = request.POST.get("confirm_password") or None
        if verify_password(request, password, confirm_password, "user:add_user") is not True:
            return verify_password(request, password, confirm_password, "user:add_user")

        first_name = request.POST.get("first_name") or None
        last_name = request.POST.get("last_name") or None
        if verify_first_last_name(request, first_name, last_name, "user:add_user") is not True:
            return verify_first_last_name(request, first_name, last_name, "user:add_user")

        birthday = request.POST.get("birthday") or None
        gender = request.POST.get("gender") or None
        phone = request.POST.get("phone") or None

        if verify_phone(request, phone, "user:add_user") is not True:
            return verify_phone(request, phone, "user:add_user")

        if phone:
            if phone[0] != "6":
                phone = "6" + phone

        email = request.POST.get("email") or None

        if validate_email(email) is False:
            return hint_message(request, "Invalid email.", "user:add_user")

        if verify_user_exists(request, username, email, phone, "user:add_user") is not True:
            return verify_user_exists(request, username, email, phone, "user:add_user")

        is_superuser = request.POST.get("is_superuser") or None
        is_staff = request.POST.get("is_staff") or None
        is_active = request.POST.get("is_active") or None

        profile = request.FILES.get("profile")
        image_url = None
        if verify_image(request, profile, "user:add_user") is not True:
            return verify_image(request, profile, "user:add_user")

        if profile:
            fs = FileSystemStorage()
            image_new_name = f"{uuid.uuid4()}.{profile.name.split('.')[-1]}"
            filename = fs.save(image_new_name, profile)
            image_url = fs.url(filename)

        user = User(
            username=username,
            first_name=first_name,
            last_name=last_name,
            birthday=birthday,
            gender=gender,
            phone=phone,
            email=email,
            is_superuser=is_superuser,
            is_staff=is_staff,
            is_active=is_active,
            profile=image_url,
        )

        user.set_password(password)

        user.save()
        return hint_message(request, "Add successful!", "user:user_list")


class DeleteUser(LoginRequiredMixin, View):

    def get(self, request, id):
        if verify_network_address(request) is not True:
            return verify_network_address(request)

        user = request.user
        if not user.is_superuser:
            return redirect("login:login")

        user = User.objects.filter(id=id).first()

        if user is None:
            return hint_message(request, "User not found.", "user:user_list")

        user.delete()
        return redirect("user:user_list")


class UserSatus(LoginRequiredMixin, View):

    def get(self, request, id):
        if verify_network_address(request) is not True:
            return verify_network_address(request)

        user = request.user
        if not user.is_superuser:
            return redirect("login:login")

        user = User.objects.filter(id=id).first()

        if user is None:
            return hint_message(request, "User not found.", "user:user_list")

        if user.is_active:
            user.is_active = False
        else:
            user.is_active = True

        user.save()
        return redirect("user:user_list")


class EditUser(LoginRequiredMixin, View):

    def get(self, request, id):
        if verify_network_address(request) is not True:
            return verify_network_address(request)

        user = request.user
        permission = 1 if user.is_superuser else (2 if not user.is_superuser and user.is_staff else 3)
        if not user.is_superuser:
            return redirect("login:login")

        user = User.objects.filter(id=id).first()

        if user is None:
            return hint_message(request, "User not found.", "user:user_list")

        return render(request, "user/register_add_edit_info_user.html", {"permission":permission,"page":"edit_user","user": user})

    def post(self, request, id):
        if verify_network_address(request) is not True:
            return verify_network_address(request)

        user = request.user
        if not user.is_superuser:
            return redirect("login:login")

        user = User.objects.filter(id=id).first()

        if user is None:
            return hint_message(request, "User not found.", "user:user_list")

        username = request.POST.get("username") or None
        if verify_username(request, username, "user:edit_user") is not True:
            return verify_username(request, username, "user:edit_user")

        password = request.POST.get("password") or None

        confirm_password = request.POST.get("confirm_password") or None

        if password or confirm_password:
            if verify_password(request, password, confirm_password, "user:edit_user") is not True:
                return verify_password(request, password, confirm_password, "user:edit_user")

        first_name = request.POST.get("first_name") or None
        last_name = request.POST.get("last_name") or None
        if verify_first_last_name(request, first_name, last_name, "user:edit_user") is not True:
            return verify_first_last_name(request, first_name, last_name, "user:edit_user")

        birthday = request.POST.get("birthday") or None

        gender = request.POST.get("gender") or None

        phone = request.POST.get("phone") or None

        if verify_phone(request, phone, "user:edit_user", id) is not True:
            return verify_phone(request, phone, "user:edit_user", id)

        if phone:
            if phone[0] != "6":
                phone = "6" + phone

        email = request.POST.get("email") or None
        if validate_email(email) is False:
            return hint_message(request, "Invalid email.", "user:edit_user", id)

        if verify_user_exists(request, username, email, phone, "user:edit_user", id) is not True:
            return verify_user_exists(request, username, email, phone, "user:edit_user", id)

        is_superuser = request.POST.get("is_superuser") or None
        is_staff = request.POST.get("is_staff") or None
        is_active = request.POST.get("is_active") or None

        profile = request.FILES.get("profile") or None
        image_url = None

        if verify_image(request, profile, "user:edit_user", id) is not True:
            return verify_image(request, "user:edit_user", id)

        if profile:
            fs = FileSystemStorage()
            image_new_name = f"{uuid.uuid4()}.{profile.name.split('.')[-1]}"
            filename = fs.save(image_new_name, profile)
            image_url = fs.url(filename)

        user.username = username
        if password:
            user.set_password(password)
        user.first_name = first_name
        user.last_name = last_name
        user.birthday = birthday
        user.gender = gender
        user.email = email
        user.phone = phone
        user.is_superuser = is_superuser
        user.is_staff = is_staff
        user.is_active = is_active
        if image_url:
            user.profile = image_url
        user.save()
        return hint_message(request, "Edit successful!", "user:user_list")


class UserInfo(LoginRequiredMixin, View):

    def get(self, request):
        if verify_network_address(request) is not True:
            return verify_network_address(request)

        user = request.user
        id = user.id
        permission = 1 if user.is_superuser else (2 if not user.is_superuser and user.is_staff else 3)
        user = User.objects.filter(id=id).first()

        if user is None:
            return hint_message(request, "User not found.", "login:login")

        return render(request, "user/register_add_edit_info_user.html", {"permission":permission,"page":"user_info","user": user})

    def post(self, request):
        if verify_network_address(request) is not True:
            return verify_network_address(request)

        user = request.user
        id = request.user.id
        user = User.objects.filter(id=id).first()

        if user is None:
            return hint_message(request, "User not found.", "login:login")

        username = request.POST.get("username") or None
        if verify_username(request, username, "user:user_info") is not True:
            return verify_username(request, username, "user:user_info")

        password = request.POST.get("password") or None

        confirm_password = request.POST.get("confirm_password") or None

        if password or confirm_password:
            if verify_password(request, password, confirm_password, "user:user_info") is not True:
                return verify_password(request, password, confirm_password, "user:user_info")

        first_name = request.POST.get("first_name") or None
        last_name = request.POST.get("last_name") or None
        if verify_first_last_name(request, first_name, last_name, "user:user_info") is not True:
            return verify_first_last_name(request, first_name, last_name, "user:user_info")

        birthday = request.POST.get("birthday") or None
        gender = request.POST.get("gender") or None
        phone = request.POST.get("phone") or None

        if verify_phone(request, phone, "user:user_info") is not True:
            return verify_phone(request, phone, "user:user_info")

        if phone:
            if phone[0] != "6":
                phone = "6" + phone

        email = request.POST.get("email") or None

        if validate_email(email) is False:
            return hint_message(
                request, "Invalid email.", "supervisor:supervisor_info"
            )

        if verify_user_exists(request, username, email, phone, "user:user_info", id) is not True:
            return verify_user_exists(request, username, email, phone, "user:user_info", id)

        is_superuser = request.POST.get("is_superuser") or user.is_superuser
        is_staff = request.POST.get("is_staff") or user.is_staff
        is_active = request.POST.get("is_active") or user.is_active

        profile = request.FILES.get("profile") or None
        image_url = None
        if verify_image(request, profile, image_url, "user:user_info") is not True:
            return verify_image(request, profile, image_url, "user:user_info")

        if profile:
            fs = FileSystemStorage()
            image_new_name = f"{uuid.uuid4()}.{profile.name.split('.')[-1]}"
            filename = fs.save(image_new_name, profile)
            image_url = fs.url(filename)

        user.username = username

        if password:
            user.set_password(password)
        user.first_name = first_name
        user.last_name = last_name
        user.birthday = birthday
        user.gender = gender
        user.email = email
        user.phone = phone
        user.is_superuser = is_superuser
        user.is_staff = is_staff
        user.is_active = is_active

        user.save()
        return hint_message(request, "Edit successful!", "solar_panel:solar_panel_info")
