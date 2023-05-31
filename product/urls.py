from django.urls import path, include
from . views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'myc', MyCategory, basename='mycategory')

router.register(r'myp', MyProducts, basename='myproduct')

router.register(r'mycart', MyCart, basename='mycart')
router.register(r'mycartitem', MyCartItem, basename='myproduct')
router.register(r'mydiscount', MyDiscount, basename='myproduct')
router.register(r'mytax', MyTax, basename='myproduct')

app_name = 'product'
urlpatterns = [
    path('latest-products/', LatestProductsList.as_view()),
    path('products/search/', search),
    path('products/<slug:category_slug>/<slug:product_slug>/',
         ProductDetail.as_view()),
    path('products/<slug:category_slug>/', CategoryDetail.as_view()),
    path('try/', add_to_cart, name='try'),
    path('try/<str:pk>/', add_to_cart, name='try'),
    path('', include(router.urls), name='prd')
]
