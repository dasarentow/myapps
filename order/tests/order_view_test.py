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


"""REFER TO PRDUCT TEST FOR TEST ON ORDER VIEWS"""
