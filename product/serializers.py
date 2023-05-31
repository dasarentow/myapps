from rest_framework import serializers
from .models import *
from rest_framework.reverse import reverse
from myusers.serializers import *


class ProductSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField(read_only=True)
    # edit_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Product
        # fields = '__all__'
        read_only_fields = (
            "get_thumbnail",

        )
        fields = (
            "id",
            "name",
            "get_absolute_url",
            "description",
            "price",
            "get_image",
            "get_thumbnail",
            # "thumbnail",
            'endpoint',
            'slug',
            'url',
            'countInStock',
            # 'discounts',
            # 'edit_url',
            # 'discount',
            'tax_price',
            'discounted_price',
            "discount_in_percentage",
            'sell_price',
        )

    def get_url(self, obj):
        # return f'/api/products/generic/{obj.pk}/'
        request = self.context.get('request')  # self.context
        # print('context', self.context)
        if request is None:
            return None
        return reverse("product:myproduct-detail", kwargs={"slug": obj.slug}, request=request)

    # def get_edit_url(self, obj):
    #     # return f'/api/products/generic/{obj.pk}/'
    #     request = self.context.get('request')  # self.context
    #     print('context', self.context)
    #     if request is None:
    #         return None
    #     return reverse("product:myproduct", kwargs={"pk": obj.pk}, request=request)


class CategorySerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True)
    url = serializers.SerializerMethodField(read_only=True)
    # endpoints = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Category
        # fields = '__all__'
        fields = (
            "id",
            "name",
            "get_absolute_url",
            "products",
            "url",
            'endpoints',

        )

    def get_url(self, obj):
        # return f'/api/products/generic/{obj.pk}/'
        request = self.context.get('request')  # self.context
        # print('context', self.context)
        if request is None:
            return None
        return reverse("product:mycategory-detail", kwargs={"pk": obj.pk}, request=request)


class CartSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cart
        fields = '__all__'


class CartItemSerializer(serializers.ModelSerializer):
    cart = CartSerializer(many=False, read_only=True)
    product = ProductSerializer(many=False, read_only=True)
    customer = UserProfileSerializer(read_only=True, many=False)

    class Meta:
        model = CartItem
        fields = '__all__'


class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = '__all__'


class TaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tax
        fields = '__all__'
