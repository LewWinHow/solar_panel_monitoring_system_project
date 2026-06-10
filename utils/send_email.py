from django.core.mail import EmailMessage


def send_email_with_solar_panel_report_pdf(id, buffer, to_email):
    # 构造邮件
    email = EmailMessage(
        subject=f"Solar Panel Report #{id}",
        body="Please find the attached solar panel report.",
        from_email="xiaohao6070@gmail.com",
        to=[to_email],
    )
    email.attach(f"SolarPanelReport-{id}.pdf", buffer.read(), "application/pdf")
    email.send()


def send_email_with_login_report_pdf(id, buffer, to_email):
    # 构造邮件
    email = EmailMessage(
        subject=f"Login Report #{id}",
        body="Please find the attached login report.",
        from_email="xiaohao6070@gmail.com",
        to=[to_email],
    )
    email.attach(f"LoginReport-{id}.pdf", buffer.read(), "application/pdf")
    email.send()
