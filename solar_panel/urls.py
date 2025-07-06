"""
URL configuration for solar_panel_monitoring_system_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static

# from django.contrib import supervisor
from django.urls import path
from . import views

app_name = "solar_panel"
urlpatterns = [
    # Solar Panel Info
    path("solar_panel_info/", views.SolarPanelInfo.as_view(), name="solar_panel_info"),
    path("solar_panel_info/<int:page>", views.SolarPanelInfo.as_view(), name="solar_panel_info"),

    # Solar Panel Status
    path("solar_panel_satus/<int:id>/", views.SolarPanelStatus.as_view(), name="solar_panel_satus"),

    # Add / Edit / Delete Solar Panel
    path("add_solar_panel/", views.AddSolarPanel.as_view(), name="add_solar_panel"),
    path("edit_solar_panel/<int:id>", views.EditSolarPanel.as_view(), name="edit_solar_panel"),
    path("delete_solar_panel/<int:id>/", views.DeleteSolarPanel.as_view(), name="delete_solar_panel"),

    # Solar Panel Monitoring & Record
    path("solar_panel_monitoring/", views.MonitoringSolarPanel.as_view(), name="solar_panel_monitoring"),
    path("solar_panel_record/", views.RecordOfSolarPanel.as_view(), name="solar_panel_record"),
    path("solar_panel_record/<int:page>", views.RecordOfSolarPanel.as_view(), name="solar_panel_record"),

    # Solar Panel Report (List & Generate)
    path("solar_panel_report/", views.ReportOfSolarPanel.as_view(), name="solar_panel_report"),
    path("solar_panel_report/<int:page>", views.ReportOfSolarPanel.as_view(), name="solar_panel_report"),

    # View Report PDF
    path("solar_panel_report/view_pdf/<int:report_id>/", views.view_report_pdf, name="view_report_pdf"),

    # Data Receive & Record Delete
    path("receive_solar_panel/", views.ReceiveSolarPanel.as_view(), name="receive_solar_panel"),
    path("delete_solar_panel_record/<int:id>", views.DeleteSolarPanelRecord.as_view(), name="delete_solar_panel_record"),
]
