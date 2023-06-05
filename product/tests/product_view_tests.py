from django.test import TestCase
from product.models import (
    upload_to,
    uploads_to,
    Category,
    Discount,
    Tax,
    CartItem,
    make_thumbnail,
)
from django.http import Http404
from product.views import ProductDetail, CategoryDetail
from product.serializers import ProductSerializer
import inspect
from myusers.models import NewUser
from mixer.backend.django import mixer
import pytest
from hypothesis import given, note, strategies as st
from hypothesis.extra.django import TestCase
from rest_framework import status
from django.urls import reverse, reverse_lazy
from django.test import Client
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
from model_bakery import baker
from pprint import pprint
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from urllib.parse import urlencode
from product.models import Product
from decimal import Decimal

from io import BytesIO
from PIL import Image
from decimal import Decimal
from django.core.files import File


User = get_user_model()


pytestmark = pytest.mark.django_db


filename1 = "example1.jpg"
filename2 = "example2.jpg"
filename3 = "example3.jpg"


# discount = baker.make(Discount)
# tax = baker.make(Tax)
@pytest.fixture
def category_accessories(autouse=True):
    accessories = baker.make(Category, name="accessories")
    pharm = baker.make(Category, name="pharm")
    med = baker.make(Category, name="med")
    yield accessories, pharm, med
    # Clean up after the test is completed
    accessories.delete()
    pharm.delete()
    med.delete()


@pytest.fixture
def product_one(
    category_accessories,
    autouse=True,
):
    accessories, pharm, med = category_accessories
    # category_one = baker.make(Category, name="accessories")
    product_one = baker.make(
        Product,
        name="phone",
        category=accessories,
        # discount=discount,
        price=Decimal(2.34),
        # tax=tax,
        countInStock=2,
    )
    yield product_one
    # Clean up after the test is completed
    product_one.delete()


@pytest.fixture
def product_two(category_accessories, autouse=True):
    accessories, pharm, med = category_accessories
    product_two = mixer.blend(
        Product,
        name="shoe",
        category=pharm,
        # discount=discount,
        price=Decimal(2.34),
        # tax=tax,
        countInStock=3,
    )
    yield product_two
    # Clean up after the test is completed
    product_two.delete()


@pytest.fixture
def product_three(category_accessories, autouse=True):
    accessories, pharm, med = category_accessories
    product_three = baker.make(
        Product,
        name="lace",
        category=category_accessories[2],
        price=Decimal(2.34),
        # discount=discount,
        # tax=tax,
        countInStock=4,
    )

    yield product_three
    # Clean up after the test is completed
    product_three.delete()


@pytest.mark.usefixtures(
    "product_one",
    "product_two",
    "product_three",
)
class TestProductViews(TestCase):
    def setUp(self):
        self.client1 = APIClient()

        self.user1 = NewUser.objects.create_user(
            username="user1", email="user1@email.com", password="password"
        )

        token_obtain_url = reverse("token_obtain_pair")
        token_refresh_url = reverse("token_refresh")
        jwt_fetch_data = {"email": "user1@email.com", "password": "password"}

        response = self.client1.post(token_obtain_url, jwt_fetch_data, format="json")
        token = response.data["access"]
        self.client1.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        # self.client2 = APIClient()

        self.user2 = NewUser.objects.create_user(
            username="user2", email="user2@email.com", password="password"
        )

        self.client2 = APIClient()
        self.client2.force_authenticate(user=self.user2)

        self.product1 = Product.objects.get(name="phone")
        self.product2 = Product.objects.get(name="shoe")
        self.product3 = Product.objects.get(name="lace")

        self.add_to_cart_url = reverse("product:try")
        self.my_cartitem_url = reverse("product:mycartitem-list")
        self.category_one = Category.objects.filter(name="accessories")

    def test_list_products(self):
        my_product_url = reverse("product:myproduct-list")

        response = self.client2.get(f"{my_product_url}?q=  ")

        responses = self.client1.get(my_product_url)

        assert response.status_code == status.HTTP_200_OK
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_product(self):
        url = reverse("product:myproduct-detail", kwargs={"slug": self.product1.slug})
        user = NewUser.objects.get(username="user1")
        user_client = APIClient()
        # user_client.force_authenticate(user=user)
        response = self.client2.get(url)
        serializer = ProductSerializer(self.product1, many=False)
        # self.assertAlmostEqual(response.data, serializer.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertEqual(response.data, ProductSerializer(self.product).data)

    def test_add_to_cart(self):
        data = {
            "product": self.product1.id,
            "quantity": 1,
            "price": self.product1.price,
        }
        data1 = {
            "product": self.product1.id,
            "quantity": 3,
            "price": self.product1.price,
        }
        data2 = {
            "product": self.product2.id,
            "quantity": 2,
            "price": self.product2.price,
        }
        data3 = {
            "product": self.product3.id,
            "quantity": 2,
            "price": self.product3.price,
        }
        wrong_data = {
            "product": 78,
            "quantity": 2,
            "price": 977,
        }

        response = self.client1.put(
            self.add_to_cart_url, data=data, content="application/json"
        )

        cart_item_one = CartItem.objects.get(customer__email=self.user1.email)
        cart_item_two = CartItem.objects.filter(customer__email=self.user2.email)

        assert response.data[0]["product"]["id"] == self.product1.id
        assert response.data[0]["quantity"] == data["quantity"]
        assert response.data[0]["price"] == float(self.product1.price)
        assert response.data[0]["customer"]["id"] == self.user1.id

        responses = self.client1.put(
            self.add_to_cart_url, data=data1, content="application/json"
        )

        responsess = self.client1.put(
            self.add_to_cart_url, data=data2, content="application/json"
        )
        responsess = self.client1.put(
            self.add_to_cart_url, data=data3, content="application/json"
        )
        responsess = self.client2.put(
            self.add_to_cart_url, data=data3, content="application/json"
        )

        cart_item_onec = CartItem.objects.filter(customer__email=self.user1.email)
        cart_item_twoc = CartItem.objects.filter(customer__email=self.user2.email)

        assert response.status_code == status.HTTP_200_OK
        assert responsess.status_code == status.HTTP_200_OK

        # Retrieve the cart items using GET method
        response = self.client1.get(self.add_to_cart_url)
        assert response.status_code == 200
        assert len(response.data) == 3

        responses = self.client1.post(
            self.add_to_cart_url, data=data1, content="application/json"
        )
        assert responses.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

        """test delete functionality"""
        delete_cart_url = reverse("product:mycartitem-detail", kwargs={"pk": 1})
        response = self.client1.delete(delete_cart_url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        response = self.client1.get(self.add_to_cart_url)
        assert response.status_code == 200
        assert len(response.data) == 2

    def test_my_cartitem(self):
        response = self.client1.get(self.my_cartitem_url)
        assert response.status_code == status.HTTP_200_OK

    def test_product_detail_view(self):
        view = ProductDetail()

        category = Category.objects.all().get(name="accessories")

        obj = view.get_object(category.slug, self.product1.slug)
        self.assertEqual(obj, self.product1)
        # product_one_category = Product.objects.get(
        #     category__name=self.product1.category
        # )
        # category_product_one = category.products.all()
        url = reverse("product:prds", args=[category.slug, self.product1.slug])
        response = self.client1.get(url)
        assert response.data == ProductSerializer(self.product1).data
        assert response.status_code == status.HTTP_200_OK

        see = Product.objects.filter(category__slug=category.slug).get(
            slug=self.product1.slug
        )

        with pytest.raises(Http404):
            obj = view.get_object(category.slug, self.product3.slug)

    def test_category_detail_view(self):
        category = Category.objects.all().get(name="accessories")
        print("see", category.slug)
        url = reverse("product:cat", args={category.slug})
        response = self.client1.get(url)
        assert response.status_code == status.HTTP_200_OK
        wrong_url = reverse("product:cat", args=[self.product2.name])
        view = CategoryDetail()

        with pytest.raises(Http404):
            name = view.get_object("ewas")
