from django.urls import path, include
from . views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'my-order', MyOrder, basename='MyOrder')
router.register(r'my-order-item', MyOrderItem, basename='MyOrderItem')
router.register(r'my-shipping', MyShippingAddress,
                basename='MyShippingAddress')
router.register(r'my-shipping/', MyShippingAddress,
                basename='MyShippingAddress')

app_name = 'order'
urlpatterns = [
    path('checkout/', checkout),
    path('myc-checkout/', product_checkout, name='my_checkout'),
    path('order-create/', createOrder, name='create-orders'),
    path('', include(router.urls))
]
