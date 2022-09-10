"""
Test for the health checl API.
"""

from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient


class HealthCheckTTests(TestCase):
    """Test the health check API."""

    def test_health_check(self):
        """Test health checl API."""
        client = APIClient()
        url = reverse("health-check")
        res = client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
