from django.test import TestCase
from product.models import (
    upload_to,
    uploads_to,
    Category,
    Discount,
    Tax,
    make_thumbnail,
)
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


# def test_upload_to():
#     instance = {
#         "filename": "test.txt",
#     }

#     path = upload_to(instance, filename=instance["filename"])

#     assert path == "product/test.txt"


def test_upload_to_with_filename():
    filename = "test.jpg"
    instance = mixer.blend(Product, image=filename)

    path = upload_to(instance, filename=instance.image)
    expected_path = "product/{filename}".format(filename=filename)
    assert path == "product/test.jpg"
    assert path == expected_path


class ProductUploadTest(TestCase):
    def test_upload_to_function(self):
        filename = "example.jpg"
        discount = baker.make(Discount)
        tax = baker.make(Tax)
        instance = baker.make(
            Product, image=filename, discount=discount, tax=tax, thumbnail=filename
        )

        # Use the filename directly

        expected_path = "product/{filename}".format(filename=filename)
        path = upload_to(instance, filename=instance.image)
        path2 = uploads_to(instance, filename)
        expected_path2 = f"product/{instance.name.lower()}_{filename}"
        self.assertEqual(path, expected_path)
        assert str(instance) == instance.name
        assert (
            instance.get_absolute_url()
            == f"http://localhost:8000/api/prd/products/{instance.category.slug}/{instance.slug}/"
        )

        get_discount = Decimal(instance.price) * Decimal("0.10")
        self.assertEqual(instance.get_discount(), get_discount)

        calc_discount = instance.discount.no_discount % 100
        formatted_discount = "{:.1f}".format(calc_discount)
        formatted_discount = f"{calc_discount:.1f}"
        # formatted_discount = f"{calc_discount:.1f}%"
        assert instance.discount_in_percentage == f"{formatted_discount} %"

        assert (
            instance.discounted_price
            == (instance.price * instance.discount.no_discount) % 100
        )

        assert instance.tax_price == instance.tax.nhis_tax * 100
        assert instance.sell_price == float(instance.price) - float(
            instance.discounted_price
        ) - float(instance.tax_price)
        assert instance.endpoint == instance.get_absolute_url()
        assert instance.get_image() == f"http://localhost:8000/{instance.image.url}"

        assert (
            instance.get_thumbnail()
            == f"http://localhost:8000/{instance.thumbnail.url}"
        )

    def test_make_thumbnail(self):
        filename = "example.jpg"
        discount = baker.make(Discount)
        tax = baker.make(Tax)
        product = baker.make(Product, image=filename, discount=discount, tax=tax)

        fake_image = BytesIO()
        image = Image.new("RGB", (100, 100), color="red")
        image.save(fake_image, "JPEG")
        fake_image.seek(0)
        thumbnail = product.make_thumbnail(File(fake_image, name="example.jpg"))
        self.assertIsNotNone(thumbnail)
        product.thumbnail = thumbnail
        # product.save()

        pass


class TestCategory(TestCase):
    def test_str_name(self):
        instance = baker.make(
            Category,
            name="my category",
        )
        assert str(instance) == "my category"

        assert instance.get_absolute_url() == "/my-category/"
        assert instance.endpoint == "/my-category/"
        assert instance.endpoints == f"http://localhost:8000/api/prd/myc/{instance.id}/"
        assert instance.get_discount() == "2334"
