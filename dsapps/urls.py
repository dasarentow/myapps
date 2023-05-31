from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DsAppsViewSet

router = DefaultRouter()
router.register(r'dsapps', DsAppsViewSet)



app_name = 'dsapps'
urlpatterns = [
    path('', include(router.urls)),
]




# urls.py
# from django.urls import path
# from .views import DsAppsViewSet


# urlpatterns = [
#     path('dsapps/', DsAppsViewSet.as_view({'get': 'list', 'post': 'create'}), name='dsapps-list'),
#     path('dsapps/<int:pk>/', DsAppsViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='dsapps-detail'),
# ]