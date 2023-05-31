from django.test import TestCase
from chat.models import upload_to, Topic, Comments, Like
import inspect
from myusers.models import NewUser
from mixer.backend.django import mixer
import pytest
from hypothesis import given, note, strategies as st
from hypothesis.extra.django import TestCase
from rest_framework import status
from django.urls import reverse
from django.test import Client
from rest_framework.test import APIClient

from model_bakery import baker
from pprint import pprint
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from urllib.parse import urlencode

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


class TestViews(APITestCase):
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

        self.topic_url = reverse("chat:topic-list")

    def test_topic_viewset(self):
        response = self.client.get(self.topic_url)
        assert response.status_code == status.HTTP_200_OK

        retrieve_topic = Topic.objects.filter(topic="topic").first()
        params = urlencode({"q": retrieve_topic.topic})
        url = f"{self.topic_url}?{params}"
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_perform_create(self):
        url = reverse("chat:topic-list")
        response = self.client.post(
            url,
            data={"topic": "new_topic", "description": "new-description"},
            content="application/json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        self.new_topic = Topic.objects.get(topic="new_topic")

    def test_perform_update(self):
        url = reverse("chat:topic-detail", kwargs={"slug": self.chat.slug})
        response = self.client.put(
            url,
            data={"topic": "new_topic", "description": self.chat.description},
            content="application/json",
        )
        assert response.status_code == status.HTTP_200_OK


@pytest.fixture
def my_model():
    my_model = Topic.objects.create(topic="Test Topic", description="Test description")
    yield my_model
    # Clean up after the test is completed
    my_model.delete()


@pytest.fixture
def my_models():
    my_models = Topic.objects.create(
        topic="Tested Topic", description="Tested description"
    )
    yield my_models
    # Clean up after the test is completed
    my_models.delete()


@pytest.fixture
def another_users():
    new_one = NewUser.objects.create_user(
        username="some", email="somes@example.com", password="somepassword"
    )
    return new_one
    # new_one.delete()


@pytest.fixture
def invalid_data():
    return {"topic": 999, "comments": "Test comment"}


@pytest.mark.usefixtures("my_model", "my_models", "invalid_data")
class TestCommentViewSet(APITestCase):
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
        self.get_url = reverse("chat:comment-list")

    def test_comment_view(self):
        fetch = Topic.objects.get(topic="Tested Topic")
        response = self.client.get(self.get_url)
        assert response.status_code == status.HTTP_200_OK

    def test_create_comment(self):
        topic = Topic.objects.get(topic="Test Topic")
        comments = "this is my comment"
        host = NewUser.objects.get(username="testuser")
        response = self.client.post(
            self.get_url,
            data={"topic": topic.id, "comments": comments},
            content="application/json",
        )
        assert response.status_code == status.HTTP_201_CREATED

        resp = self.client.post(
            self.get_url,
            data={"topic": topic.id, "comments": "this is second comments"},
            content="application/json",
        )
        assert resp.status_code == status.HTTP_201_CREATED

        # get_user = NewUser.objects.get(username="some")
        # self.client.force_authenticate(user=get_user)
        one = NewUser.objects.create_user(
            username="raid", email="raid@email.com", password="password"
        )
        get_one = NewUser.objects.get(username="raid")
        c = Client()
        logged_in = c.login(username="raid", password="password")

        resper = self.client.post(
            self.get_url,
            data={
                "topic": topic.id,
                "comments": "this is third comments",
            },
            content="application/json",
        )
        assert resper.status_code == status.HTTP_201_CREATED

        assert Comments.objects.count() == 3

        comment = Comments.objects.first()
        assert comment.topic == topic
        assert comment.comments == comments
        assert comment.host == host

        get_raid_comment = Comments.objects.filter(host__username="raid")
        # print("get_raid_comment", get_raid_comment)

    def test_perform_create_failure(self):
        # Arrange
        # Act
        num = 9999
        response = self.client.post(
            self.get_url,
            data={"topic": num, "comments": "this comment"},
            content="application/json",
        )
        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.usefixtures("my_model", "my_models", "invalid_data")
class TestAddLikes(TestCase):
    def setUp(self):
        self.client = APIClient()
        username = "testeruser"
        email = "testeruser@email.com"
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

        password = "testpassword"
        self.testers_user = NewUser.objects.create_user(
            username="testersuser", email="testersuser@email.com", password=password
        )

        self.chat = mixer.blend(Topic, topic="my topic", description="description")
        jwt_fetch_datas = {"email": email, "password": password}
        response = self.client.post(token_obtain_url, jwt_fetch_datas, format="json")
        token2 = response.data["access"]
        self.client2 = APIClient()
        self.client2.credentials(HTTP_AUTHORIZATION=f"Bearer {token2}")
        self.topic = Topic.objects.get(topic="Test Topic")
        self.add_url = reverse("chat:add-likes")
        self.add_like_url = reverse(
            "chat:add-likes-detail", kwargs={"pk": self.topic.id}
        )

    def test_get_method(self):
        response = self.client.get(self.add_url)
        assert response.status_code == status.HTTP_200_OK

        response = self.client.get(self.add_like_url)
        assert response.status_code == status.HTTP_200_OK

    def test_add_likes_view(self):
        data = {"id": self.topic.id}

        add_like_url = reverse("chat:add-likes-detail", kwargs={"pk": self.topic.id})

        response = self.client.put(
            add_like_url,
            data=data,
        )
        assert response.status_code == status.HTTP_200_OK
        assert self.topic.like.all().count() == 1
        res = self.client.put(
            self.add_like_url,
            data=data,
        )
        # assert res.status_code == status.HTTP_304_NOT_MODIFIED
        assert self.topic.like.all().count() == 1
        topic_participant = self.topic.like.all().first()
        like = Like.objects.get(pk=topic_participant.id)
        print("data: %s" % topic_participant.participants.count())

        new_response = self.client2.put(
            self.add_like_url, data=data, content="application/json"
        )
        new_topic_participant = self.topic.like.all().first()
        print("new response", new_topic_participant.participants.all())

        user = User.objects.create(
            username="tested", email="tested@example", password="tested"
        )
        user_client = APIClient()
        user_client.force_authenticate(user=user)
        new_like = user_client.put(
            self.add_like_url, data=data, content="application/json"
        )
        assert new_topic_participant.participants.all().count() == 2
