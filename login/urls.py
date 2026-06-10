from django.urls import path
from login import views

app_name = "login"

urlpatterns = [
    # Login related
    path("login/", views.Login.as_view(), name="login"),
    path("logout/", views.Logout.as_view(), name="logout"),
    path("forgot_password/", views.ForgotPassword.as_view(), name="forgot_password"),
    path("verify_code/", views.VerificationCode.as_view(), name="verification_code"),
    path("reset_password/", views.ResetPassword.as_view(), name="reset_password"),

    # Login Information
    path("login_info/", views.InfoOfLogin.as_view(), name="login_info"),
    path("login_info/<int:page>", views.InfoOfLogin.as_view(), name="login_info"),

    # Login Record
    path("login_record/", views.RecordOfLogin.as_view(), name="login_record"),
    path("login_record/<int:page>", views.RecordOfLogin.as_view(), name="login_record"),

    # Login Report
    path("login_report/", views.ReportOfLogin.as_view(), name="login_report"),
    path("login_report/<int:page>", views.ReportOfLogin.as_view(), name="login_report"),
    path("delete_login_report/<int:id>", views.DeleteLoginReport.as_view(), name="delete_login_report"),

    # View Report PDF
    path("login_report/view_pdf/<int:id>/<int:download>", views.LoginReportPDFView.as_view(), name="view_login_report_pdf"),

    # Blacklist
    path("login_blacklist/<int:id>", views.LoginBlacklist.as_view(), name="login_blacklist"),

    # Delete_Login
    path("login/delete_login_info/<int:id>", views.DeleteLoginInfo.as_view(), name="delete_login_info"),
    path("login/delete_login_record/<int:id>", views.DeleteLoginRecord.as_view(), name="delete_login_record"),
]
