from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.validators import validate_email
from django.shortcuts import redirect
from django.views import View
from utils.general_function import *


class Register(View):
    def get(self, request):
        return render(request, "user/register_add_edit_info_user.html", {"permission": None, "page": "register"})

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
            fs = FileSystemStorage(location='media/profile', base_url='/media/profile/')
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

    def get(self, request, page=1):


        user = request.user
        permission = 1 if user.is_superuser else (2 if not user.is_superuser and user.is_staff else 3)
        if not user.is_superuser and not user.is_staff:
            return redirect("login:login")

        user_list = User.objects.all()
        user_list = get_data_by_page(user_list, page)[0]
        is_paginated = get_data_by_page(user_list, page)[1]
        return render(request, "user/user_list.html",
                      {"permission": permission, "user_list": user_list, "is_paginated": is_paginated})

    def post(self, request, page=1):


        user = request.user
        permission = 1 if user.is_superuser else (2 if not user.is_superuser and user.is_staff else 3)
        if not user.is_superuser or not user.is_staff:
            return redirect("login:login")

        filter_select = request.POST.get("filter_select") or None
        filter_input = request.POST.get("filter_input") or None
        filter_input_second = request.POST.get("filter_input_second") or None
        gender_select = request.POST.get("gender_select") or None
        supervisor_select = request.POST.get("supervisor_select") or None
        staff_select = request.POST.get("staff_select") or None
        status_select = request.POST.get("status_select") or None
        user_list = User.objects.all()
        order_by = request.POST.get("order_by") or None

        if filter_select:
            if filter_select == "1":
                user_list = User.objects.all()
            elif filter_select == "2":
                if filter_input:
                    user_list = User.objects.filter(id=filter_input).all()
            elif filter_select == "3":
                if filter_input:
                    user_list = User.objects.filter(username__contains=filter_input).all()
            elif filter_select == "4":
                if filter_input:
                    full_name = filter_input.strip().split()
                    if len(full_name) == 1:
                            Q(first_name__icontains=full_name[0]) | Q(last_name__icontains=full_name[0])
                    elif len(filter_input) >= 2:
                            Q(first_name__icontains=full_name[0]) | Q(last_name__icontains=full_name[-1])
            elif filter_select == "5":
                if gender_select:
                    user_list = User.objects.filter(gender=gender_select).all()
            elif filter_select == "6":
                if supervisor_select:
                    user_list = User.objects.filter(is_superuser=supervisor_select).all()
            elif filter_select == "7":
                if staff_select:
                    user_list = User.objects.filter(is_staff=staff_select).all()
            elif filter_select == "8":
                if status_select:
                    user_list = User.objects.filter(is_active=status_select).all()
            elif filter_select == "9":
                if filter_input and filter_input_second:
                    user_list = User.objects.filter(date_joined__gte=filter_input,
                                                                  date_joined__lte=filter_input_second).all()
                elif filter_input and filter_input_second is None:
                    user_list = User.objects.filter(date_joined__gte=filter_input).all()
                elif filter_input is None and filter_input_second:
                    user_list = User.objects.filter(
                        date_joined__lte=filter_input_second).all()

        if order_by and order_by == "2":
            user_list = user_list.order_by("-id")
        else:
            user_list = user_list.order_by("id")

        user_list = get_data_by_page(user_list, page)[0]
        is_paginated = get_data_by_page(user_list, page)[1]
        return render(request, "user/user_list.html",
                      {"permission": permission, "user_list": user_list,
                       "is_paginated": is_paginated, "filter_select": filter_select, "filter_input": filter_input,
                       "filter_input_second": filter_input_second, "gender_select": gender_select,
                       "supervisor_select": supervisor_select, "staff_select": staff_select,
                       "status_select": status_select,
                       "order_by": order_by})


class AddUser(LoginRequiredMixin, View):

    def get(self, request):


        user = request.user
        permission = 1 if user.is_superuser else (2 if not user.is_superuser and user.is_staff else 3)
        if not user.is_superuser:
            return redirect("login:login")

        return render(request, "user/register_add_edit_info_user.html", {"permission": permission, "page": "add_user"})

    def post(self, request):


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
            fs = FileSystemStorage(location='media/profile', base_url='/media/profile/')
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


        user = request.user
        permission = 1 if user.is_superuser else (2 if not user.is_superuser and user.is_staff else 3)
        if not user.is_superuser:
            return redirect("login:login")

        user = User.objects.filter(id=id).first()

        if user is None:
            return hint_message(request, "User not found.", "user:user_list")

        return render(request, "user/register_add_edit_info_user.html",
                      {"permission": permission, "page": "edit_user", "user": user})

    def post(self, request, id):


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
            fs = FileSystemStorage(location='media/profile', base_url='/media/profile/')
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


        user = request.user
        id = user.id
        permission = 1 if user.is_superuser else (2 if not user.is_superuser and user.is_staff else 3)
        user = User.objects.filter(id=id).first()

        if user is None:
            return hint_message(request, "User not found.", "login:login")

        return render(request, "user/register_add_edit_info_user.html",
                      {"permission": permission, "page": "user_info", "user": user})

    def post(self, request):


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
