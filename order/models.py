# from django.contrib.auth.models import User
from product.models import CartItem
from product.models import Product
from django.urls import reverse
from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()


class ShippingAddress(models.Model):
    # order = models.OneToOneField(
    #     Order, on_delete=models.CASCADE, null=True, blank=True)
    address = models.CharField(max_length=250, null=True, blank=True)
    city = models.CharField(max_length=250, null=True, blank=True)
    postalCode = models.CharField(max_length=250, null=True, blank=True)
    country = models.CharField(max_length=250, null=True, blank=True)
    shippingPrice = models.DecimalField(
        max_digits=7, decimal_places=2, null=True, blank=True)
    user = models.ForeignKey(User, related_name='users',
                             on_delete=models.CASCADE)
    email = models.EmailField(max_length=255, null=True, blank=True)
    # _id = models.AutoField(primary_key=True, editable=False)

    def __str__(self):
        return str(self.address)


class Order(models.Model):
    user = models.ForeignKey(
        User, related_name='orders', on_delete=models.CASCADE)
    shippingAddress = models.ForeignKey(
        ShippingAddress, related_name='shipping', on_delete=models.CASCADE, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    # product = models.CharField(max_length=30000, blank=True, null=True)
    # product = models.ForeignKey(
    #     CartItem, related_name='items', on_delete=models.DO_NOTHING, null=True, blank=True)
    product = models.ForeignKey(
        Product, related_name='items', on_delete=models.CASCADE, null=True, blank=True)
    price = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)

    paid_amount = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True)
    # stripe_token = models.CharField(max_length=100, null=True, blank=True)
    paymentMethod = models.CharField(
        max_length=250, null=True, blank=True, default='card')
    is_paid = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at',]

    def __str__(self):
        return str(self.user)

    def get_cost(self):
        return self.price * self.quantity


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, related_name='items', on_delete=models.CASCADE)
    is_delivered = models.BooleanField(default=False)

    def __str__(self):
        return '%s' % self.id
