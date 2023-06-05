from datetime import datetime
from io import BytesIO
from PIL import Image
from decimal import Decimal

from django.core.files import File
from django.db import models
from django.urls import reverse, reverse_lazy
from django_extensions.db.fields import AutoSlugField
from django.contrib.auth import get_user_model

User = get_user_model()
from django.utils.translation import gettext_lazy as _


def upload_to(instance, filename):
    return "product/{filename}".format(filename=filename)
    # return "product/{}".format(filename)


def uploads_to(instance, filename):
    model_class = instance.__class__

    unique_filename = f"{model_class.__name__.lower()}_{filename}"

    return f"product/{unique_filename}"


def make_thumbnail(image, size=(300, 200)):
    img = Image.open(image)
    img = img.convert("RGB")
    img.thumbnail(size)

    thumb_io = BytesIO()
    img.save(thumb_io, "JPEG", quality=85)

    thumbnail = File(thumb_io, name=image.name)

    return thumbnail


# def uploads_to(instance, filename):
#     model_class = instance.__class__

#     if instance.pk is None:
#         # If primary key is None, generate unique filename without including the primary key
#         unique_filename = f"{model_class.__name__.lower()}_{filename}"
#     else:
#         unique_filename = f"{model_class.__name__.lower()}_{instance.pk}_{filename}"

#     return f"product/{unique_filename}"


class Tax(models.Model):
    # product_tax = models.ForeignKey(
    #     Product, on_delete=models.CASCADE)
    tax = models.DecimalField(default=0, decimal_places=4, max_digits=100)
    nhis_tax = models.DecimalField(default=0.014, decimal_places=4, max_digits=100)
    vat = models.DecimalField(default=0.025, decimal_places=4, max_digits=100)


class Discount(models.Model):
    # product = models.ForeignKey('Product', on_delete=models.CASCADE)
    no_discount = models.DecimalField(default=0, decimal_places=2, max_digits=100)
    base_discount = models.DecimalField(default=5, decimal_places=2, max_digits=100)
    middle_discount = models.DecimalField(default=10, decimal_places=2, max_digits=100)
    premium_discount = models.DecimalField(default=25, decimal_places=2, max_digits=100)


class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from=["name"])

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f"/{self.slug}/"

    @property
    def endpoint(self):
        return self.get_absolute_url()

    @property
    def endpoints(self):
        return "http://localhost:8000" + reverse_lazy(
            "product:mycategory-detail",
            kwargs={"pk": self.pk},
        )

    def get_discount(self):
        return "2334"


class Product(models.Model):
    category = models.ForeignKey(
        Category, related_name="products", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    # slug = models.SlugField()
    slug = AutoSlugField(populate_from=["name", "category__slug"])
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    image = models.ImageField(_("Image"), upload_to=uploads_to, blank=True, null=True)
    thumbnail = models.ImageField(upload_to=upload_to, blank=True, null=True)
    # thumbnail = models.ImageField(upload_to=uploads, blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    countInStock = models.PositiveIntegerField(default=0)
    discount = models.ForeignKey(
        Discount, on_delete=models.CASCADE, null=True, blank=True
    )
    # discount = models.DecimalField(max_digits=6, decimal_places=2)
    discounted_price = models.IntegerField(blank=True, default=0)
    tax = models.ForeignKey(Tax, blank=True, null=True, on_delete=models.CASCADE)

    class Meta:
        ordering = ("-date_added",)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return (
            "http://localhost:8000/api"
            + f"/prd/products/{self.category.slug}/{self.slug}/"
        )

    # @property
    # def sale_price(self):
    #     return "%2f" % (float(self.price) * 0.8)

    def get_discount(self):
        return round(self.price * Decimal("0.10"), 4)

    @property
    def discount_in_percentage(self):
        return f"{float(self.discount.no_discount)} %"

    @property
    def discounted_price(self):
        return (self.price * self.discount.no_discount) / 100

    @property
    def tax_price(self):
        return self.tax.nhis_tax * 100

    @property
    def sell_price(self):
        return float(self.price) - float(self.discounted_price) - float(self.tax_price)

    @property
    def endpoint(self):
        return self.get_absolute_url()

    def get_image(self):
        if self.image:
            return "http://localhost:8000/" + self.image.url
        return ""

    def make_thumbnail(self, image, size=(300, 200)):
        img = Image.open(image)
        img = img.convert("RGB")
        img.thumbnail(size)

        thumb_io = BytesIO()
        img.save(thumb_io, "JPEG", quality=85)

        thumbnail = File(thumb_io, name=image.name)

        return thumbnail

    def get_thumbnail(self):
        if self.thumbnail:
            return "http://localhost:8000/" + self.thumbnail.url
        else:
            if self.image:
                self.thumbnail = self.make_thumbnail(self.image)
                self.save()

                return "http://localhost:8000/" + self.thumbnail.url
            else:
                return ""

    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)
    #     if self.image:
    #         self.thumbnail = self.make_thumbnail(self.image)
    #         self.save(update_fields=["thumbnail"])


class Cart(models.Model):
    user = models.ForeignKey(User, related_name="user", on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=datetime.now)


class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.FloatField(blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    customer = models.ForeignKey(
        User, related_name="carts", on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self):
        return f"Cart item ({self.id}): {self.product.name} - {self.quantity}"
