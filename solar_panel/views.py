import io
import json
import datetime

from django.db.models import Count

from django.http import HttpResponse, FileResponse
from django.shortcuts import redirect, get_object_or_404

from django.utils.timezone import make_aware, localtime, is_naive
from django.utils.decorators import method_decorator

from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm

from solar_panel.models import (
    SolarPanelRecord,
    SolarPanelMonitoring,
    SolarPanelReport,
    ContentOfSolarPanelReport, SolarPanelDetectVideo,
)

from utils.general_function import *
from ai_model.detect_solar_panel_model.detect_solar_panel_with_image import detect_solar_panel_with_image
from solar_panel.models import SolarPanel
import os

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"


class SolarPanelInfo(LoginRequiredMixin, View):

    def get(self, request, page=1):

        user = request.user
        permission = 1 if user.is_superuser else (2 if not user.is_superuser and user.is_staff else 3)
        solar_panel_list = SolarPanel.objects.all()
        solar_panel_list = get_data_by_page(solar_panel_list, page)[0]
        is_paginated = get_data_by_page(solar_panel_list, page)[1]
        return render(request, 'solar_panel/solar_panel_info.html',
                      {"permission": permission, "solar_panel_list": solar_panel_list,
                       'is_paginated': is_paginated})

    def post(self, request, page=1):

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
                if status_select:
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

        user = request.user
        if not user.is_superuser:
            return redirect("login:login")

        return render(request, "solar_panel/add_edit_solar_panel.html", {"page": "add_solar_panel"})

    def post(self, request):

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
        solar_panel = SolarPanel.objects.filter(
            zone=zone, position=position
        ).first()

        if solar_panel:
            return hint_message(
                request, "This position already exists.", "solar_panel:add_solar_panel"
            )

        status = request.POST.get("status") or None

        if SolarPanel.objects.exists():
            id = SolarPanel.objects.last().id
            solar_panel = SolarPanel(
                id=id + 1,
                name=name,
                zone=zone,
                position=position,
                status=status,
            )
            solar_panel.save()
        else:
            solar_panel = SolarPanel(
                id=1,
                name=name,
                zone=zone,
                position=position,
                status=status,
            )
            solar_panel.save()

        return hint_message(request, "Add Successful!", "solar_panel:solar_panel_info")


class DeleteSolarPanel(LoginRequiredMixin, View):

    def get(self, request, id):

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

        solar_panel = SolarPanel.objects.filter(zone=zone, position=position).exclude(id=id).first()

        if solar_panel:
            return hint_message(
                request, "This position already exists.", "solar_panel:add_solar_panel"
            )

        status = request.POST.get("status") or None

        solar_panel = SolarPanel.objects.filter(id=id).first()
        solar_panel.name = name
        solar_panel.zone = zone
        solar_panel.position = position
        solar_panel.status = status
        solar_panel.save()

        return hint_message(
            request, "Edit Successful!", "solar_panel:solar_panel_info"
        )


class MonitoringSolarPanel(LoginRequiredMixin, View):

    def get(self, request):

        monitoring_list = SolarPanelMonitoring.objects.filter(solar_panel__status=1).all()
        zones = []
        monitoring_by_zone_list = {}
        for monitoring in monitoring_list:
            if monitoring.solar_panel.zone not in zones:
                zones.append(monitoring.solar_panel.zone)
        zones.sort()
        for zone in zones:
            monitoring_list_by_zone = SolarPanelMonitoring.objects.filter(solar_panel__status=1,
                                                                          solar_panel__zone=zone).all().order_by(
                "solar_panel__position")
            monitoring_by_zone_list[str(zone)] = monitoring_list_by_zone

        count_damage = SolarPanelMonitoring.objects.filter(solar_panel__status=1).values("damage").annotate(
            count=Count("id"))
        count_cleanliness = SolarPanelMonitoring.objects.filter(solar_panel__status=1).values("cleanliness").annotate(
            count=Count("id"))

        # warning_solar_panel_list = WarningSolarPanel.objects.all()
        solar_panel_detect_video = SolarPanelDetectVideo.objects.last()
        user = request.user
        permission = 1 if user.is_superuser else (2 if not user.is_superuser and user.is_staff else 3)
        return render(request, "solar_panel/solar_panel_monitoring.html",
                      {"permission": permission, "monitoring_by_zone_list": monitoring_by_zone_list,
                       "count_damage": count_damage, "count_cleanliness": count_cleanliness, "solar_panel_detect_video": solar_panel_detect_video})


class RecordOfSolarPanel(LoginRequiredMixin, View):

    def get(self, request, page=1):

        solar_panel_record_list = SolarPanelRecord.objects.all()
        solar_panel_record_list = get_data_by_page(solar_panel_record_list, page)[0]
        is_paginated = get_data_by_page(solar_panel_record_list, page)[1]
        user = request.user
        permission = 1 if user.is_superuser else (2 if not user.is_superuser and user.is_staff else 3)
        return render(request, "solar_panel/solar_panel_record.html",
                      {"permission": permission, "solar_panel_record_list": solar_panel_record_list,
                       "is_paginated": is_paginated})

    def post(self, request, page=1):

        user = request.user
        permission = 1 if user.is_superuser else (2 if not user.is_superuser and user.is_staff else 3)

        filter_select = request.POST.get("filter_select") or None
        filter_input = request.POST.get("filter_input") or None
        filter_input_second = request.POST.get("filter_input_second") or None
        damage_select = request.POST.get("damage_select") or None
        cleanliness_select = request.POST.get("cleanliness_select") or None
        solar_panel_record_list = SolarPanelRecord.objects.all()
        order_by = request.POST.get("order_by") or None

        if filter_select:
            if filter_select == "1":
                solar_panel_record_list = SolarPanelRecord.objects.all()
            elif filter_select == "2":
                if filter_input:
                    solar_panel_record_list = SolarPanelRecord.objects.filter(id=filter_input).all()
            elif filter_select == "3":
                if filter_input:
                    solar_panel_record_list = SolarPanelRecord.objects.filter(solar_panel__id=filter_input).all()
            elif filter_select == "4":
                if filter_input:
                    solar_panel_record_list = SolarPanelRecord.objects.filter(
                        solar_panel__name__contains=filter_input).all()
            elif filter_select == "5":
                if filter_input:
                    solar_panel_record_list = SolarPanelRecord.objects.filter(solar_panel__zone=filter_input).all()
            elif filter_select == "6":
                if damage_select:
                    solar_panel_record_list = SolarPanelRecord.objects.filter(damage=damage_select).all()
            elif filter_select == "7":
                if cleanliness_select:
                    solar_panel_record_list = SolarPanelRecord.objects.filter(cleanliness=cleanliness_select).all()
            elif filter_select == "8":
                if filter_input and filter_input_second:
                    solar_panel_record_list = SolarPanelRecord.objects.filter(recorded_time__gte=filter_input,
                                                                              recorded_time__lte=filter_input_second).all()
                elif filter_input and filter_input_second is None:
                    solar_panel_record_list = SolarPanelRecord.objects.filter(recorded_time__gte=filter_input).all()
                elif filter_input is None and filter_input_second:
                    solar_panel_record_list = SolarPanelRecord.objects.filter(
                        recorded_time__lte=filter_input_second).all()

        if order_by and order_by == "2":
            solar_panel_record_list = solar_panel_record_list.order_by("-id")
        else:
            solar_panel_record_list = solar_panel_record_list.order_by("id")

        solar_panel_record_list = get_data_by_page(solar_panel_record_list, page)[0]
        is_paginated = get_data_by_page(solar_panel_record_list, page)[1]
        return render(request, "solar_panel/solar_panel_record.html",
                      {"permission": permission, "solar_panel_record_list": solar_panel_record_list,
                       "is_paginated": is_paginated, "filter_select": filter_select, "filter_input": filter_input,
                       "filter_input_second": filter_input_second,
                       "damage_select": damage_select,
                       "cleanliness_select": cleanliness_select, "order_by": order_by})


class ReportOfSolarPanel(LoginRequiredMixin, View):
    def get(self, request, page=1):

        user = request.user
        permission = 1 if user.is_superuser else (2 if user.is_staff else 3)

        solar_panel_report_list = SolarPanelReport.objects.all()
        solar_panel_report_list = get_data_by_page(solar_panel_report_list, page)[0]
        is_paginated = get_data_by_page(solar_panel_report_list, page)[1]

        return render(request, "solar_panel/solar_panel_report.html", {
            "permission": permission,
            "solar_panel_report_list": solar_panel_report_list, "is_paginated": is_paginated,
        })

    def post(self, request, page=1):

        user = request.user
        permission = 1 if user.is_superuser else (2 if user.is_staff else 3)
        filter_select = request.POST.get("filter_select") or None
        filter_input = request.POST.get("filter_input") or None
        solar_panel_report_list = SolarPanelReport.objects.all()
        order_by = request.POST.get("order_by") or None

        if filter_select:
            if filter_select == "1":
                solar_panel_report_list = SolarPanelReport.objects.all()
            elif filter_select == "2":
                if filter_input:
                    solar_panel_report_list = SolarPanelReport.objects.filter(id=filter_input).all()
            elif filter_select == "3":
                if filter_input:
                    solar_panel_report_list = SolarPanelReport.objects.filter(month=filter_input).all()
            elif filter_select == "4":
                if filter_input:
                    solar_panel_report_list = SolarPanelReport.objects.filter(year=filter_input).all()

        if order_by and order_by == "2":
            solar_panel_report_list = solar_panel_report_list.order_by("-id")
        else:
            solar_panel_report_list = solar_panel_report_list.order_by("id")

        solar_panel_report_list = get_data_by_page(solar_panel_report_list, page)[0]
        is_paginated = get_data_by_page(solar_panel_report_list, page)[1]
        return render(request, "solar_panel/solar_panel_report.html",
                      {"permission": permission, "solar_panel_report_list": solar_panel_report_list,
                       "is_paginated": is_paginated, "filter_select": filter_select, "filter_input": filter_input,
                       "order_by": order_by})


class SolarPanelReportPDFView(View):
    def get(self, request, id, download=0):
        report = get_object_or_404(SolarPanelReport, id=id)
        content = ContentOfSolarPanelReport.objects.filter(solar_panel_report=report).first()

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        # 标题
        p.setFont("Helvetica-Bold", 20)
        p.drawCentredString(width / 2, height - 2 * cm, "Solar Panel Monthly Report")

        # 基本信息
        p.setFont("Helvetica", 12)
        y = height - 3.5 * cm
        p.drawString(2.5 * cm, y, f"Report ID: {id}")
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
        p.drawString(3 * cm, y, f"Total solar panels: {content.total_solar_panel}")
        y -= 0.6 * cm
        p.drawString(3 * cm, y, f"Damaged panels: {content.total_damage}")
        y -= 0.6 * cm
        p.drawString(3 * cm, y, f"Clean panels: {content.total_clean}")
        y -= 0.6 * cm
        p.drawString(3 * cm, y, f"Dusty panels: {content.total_dusty}")
        y -= 0.6 * cm
        p.drawString(3 * cm, y, f"Bird drop affected panels: {content.total_bird_drop}")

        # 页脚页码
        p.setFont("Helvetica-Oblique", 10)
        p.drawRightString(width - 2 * cm, 1.5 * cm, "Page 1")

        p.showPage()
        p.save()
        buffer.seek(0)
        if download == 0:
            return FileResponse(buffer, as_attachment=False, filename=f"SolarPanelReport-{id}.pdf")
        else:
            return FileResponse(buffer, as_attachment=True, filename=f"SolarPanelReport-{id}.pdf")


class DeleteSolarPanelReport(LoginRequiredMixin, View):
    def get(self, request, id):
        report = get_object_or_404(SolarPanelReport, id=id)
        report.delete()
        return redirect("solar_panel:solar_panel_report")


@method_decorator(csrf_exempt, name="dispatch")
class ReceiveSolarPanel(View):

    def post(self, request):

        data = request.POST.get("solar_panel_json")
        image = request.FILES.get("solar_panel_image")
        if image:
            if not image.content_type.startswith("image/"):
                return HttpResponse("Invalid image format. Please upload jpg/jpeg/png format.")
            if image.size > 100 * 1024 * 1024:
                return HttpResponse("Image too large. Maximum size is 100MB.")
        else:
            return HttpResponse("Image not found.")

        data = json.loads(data)

        detect_results = detect_solar_panel_with_image(image)
        detect_result = None
        path = None
        for key, value in detect_results.items():
            if key == "detections":
                detect_result = value
            if key == "result_path":
                path = value

        path = path.split("solar_panel_monitoring_system_project")[1]
        path = path.replace("\\", "/")

        # detect_label = ["Bird_drop", "Clean", "Damage", "Dusty"]
        result_label = []

        for result in detect_result:
            result_label.append(result["class"])

        damage = 0
        cleanliness = 1

        if "Clean" in result_label and not "Bird_Drop" in result_label and not "Dusty" in result_label:
            cleanliness = 1
        if "Dusty" in result_label and not "Bird_Drop" in result_label and not "Clean" in result_label:
            cleanliness = 2
        if "Bird_Drop" in result_label and not "Clean" in result_label:
            cleanliness = 3
        if "Damage" in result_label:
            damage = 1

        solar_panel_id = data["id"]
        solar_panel = SolarPanel.objects.filter(id=data["id"]).first()

        if not solar_panel:
            return HttpResponse("Solar Panel Not Found.")

        old_monitoring = SolarPanelMonitoring.objects.filter(
            solar_panel_id=data["id"]
        ).first()

        record = SolarPanelRecord(
            solar_panel_id=data["id"],
            damage=damage,
            cleanliness=cleanliness,
            recorded_time=datetime.time,
            image=path,
        )
        record.save()

        if old_monitoring:
            old_monitoring.damage = damage
            old_monitoring.cleanliness = cleanliness
            old_monitoring.image = path
            old_monitoring.save()
        else:
            new_monitoring = SolarPanelMonitoring(
                solar_panel_id=data["id"],
                damage=damage,
                cleanliness=cleanliness,
                image=path,
            )
            new_monitoring.save()

        return HttpResponse("Solar Panel Receive Successful!")


class DeleteSolarPanelRecord(LoginRequiredMixin, View):

    def get(self, request, id):

        user = request.user
        if not user.is_superuser:
            return redirect("login:login")
        solar_panel_record = SolarPanelRecord.objects.filter(id=id).first()
        if not solar_panel_record:
            return hint_message(request, "Solar Panel Record Not Found.", "solar_panel:solar_panel_record")
        solar_panel_record.delete()
        return redirect("solar_panel:solar_panel_record")


class DeleteSolarPanelReport(LoginRequiredMixin, View):
    def get(self, request, id):
        user = request.user
        if not user.is_superuser:
            return redirect("login:login")
        solar_panel_report = SolarPanelReport.objects.filter(id=id).first()
        if not solar_panel_report:
            return hint_message(request, "Solar Panel Report Not Found.", "solar_panel:solar_panel_report")
        solar_panel_report.delete()
        return redirect("solar_panel:solar_panel_report")
