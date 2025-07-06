import datetime
import json
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models.functions import ExtractMinute
from django.db.transaction import savepoint
from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.template.context_processors import request
from django.utils.dateparse import parse_datetime
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.utils.timezone import now
from getmac import get_mac_address

from login.models import LoginInfo
import solar_panel
from .models import SolarPanel, SolarPanelRecord, AVGTemperatureByZone, AVGTemperatureByTime
from django.db.models import Avg, Count
from django.utils import timezone
from collections import OrderedDict
from django.views import View
from django.shortcuts import render, get_object_or_404
from django.http import FileResponse
from .models import SolarPanelReportt
from django.utils.timezone import now
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from django.contrib import messages
from django.utils.timezone import make_aware, localtime, is_naive
from io import BytesIO
import io
import os
from solar_panel import models
from solar_panel.models import SolarPanel, SolarPanelRecord, SolarPanelMonitoring, SolarPanelReportt
from . import views
from general_func import *
from ai_model.image_detect_model.program import detect_solar_panel


class SolarPanelInfo(LoginRequiredMixin, View):

    def get(self, request, page=1):
        if verify_network_address(request) is not True:
            return verify_network_address(request)

        user = request.user
        permission = 1 if user.is_superuser else (2 if not user.is_superuser and user.is_staff else 3)
        solar_panel_list = SolarPanel.objects.all()
        solar_panel_list = get_data_by_page(solar_panel_list, page)[0]
        is_paginated = get_data_by_page(solar_panel_list, page)[1]
        return render(request, 'solar_panel/solar_panel_info.html',
                      {"permission": permission, "solar_panel_list": solar_panel_list,
                       'is_paginated': is_paginated})

    def post(self, request, page=1):
        if verify_network_address(request) is not True:
            return verify_network_address(request)

        user = request.user
        permission = 1 if user.is_superuser else (2 if not user.is_superuser and user.is_staff else 3)
        filter_select = request.POST.get("filter_select") or None
        filter_input = request.POST.get("filter_input") or None

        filter_input_second = request.POST.get("filter_input_second") or None
        status_select = request.POST.get("status_select") or None
        solar_panel_list = SolarPanel.objects.all()
        order_by = request.POST.get("order_by") or None

        if filter_select:
            if filter_select == "1":
                solar_panel_list = SolarPanel.objects.all()
            elif filter_select == "2":
                if filter_input:
                    solar_panel_list = SolarPanel.objects.filter(id=filter_input).all()
            elif filter_select == "3":
                if filter_input:
                    solar_panel_list = SolarPanel.objects.filter(name__contains=filter_input).all()
            elif filter_select == "4":
                if filter_input:
                    solar_panel_list = SolarPanel.objects.filter(zone=filter_input).all()
            elif filter_select == "5":
                solar_panel_list = SolarPanel.objects.filter(status=status_select).all()
            elif filter_select == "6":
                if filter_input and filter_input_second:
                    solar_panel_list = SolarPanel.objects.filter(created_time__gte=filter_input,
                                                                 created_time__lte=filter_input_second).all()
                elif filter_input and filter_input_second is None:
                    solar_panel_list = SolarPanel.objects.filter(created_time__gte=filter_input).all()
                elif filter_input is None and filter_input_second:
                    solar_panel_list = SolarPanel.objects.filter(created_time__lte=filter_input_second).all()
                else:
                    solar_panel_list = SolarPanel.objects.all()
            else:
                solar_panel_list = SolarPanel.objects.all()
        else:
            solar_panel_list = SolarPanel.objects.all()

        if order_by and order_by == "2":
            solar_panel_list = solar_panel_list.order_by("-id")
        else:
            solar_panel_list = solar_panel_list.order_by("id")

        solar_panel_list = get_data_by_page(solar_panel_list, page)[0]
        is_paginated = get_data_by_page(solar_panel_list, page)[1]

        return render(request, 'solar_panel/solar_panel_info.html',
                      {"permission": permission, "solar_panel_list": solar_panel_list, "is_paginated": is_paginated,
                       "filter_select": filter_select, "filter_input": filter_input,
                       "filter_input_second": filter_input_second, "status_select": status_select,
                       "order_by": order_by})


class SolarPanelStatus(LoginRequiredMixin, View):

    def get(self, request, id):
        if verify_network_address(request) is not True:
            return verify_network_address(request)

        solar_panel = SolarPanel.objects.get(id=id)

        if solar_panel is None:
            return hint_message(
                request, "Solar Panel Not Found.", "solar_panel:solar_panel_info"
            )

        if solar_panel.status:
            solar_panel.status = False
        else:
            solar_panel.status = True

        solar_panel.save()
        return redirect("solar_panel:solar_panel_info")


class AddSolarPanel(LoginRequiredMixin, View):

    def get(self, request):
        if verify_network_address(request) is not True:
            return verify_network_address(request)

        user = request.user
        if not user.is_superuser:
            return redirect("login:login")

        return render(request, "solar_panel/add_edit_solar_panel.html", {"page": "add_solar_panel"})

    def post(self, request):
        if verify_network_address(request) is not True:
            return verify_network_address(request)

        user = request.user
        if not user.is_superuser:
            return redirect("login:login")

        name = request.POST.get("name") or None

        if len(name) > 150:
            return hint_message(
                request,
                "Name must be less than 150 characters.",
                "solar_panel:add_solar_panel",
            )

        zone = request.POST.get("zone") or None
        position = request.POST.get("position") or None
        solar_panel = models.SolarPanel.objects.filter(
            zone=zone, position=position
        ).first()

        if solar_panel:
            return hint_message(
                request, "This position already exists.", "solar_panel:add_solar_panel"
            )

        temperature_threshold = float(request.POST.get("temperature_threshold")) or None

        if temperature_threshold < 0:
            return hint_message(
                request,
                "Temperature must be greater than 0.",
                "solar_panel:add_solar_panel",
            )

        status = request.POST.get("status") or None

        if SolarPanel.objects.exists():
            id = SolarPanel.objects.last().id
            solar_panel = SolarPanel(
                id=id + 1,
                name=name,
                zone=zone,
                position=position,
                temperature_threshold=temperature_threshold,
                status=status,
            )
            solar_panel.save()
        else:
            solar_panel = SolarPanel(
                id=1,
                name=name,
                zone=zone,
                position=position,
                temperature_threshold=temperature_threshold,
                status=status,
            )
            solar_panel.save()

        return hint_message(request, "Add Successful!", "solar_panel:solar_panel_info")


class DeleteSolarPanel(LoginRequiredMixin, View):

    def get(self, request, id):
        if verify_network_address(request) is not True:
            return verify_network_address(request)

        user = request.user
        if not user.is_superuser:
            return redirect("login:login")

        solar_panel = SolarPanel.objects.get(id=id)

        if solar_panel:
            solar_panel.delete()
            solar_panel_list = SolarPanel.objects.filter(id__gt=id).all()
            if solar_panel_list:
                for item in solar_panel_list:
                    item.id -= 1
                    item.save()
                solar_panel = SolarPanel.objects.last()
                solar_panel.delete()
            return hint_message(
                request, "Delete Successful!", "solar_panel:solar_panel_info"
            )
        else:
            return hint_message(
                request, "Solar Panel Not Found.", "solar_panel:solar_panel_info"
            )


class EditSolarPanel(LoginRequiredMixin, View):
    def get(self, request, id):
        if verify_network_address(request) is not True:
            return verify_network_address(request)

        user = request.user
        if not user.is_superuser:
            return redirect("login:login")

        solar_panel = SolarPanel.objects.filter(id=id).first()
        if solar_panel is None:
            return hint_message(
                request, "Solar Panel Not Found.", "solar_panel:solar_panel_info"
            )
        return render(request, "solar_panel/add_edit_solar_panel.html",
                      {"page": "edit_solar_panel", "solar_panel": solar_panel})

    def post(self, request, id):
        if verify_network_address(request) is not True:
            return verify_network_address(request)

        user = request.user
        if not user.is_superuser:
            return redirect("login:login")

        solar_panel = SolarPanel.objects.filter(id=id).first()
        if solar_panel is None:
            return hint_message(
                request, "Solar Panel Not Found.", "solar_panel:solar_panel_info"
            )

        name = request.POST.get("name") or None
        if len(name) > 150:
            return hint_message(
                request,
                "Name must be less than 150 characters.",
                "solar_panel:add_solar_panel",
            )

        zone = request.POST.get("zone") or None
        position = request.POST.get("position") or None

        solar_panel = models.SolarPanel.objects.filter(zone=zone, position=position).exclude(id=id).first()

        if solar_panel:
            return hint_message(
                request, "This position already exists.", "solar_panel:add_solar_panel"
            )

        temperature_threshold = float(request.POST.get("temperature_threshold")) or None

        if temperature_threshold < 0:
            return hint_message(
                request,
                "Temperature must be greater than 0.",
                "solar_panel:add_solar_panel",
            )

        status = request.POST.get("status") or None

        solar_panel = models.SolarPanel.objects.filter(id=id).first()
        solar_panel.name = name
        solar_panel.zone = zone
        solar_panel.position = position
        solar_panel.temperature_threshold = temperature_threshold
        solar_panel.status = status
        solar_panel.save()

        return hint_message(
            request, "Edit Successful!", "solar_panel:solar_panel_info"
        )


class MonitoringSolarPanel(LoginRequiredMixin, View):

    def get(self, request):
        if verify_network_address(request) is not True:
            return verify_network_address(request)

        monitoring_list = SolarPanelMonitoring.objects.filter(solar_panel__status=1).all()
        zones = []
        all_zone_monitoring = {}
        for monitoring in monitoring_list:
            if monitoring.solar_panel.zone not in zones:
                zones.append(monitoring.solar_panel.zone)
        zones.sort()
        for zone in zones:
            monitoring_list_by_zone = SolarPanelMonitoring.objects.filter(solar_panel__status=1,
                                                                          solar_panel__zone=zone).all().order_by(
                "solar_panel__position")
            all_zone_monitoring[str(zone)] = monitoring_list_by_zone

        count_status = SolarPanelMonitoring.objects.filter(solar_panel__status=1).values("status").annotate(
            count=Count("id"))
        count_damage = SolarPanelMonitoring.objects.filter(solar_panel__status=1).values("damage").annotate(
            count=Count("id"))
        count_cleanliness = SolarPanelMonitoring.objects.filter(solar_panel__status=1).values("cleanliness").annotate(
            count=Count("id"))

        data = []
        all_avg_tmp_by_time = AVGTemperatureByTime.objects.annotate(minute=ExtractMinute("recorded_time")).filter(
            minute__in=[0, 10, 20, 30, 40, 50])
        for avg_tmp_by_time in all_avg_tmp_by_time:
            avg_tmp_by_zone = AVGTemperatureByZone.objects.filter(AVGTemperatureByTime_id=avg_tmp_by_time.id).values(
                "zone", "avg_temperature")
            data2 = {avg_tmp_by_time.recorded_time.strftime("%H:%M"): avg_tmp_by_zone}
            data.append(data2)

        context = {"all_zone_monitoring": all_zone_monitoring, "count_status": count_status,
                   "count_damage": count_damage, "count_cleanliness": count_cleanliness, "data": data}

        user = request.user
        permission = 1 if user.is_superuser else (2 if not user.is_superuser and user.is_staff else 3)
        return render(request, "solar_panel/solar_panel_monitoring.html",
                      {"permission": permission, "context": context})


class RecordOfSolarPanel(LoginRequiredMixin, View):

    def get(self, request, page=1):
        if verify_network_address(request) is not True:
            return verify_network_address(request)

        solar_panel_record_list = SolarPanelRecord.objects.all()
        solar_panel_record_list = get_data_by_page(solar_panel_record_list, page)[0]
        is_paginated = get_data_by_page(solar_panel_record_list, page)[1]
        user = request.user
        permission = 1 if user.is_superuser else (2 if not user.is_superuser and user.is_staff else 3)
        return render(request, "solar_panel/solar_panel_record.html",
                      {"permission": permission, "solar_panel_record_list": solar_panel_record_list,
                       "is_paginated": is_paginated})

    def post(self, request):
        if verify_network_address(request) is not True:
            return verify_network_address(request)
        
        user = request.user
        permission = 1 if user.is_superuser else (2 if not user.is_superuser and user.is_staff else 3)
        
        filter_select = request.POST.get("filter_select") or None
        filter_input = request.POST.get("filter_input") or None

        filter_input_second = request.POST.get("filter_input_second") or None
        status_select = request.POST.get("status_select") or None
        damage_select = request.POST.get("damage_select") or None
        cleanliness_select = request.POST.get("cleanliness_select") or None
        solar_panel_list = SolarPanel.objects.all()
        order_by = request.POST.get("order_by") or None

        if filter_select:
            if filter_select == "1":
                solar_panel_list = SolarPanelRecord.objects.all()
            elif filter_select == "2":
                if filter_input:
                    solar_panel_list = SolarPanelRecord.objects.filter(id=filter_input).all()
            elif filter_select == "3":
                if filter_input:
                    solar_panel_list = SolarPanelRecord.objects.filter(name__contains=filter_input).all()
            elif filter_select == "4":
                if filter_input:
                    solar_panel_list = SolarPanelRecord.objects.filter(zone=filter_input).all()
            elif filter_select == "5":
                solar_panel_list = SolarPanelRecord.objects.filter(status=status_select).all()
            elif filter_select == "6":
                solar_panel_list = SolarPanelRecord.objects.filter(damage=damage_select).all()
            elif filter_select == "7":
                solar_panel_list = SolarPanelRecord.objects.filter(cleanliness=cleanliness_select).all()
            elif filter_select == "8":
                if filter_input and filter_input_second:
                    solar_panel_list = SolarPanelRecord.objects.filter(created_time__gte=filter_input,
                                                                 created_time__lte=filter_input_second).all()
                elif filter_input and filter_input_second is None:
                    solar_panel_list = SolarPanelRecord.objects.filter(created_time__gte=filter_input).all()
                elif filter_input is None and filter_input_second:
                    solar_panel_list = SolarPanelRecord.objects.filter(created_time__lte=filter_input_second).all()
                else:
                    solar_panel_list = SolarPanelRecord.objects.all()
            else:
                solar_panel_list = SolarPanelRecord.objects.all()
        else:
            solar_panel_list = SolarPanelRecord.objects.all()

        if order_by and order_by == "2":
            solar_panel_record_list = solar_panel_record_list.order_by("-id")
        else:
            solar_panel_record_list = solar_panel_record_list.order_by("id")

        solar_panel_record_list = get_data_by_page(solar_panel_record_list, page)[0]
        is_paginated = get_data_by_page(solar_panel_record_list, page)[1]        
        return render(request, "solar_panel/solar_panel_record.html",
                      {"permission": permission, "solar_panel_record_list": solar_panel_record_list})


class ReportOfSolarPanel(LoginRequiredMixin, View):
    def get(self, request, page=1):
        if verify_network_address(request) is not True:
            return verify_network_address(request)

        user = request.user
        permission = 1 if user.is_superuser else (2 if user.is_staff else 3)

        reports = SolarPanelReportt.objects.all().order_by('-generated_time')

        return render(request, "solar_panel/solar_panel_report.html", {
            "permission": permission,
            "reports": reports
        })

    def post(self, request):
        if verify_network_address(request) is not True:
            return verify_network_address(request)

        current_time = now()
        month = current_time.month
        year = current_time.year

        if SolarPanelReportt.objects.filter(month=month, year=year).exists():
            messages.error(request, f"❌ Report for {month}/{year} already exists.")
            return redirect("solar_panel:solar_panel_report")

        records = SolarPanelRecord.objects.filter(
            recorded_time__year=year, recorded_time__month=month
        )

        total_panels = records.values("solar_panel").distinct().count()
        total_records = records.count()

        status_count = {
            1: records.filter(status=1).count(),
            2: records.filter(status=2).count(),
            3: records.filter(status=3).count(),
            4: records.filter(status=4).count(),
            5: records.filter(status=5).count(),
        }

        SolarPanelReportt.objects.create(
            month=month,
            year=year
        )

        messages.success(request, f"✅ Report for {month}/{year} generated successfully.")
        return redirect("solar_panel:solar_panel_report")


# 📄 查看 PDF 页面（inline 显示）
def view_report_pdf(request, report_id):
    report = get_object_or_404(SolarPanelReportt, id=report_id)

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Title
    p.setFont("Helvetica-Bold", 20)
    p.drawCentredString(width / 2, height - 2 * 72 / 2.54, "Solar Panel Monthly Report")

    # Basic Info
    p.setFont("Helvetica", 12)
    y = height - 3.5 * 72 / 2.54
    p.drawString(2.5 * 72 / 2.54, y, f"Report ID: {report.id}")
    y -= 0.8 * 72 / 2.54
    p.drawString(2.5 * 72 / 2.54, y, f"Month/Year: {report.month}/{report.year}")

    if is_naive(report.generated_time):
        generated_time = make_aware(report.generated_time)
    else:
        generated_time = report.generated_time

    generated_time_local = localtime(generated_time)
    y -= 0.8 * 72 / 2.54
    p.drawString(2.5 * 72 / 2.54, y, f"Generated Time: {generated_time_local.strftime('%Y-%m-%d %H:%M:%S')}")

    # Records Summary
    records = SolarPanelRecord.objects.filter(
        recorded_time__year=report.year, recorded_time__month=report.month
    )

    total_panels = records.values("solar_panel").distinct().count()
    total_records = records.count()

    status_count = {
        1: records.filter(status=1).count(),
        2: records.filter(status=2).count(),
        3: records.filter(status=3).count(),
        4: records.filter(status=4).count(),
        5: records.filter(status=5).count(),
    }

    y -= 1.5 * 72 / 2.54
    p.setFont("Helvetica-Bold", 14)
    p.drawString(2.5 * 72 / 2.54, y, "Summary")

    p.setFont("Helvetica", 12)
    y -= 0.8 * 72 / 2.54
    p.drawString(3 * 72 / 2.54, y, f"Total Solar Panels Monitored: {total_panels}")
    y -= 0.6 * 72 / 2.54
    p.drawString(3 * 72 / 2.54, y, f"Total Records Collected: {total_records}")

    y -= 1.0 * 72 / 2.54
    p.drawString(3 * 72 / 2.54, y, f"Status Counts:")
    y -= 0.6 * 72 / 2.54
    p.drawString(4 * 72 / 2.54, y, f"Normal: {status_count[1]}")
    y -= 0.5 * 72 / 2.54
    p.drawString(4 * 72 / 2.54, y, f"Temperature High: {status_count[2]}")
    y -= 0.5 * 72 / 2.54
    p.drawString(4 * 72 / 2.54, y, f"Temperature Too High: {status_count[3]}")
    y -= 0.5 * 72 / 2.54
    p.drawString(4 * 72 / 2.54, y, f"Stopped: {status_count[4]}")
    y -= 0.5 * 72 / 2.54
    p.drawString(4 * 72 / 2.54, y, f"On Fire: {status_count[5]}")

    # Footer
    p.setFont("Helvetica-Oblique", 10)
    p.drawRightString(width - 2 * 72 / 2.54, 1.5 * 72 / 2.54, "Page 1")

    p.showPage()
    p.save()

    buffer.seek(0)

    download = request.GET.get('download')
    if download == "1":
        return FileResponse(buffer, as_attachment=True, filename=f"SolarPanelReport-{report.month}-{report.year}.pdf")
    else:
        return FileResponse(buffer, as_attachment=False, filename=f"SolarPanelReport-{report.month}-{report.year}.pdf")


@method_decorator(csrf_exempt, name="dispatch")
class ReceiveSolarPanel(View):

    def post(self, request):

        data = request.POST.get("solar_panel_json")
        image = request.FILES.get("solar_panel_image")

        data = json.loads(data)

        all_detect_result = detect_solar_panel(image)
        detect_result = None
        for key, value in all_detect_result.items():
            if key == "detections":
                detect_result = value

        detect_label = ["bird_drop", "clean", "damage", "dusty"]
        result_label = []

        for result in detect_result:
            result_label.append(result["class"])

        damage = 0
        cleanliness = 1

        if "clean" in result_label and not "bird_drop" in result_label and not "dusty" in result_label:
            cleanliness = 1
        if "dusty" in result_label and not "bird_drop" in result_label and not "clean" in result_label:
            cleanliness = 2
        if "bird_drop" in result_label and not "clean" in result_label:
            cleanliness = 3
        if "damage" in result_label:
            damage = 1

        solar_panel = SolarPanel.objects.filter(id=data["id"]).first()

        if not solar_panel:
            return HttpResponse("Solar Panel Not Found.")

        old_monitoring = SolarPanelMonitoring.objects.filter(
            solar_panel_id=data["id"]
        ).first()

        status = data["status"] if data["status"] < 6 else 6
        # damage = data["damage"] if data["damage"] < 2 else 2
        # cleanliness = data["cleanliness"] if data["cleanliness"] < 4 else 4
        record = SolarPanelRecord(
            solar_panel_id=data["id"],
            temperature=data["temperature"],
            status=status,
            damage=damage,
            cleanliness=cleanliness,
            recorded_time=datetime.time,
        )
        record.save()

        if old_monitoring:
            old_monitoring.temperature = data["temperature"]
            old_monitoring.status = status
            old_monitoring.damage = damage
            old_monitoring.cleanliness = cleanliness
            old_monitoring.save()
        else:

            new_monitoring = SolarPanelMonitoring(
                solar_panel_id=data["id"],
                temperature=data["temperature"],
                status=status,
                damage=damage,
                cleanliness=cleanliness,
            )
            new_monitoring.save()

        all_zone_avg_tmp = SolarPanelMonitoring.objects.values('solar_panel__zone').annotate(avg_tmp=Avg("temperature"))
        recorded_time = datetime.datetime.now()
        avg_tmp_by_time = AVGTemperatureByTime(recorded_time=recorded_time)
        for zone_avg_tmp in all_zone_avg_tmp:
            zone = None
            avg_tmp = None
            for key, value in zone_avg_tmp.items():
                if key == "solar_panel__zone":
                    zone = value
                if key == "avg_tmp":
                    avg_tmp = value
            avg_tmp_by_time.save()
            avg_tmp_by_zone = AVGTemperatureByZone(zone=zone, avg_temperature=avg_tmp,
                                                   AVGTemperatureByTime_id=avg_tmp_by_time.id)
            avg_tmp_by_zone.save()

        return HttpResponse("Solar Panel Receive Successful!")


class DeleteSolarPanelRecord(LoginRequiredMixin, View):

    def get(self, request, id):
        if verify_network_address(request) is not True:
            return verify_network_address(request)
        user = request.user
        if not user.is_superuser:
            return redirect("login:login")
        solar_panel_record = SolarPanelRecord.objects.filter(id=id).first()
        if not solar_panel_record:
            return hint_message(request, "Solar Panel Record Not Found.", "solar_panel:solar_panel_record")
        solar_panel_record.delete()
        return redirect("solar_panel:solar_panel_record")
