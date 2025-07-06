from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model


class SolarPanelReportViewTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_superuser(
            username="testuser", password="testpass", email="test@example.com"
        )
        self.client = Client()
        self.client.login(username="testuser", password="testpass")

    def test_report_view(self):
        response = self.client.get(reverse("solar_panel_report"))
        self.assertEqual(response.status_code, 200)
