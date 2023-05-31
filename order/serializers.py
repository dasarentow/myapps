from rest_framework import serializers
from . models import *
from myusers.serializers import UserProfileSerializer
from product.serializers import *


# cart = CartSerializer(many=False, read_only=True)
# product = ProductSerializer(many=False, read_only=True)


class ShippingAddressSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True, many=False)

    class Meta:
        model = ShippingAddress
        fields = '__all__'


class OrderItemSerializer(serializers.ModelSerializer):
    # product = ProductSerializer()
    # shipping = ShippingAddressSerializer(many=False)

    class Meta:
        model = OrderItem
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    user = UserProfileSerializer()
    product = ProductSerializer(many=False)

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = (
            "product", 'is_paid', 'shippingAddress', 'paymentMethod', 'paid_amount', 'user', 'is_paid', 'get_cost',
        )
