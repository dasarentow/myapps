from django.test import TestCase
from chat.models import upload_to, Topic
from myusers.models import NewUser
from mixer.backend.django import mixer
import pytest
from hypothesis import given, note, strategies as st
from hypothesis.extra.django import TestCase

from django.urls import reverse

from rest_framework.test import APIClient

from model_bakery import baker
from pprint import pprint
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()


pytestmark = pytest.mark.django_db


def test_upload_to():
    """Test that the upload_to function returns the correct path."""

    # def upload_to(instance, filename):
    #     return "chat/{filename}".format(filename=filename)

    # Create a test instance.
    instance = {
        "filename": "test.txt",
    }

    # Call the upload_to function.
    path = upload_to(instance, filename=instance["filename"])

    # Assert that the path is correct.
    assert path == "chat/test.txt"


class TestModel(APITestCase):
    def setUp(self):
        self.client = APIClient()
        username = "testuser"
        email = "testuser@email.com"
        password = "testpassword"
        self.new_user = NewUser.objects.create_user(
            username=username, email=email, password=password
        )

        self.chat = mixer.blend(Topic, topic="topic", description="description")
        jwt_fetch_data = {"email": email, "password": password}
        token_obtain_url = reverse("token_obtain_pair")
        token_refresh_url = reverse("token_refresh")
        response = self.client.post(token_obtain_url, jwt_fetch_data, format="json")
        token = response.data["access"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_get_absolute_url(self):
        assert (
            self.chat.get_absolute_url()
            == "http://127.0.0.1:8000"
            + f"/api/topics/{self.chat.topic}-{self.chat.description}/"
        )

        assert self.chat.slugify == "topic-description-description%"
