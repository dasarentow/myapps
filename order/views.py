from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework.viewsets import ModelViewSet
from myusers.models import NewUser
from myusers.serializers import UserPublicSerializer
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
import stripe
from django.conf import settings
from rest_framework import status, authentication, permissions
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework import serializers

# Create your views here.


class MyOrder(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class MyOrderItem(ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer


class MyShippingAddress(ModelViewSet):
    queryset = ShippingAddress.objects.all()
    serializer_class = ShippingAddressSerializer
    # lookup_field = 'address'

    def get_queryset(self):
        user = self.request.user.email
        return self.queryset.filter(user__email=user)

    def perform_create(self, serializer, *args, **kwargs):
        user = self.request.user.email
        get_user = NewUser.objects.filter(email=user).first()

        serializer.save(user=get_user)

    def get_object(
        self,
        queryset=None,
        *args,
        **kwargs,
    ):
        print("kwargs1", kwargs, args)
        item = self.kwargs.get("address")
        print("kwargs2", item)
        print("slug")
        return get_object_or_404(ShippingAddress, address=item)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        print("me instance....: %s" % instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


@api_view(["GET", "POST", "PUT"])
def createOrder(request):
    print("i am at create order")
    cartItem = CartItem.objects.all().filter(cart__user=request.user)
    order = Order.objects.all()
    user_orders = request.user.orders.all()
    serializer = OrderSerializer(user_orders, many=True)
    order_item = OrderItem.objects.all()

    if request.method == "GET":
        user = request.user
        shipping_address = user.users.first()
        serializer = OrderSerializer(
            user_orders,
            many=True,
        )
        return Response(serializer.data)

    if request.method == "PUT":
        with transaction.atomic():
            data = request.data
            customer = request.user
            shipping_address = customer.users.first()
            paid_amount = data["paid_amount"]
            product = data["ordered_items"]

            for i in product:
                i_product = i["product"]
                pd = get_object_or_404(Product, id=i_product["id"])
                i_price = i["price"]
                i_quantity = i["quantity"]
                new_stock = pd.countInStock - i_quantity
                pd.countInStock = new_stock
                pd.save()

                created_order = order.create(
                    user=customer,
                    shippingAddress=shipping_address,
                    product=pd,
                    price=i_price,
                    quantity=i_quantity,
                    paid_amount=paid_amount,
                    paymentMethod="card",
                    is_paid=True,
                )

            cartItem.delete()

            order_item.create(order=created_order, is_delivered=False)

            serializer = OrderSerializer(
                order,
                many=True,
            )
            return Response(serializer.data)
    return Response(serializer.data)


@api_view(["GET", "POST", "PUT"])
def createOrders(request):
    if request.method == "GET":
        user_orders = request.user.orders.all()
        serializer = OrderSerializer(user_orders, many=True)
        return Response(serializer.data)

    if request.method == "PUT":
        data = request.data
        user = request.user
        customer = request.user
        shipping_address = customer.users.first()
        paid_amount = data["paid_amount"]
        products = data["ordered_items"]

        # Update product stock and create order items
        order_items = []
        for item in products:
            product_id = item["product"]["id"]
            quantity = item["quantity"]
            price = item["price"]

            product = get_object_or_404(Product, id=product_id)
            new_stock = product.countInStock - quantity
            product.countInStock = new_stock
            product.save()

        # Create order
        order = Order.objects.create(
            user=customer,
            shippingAddress=shipping_address,
            paid_amount=paid_amount,
            paymentMethod="card",
            is_paid=True,
        )
        order.save()
        order.items.bulk_create(order_items)

        order_item = OrderItem.objects.create(
            order=order,
            is_delivered=False,
        )
        order_items.append(order_item)

        # Delete cart items
        cart_items = CartItem.objects.filter(cart__user=request.user)
        cart_items.delete()

        # Return serialized order data
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


# @api_view(["GET", "POST", "PUT"])
# def createOrder(request):
#     cartItems = CartItem.objects.all()
#     cartItem = CartItem.objects.all().filter(cart__user=request.user)
#     cnames = [c.product.name for c in cartItem]
#     print("Creater", cartItem)
#     products = Product.objects.all()

#     order = Order.objects.all()
#     filt = Order.objects.filter(user=request.user)
#     dee = request.user.orders.all()
#     save = order.filter()
#     serializer = OrderSerializer(dee, many=True)
#     order_item = OrderItem.objects.all()

#     if request.method == "GET":
#         user = request.user
#         shipping_address = user.users.first()
#         serializer = OrderSerializer(
#             dee,
#             many=True,
#         )
#         return Response(serializer.data)

#     if request.method == "PUT":
#         data = request.data
#         user = request.user
#         great = user.carts.all().first()

#         customer = request.user
#         shipping_address = customer.users.first()
#         paid_amount = data["paid_amount"]
#         product = data["ordered_items"]
#         print("ssssssss", shipping_address)

#         for i in product:
#             i_product = i["product"]
#             pd = Product.objects.get(id=i_product["id"])

#             print("save10", pd)
#             i_price = i["price"]
#             i_quantity = i["quantity"]
#             new_stock = pd.countInStock - i_quantity
#             pd.countInStock = new_stock
#             pd.save()

#             by = order.create(
#                 user=customer,
#                 shippingAddress=shipping_address,
#                 product=pd,
#                 price=i_price,
#                 quantity=i_quantity,
#                 paid_amount=paid_amount,
#                 paymentMethod="card",
#                 is_paid=True,
#             )

#         cartItem.delete()

#         order_item.create(order=by, is_delivered=False)

#         serializer = OrderSerializer(
#             order,
#             many=True,
#         )
#         return Response(serializer.data)
#     return Response(serializer.data)


@api_view(["POST"])
def checkout(request):
    serializer = OrderSerializer(data=request.data)

    if serializer.is_valid():
        stripe.api_key = settings.STRIPE_SECRET_KEY
        paid_amount = sum(
            item.get("quantity") * item.get("product").price
            for item in serializer.validated_data["items"]
        )

        try:
            charge = stripe.Charge.create(
                amount=int(paid_amount * 100),
                currency="USD",
                description="Charge from Djackets",
                source=serializer.validated_data["stripe_token"],
            )

            serializer.save(user=request.user, paid_amount=paid_amount)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "POST"])
def product_checkout(request):
    "i am am at Product checkout"
    queryset = Order.objects.filter()
    ship = ShippingAddress.objects.all()
    user = request.user.email
    stripe.api_key = settings.STRIPE_SECRET_KEY

    if request.method == "GET":
        info = queryset.filter(user__email=user)
        serializer = OrderSerializer(info, many=True)
        getShipping = ship.filter(user__email=user).first()

        print(
            "sh details:  ",
            getShipping,
        )

        return Response(
            serializer.data,
        )

    if request.method == "POST":
        data = request.data
        getShipping = ship.filter(user__email=user).first()
        paid_amount = data["paid_amount"]
        print("Payed", paid_amount)

        try:
            charge = stripe.Charge.create(
                amount=int(paid_amount * 100),
                currency="USD",
                description="Charge from Ds Enterprise",
                source=serializer.validated_data["stripe_token"],
            )
        except Exception:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response()
