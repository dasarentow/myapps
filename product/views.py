from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import PageNumberPagination

from .models import Product, Category
from .serializers import *


class ProductPagination(PageNumberPagination):
    page_size = 30


class MyCart(ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer


class MyTax(ModelViewSet):
    queryset = Tax.objects.all()
    serializer_class = TaxSerializer


class CartItemView(APIView):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer

    def get(self, request, format=None):
        user = self.request.user
        serializer = CartItemSerializer(user)
        return Response(serializer.data)


@api_view(['GET', 'PUT', ])
def add_to_cart(request, *args, **kwargs):
    pagination_class = PageNumberPagination
    queryset = CartItem.objects.all()
    myproduct = Product.objects.all()
    category = Category.objects.all()
    data = request.data
    print('data', data)
    user = request.user.email
    cart_item = CartItem.objects.filter(
        cart__user__email=user)

    if request.method == 'GET':

        cart_item = CartItem.objects.filter(
            cart__user__email=user)
        # print('cart_item', cart_item)
        info = queryset.filter(cart__user__email=user)

        serializer = CartItemSerializer(info, many=True)
        return Response(serializer.data)

    if request.method == 'PUT':
        customer = request.user
        print('cus',  customer)

        cart = Cart.objects.all()
        cart_user = cart.filter(user__email=user)

        data = request.data
        getProducts = data.get('product')
        getQuantity = data.get('quantity')
        print('feeel', getProducts, getQuantity)

        if not cart_user:
            cee = cart.create(user=request.user)
        if cart_user:
            cee = cart.get(user__email=user)
        if cart_item:
            # for item in cart_item:
            print('multiples')
            pd = myproduct.filter(pk=data['product']).first()
            new = cart_item.filter(product=pd).first()
            if new:
                new.quantity = data['quantity']

                new.price = new.price
                new.customer = customer
                print('passed through here')
                new.save()
            else:
                print('i am not in the cart')
                cart_item.create(
                    cart=cee, product=pd, quantity=data['quantity'], price=data['price'], customer=customer)
                print('i am added to cart')

        else:
            product = Product.objects.all()
            pd = product.get(pk=data['product'])

            cart_item.create(
                cart=cee, product=pd, quantity=data['quantity'], price=data['price'], customer=customer)
            print('i run second time')
            # cart_item.save()

        you = CartItem.objects.all()
        right = you.filter(cart__user__email=user)
        serializer = CartItemSerializer(right, many=True)
        return Response(serializer.data)

    # if request.method == 'DELETE':
    #     data = request.data['product']
    #     print('Request', data)
    #     # pd = myproduct.filter(pk=data).first()
    #     # new = cart_item.filter(product=pd).first()
    #     # new.delete()
    #     return Response('you deleted me')


class MyCartItem(ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer

    def get_queryset(self):
        user = self.request.user.email
        carts = Cart.objects.all()
        cart = carts.filter(user__email=user)
        if not cart:
            print('is1:  ', cart, )
        if cart is None:
            print('no one in cart')
        # me = carts.us
        print('is:  ', cart, )
        return self.queryset.filter(cart__user__email=user)

    def perform_destroy(self, instance):
        instance.delete()


class MyDiscount(ModelViewSet):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer


class MyCategory(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class MyProducts(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = ProductPagination
    lookup_field = 'slug'

    def get_queryset(self):
        qs = Product.objects.all()
        q = self.request.GET.get(
            'q') if self.request.GET.get('q') != None else ''
        if q:
            qs = qs.filter(Q(name__contains=q) |
                           Q(category__name__contains=q) |
                           #    Q(discount__contains=q) |
                           Q(id__icontains=q)).distinct()

        # return self.queryset
        return qs

        # return self.queryset[0:20]

    def get_object(self, queryset=None, *args, **kwargs,):
        print('kwargs1', kwargs, args)
        item = self.kwargs.get('slug')
        print('kwargs2', item)
        print('slug')
        return get_object_or_404(Product, slug=item)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        print('instance: %s' % instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    # def retrieve(self, request, pk=None, **kwargs):
    #     item = self.kwargs.get('slug')
    #     prd = get_object_or_404(self.queryset, slug=item)
    #     serializer_class = ProductSerializer(prd)
    #     return Response(serializer_class.data)

    def perform_create(self, serializer):
        category = Category.objects.get(pk=1)

        serializer.save(category=category)

    # action_serializers = {
    #     'retrieve': ProductSerializer,
    #     'list': ProductSerializer,
    #     'create': ProductSerializer
    # }

    # def get_serializer_class(self):

    #     if hasattr(self, 'action_serializers'):
    #         return self.action_serializers.get(self.action, self.serializer_class)

    #     return super(ProductViewSet, self).get_serializer_class()

    # detail_serializer_class =ProductDetailSerializer

    # def get_serializer_class(self):
    #     if self.action == 'retrieve':
    #         if hasattr(self, 'detail_serializer_class'):
    #             return self.detail_serializer_class

    #     return super(ProductViewSet, self).get_serializer_class()


class LatestProductsList(APIView):
    def get(self, request, format=None):
        products = Product.objects.all()[0:4]
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class ProductDetail(APIView):
    def get_object(self, category_slug, product_slug):
        try:
            return Product.objects.filter(category__slug=category_slug).get(slug=product_slug)
        except Product.DoesNotExist:
            raise Http404

    def get(self, request, category_slug, product_slug, format=None):
        product = self.get_object(category_slug, product_slug)
        serializer = ProductSerializer(product)
        return Response(serializer.data)


class CategoryDetail(APIView):
    def get_object(self, category_slug):
        try:
            return Category.objects.get(slug=category_slug)
        except Category.DoesNotExist:
            raise Http404

    def get(self, request, category_slug, format=None):
        category = self.get_object(category_slug)
        serializer = CategorySerializer(category)
        return Response(serializer.data)


@api_view(['POST'])
def search(request):
    query = request.data.get('query', '')

    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query))
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    else:
        return Response({"products": []})
