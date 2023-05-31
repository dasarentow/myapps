from django.shortcuts import render
from . models import *
from . serializers import *
from rest_framework.viewsets import ModelViewSet
from myusers.models import NewUser
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
import stripe
from django.conf import settings
from rest_framework import status, authentication, permissions
from rest_framework.decorators import api_view, authentication_classes, permission_classes
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

    def get_object(self, queryset=None, *args, **kwargs,):
        print('kwargs1', kwargs, args)
        item = self.kwargs.get('address')
        print('kwargs2', item)
        print('slug')
        return get_object_or_404(ShippingAddress, address=item)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        print('me instance....: %s' % instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


@api_view(['GET', 'POST', 'PUT'])
def createOrder(request):
    cartItems = CartItem.objects.all()
    cartItem = CartItem.objects.all().filter(cart__user=request.user)
    cnames = [c.product.name for c in cartItem]
    print('Creater', cartItem)
    products = Product.objects.all()

    order = Order.objects.all()
    filt = Order.objects.filter(user=request.user)
    dee = request.user.orders.all()
    save = order.filter()
    serializer = OrderSerializer(dee, many=True)
    order_item = OrderItem.objects.all()

    if request.method == 'GET':

        user = request.user
        save = user.user.all()
        savior = user.orders.all()

        shipping_address = user.users.first()

        me = products.filter(name__in=cnames)

        great = user.carts.all()

        print('Create Order', savior)
        # for i in cartItem:
        #     print(i.product)
        # return Response(serializer.data)
        # # print(cartItem.get(product=set.all()))
        serializer = OrderSerializer(dee, many=True,)
        return Response(serializer.data)

        pass

    if request.method == 'PUT':
        data = request.data
        user = request.user
        great = user.carts.all().first()

        customer = request.user
        shipping_address = customer.users.first()
        paid_amount = data['paid_amount']
        product = data['ordered_items']
        print('ssssssss', shipping_address)

        # for i in cartItem:
        #     print('subsequent', i.product)
        #     me = products.get(name=i.product.name)

        #     new = me.countInStock - i.quantity
        #     me.countInStock = new
        # me.save()

        # print('save', new,  me.countInStock)
        for i in product:
            i_product = i['product']
            pd = Product.objects.get(id=i_product['id'])

            print('save10', pd)
            i_price = i['price']
            i_quantity = i['quantity']
            new_stock = pd.countInStock - i_quantity
            pd.countInStock = new_stock
            pd.save()
        # names = [c['product']['name'] for c in product]
        # print('save3', names)

            by = order.create(user=customer, shippingAddress=shipping_address, product=pd, price=i_price, quantity=i_quantity,
                              paid_amount=paid_amount, paymentMethod='card', is_paid=True,)

        cartItem.delete()

        order_item.create(order=by, is_delivered=False)

        serializer = OrderSerializer(order, many=True,)
        return Response(serializer.data)
    return Response(serializer.data)
    return Response()


@api_view(['POST'])
def checkout(request):
    serializer = OrderSerializer(data=request.data)

    if serializer.is_valid():
        stripe.api_key = settings.STRIPE_SECRET_KEY
        paid_amount = sum(item.get(
            'quantity') * item.get('product').price for item in serializer.validated_data['items'])

        try:
            charge = stripe.Charge.create(
                amount=int(paid_amount * 100),
                currency='USD',
                description='Charge from Djackets',
                source=serializer.validated_data['stripe_token']
            )

            serializer.save(user=request.user, paid_amount=paid_amount)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
def product_checkout(request):
    queryset = Order.objects.filter()
    ship = ShippingAddress.objects.all()
    user = request.user.email
    stripe.api_key = settings.STRIPE_SECRET_KEY

    if request.method == 'GET':

        info = queryset.filter(user__email=user)
        serializer = OrderSerializer(info, many=True)
        getShipping = ship.filter(
            user__email=user).first()

        print('sh details:  ', getShipping, )

        return Response(serializer.data,)

    if request.method == 'POST':
        data = request.data
        getShipping = ship.filter(
            user__email=user).first()
        paid_amount = data['paid_amount']
        print('Payed', paid_amount)

        try:
            charge = stripe.Charge.create(
                amount=int(paid_amount * 100),
                currency='USD',
                description='Charge from Ds Enterprise',
                source=serializer.validated_data['stripe_token']
            )
        except Exception:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response()
