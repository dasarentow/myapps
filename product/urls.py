from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"myc", MyCategory, basename="mycategory")

router.register(r"myp", MyProducts, basename="myproduct")

router.register(r"mycart", MyCart, basename="mycart")
router.register(r"mycartitem", MyCartItem, basename="mycartitem")
router.register(r"mydiscount", MyDiscount, basename="mydiscount")
router.register(r"mytax", MyTax, basename="mytax")

app_name = "product"
urlpatterns = [
    path("latest-products/", LatestProductsList.as_view()),
    path("products/search/", search),
    path(
        "products/<slug:category_slug>/<slug:product_slug>/",
        ProductDetail.as_view(),
        name="prds",
    ),
    path("products/<slug:category_slug>/", CategoryDetail.as_view(), name="cat"),
    path("try/", add_to_cart, name="try"),
    path("try/<str:pk>/", add_to_cart, name="try"),
    path("", include(router.urls), name="prd"),
]
