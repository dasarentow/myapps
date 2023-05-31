from django.shortcuts import render

# Create your views here.


from rest_framework import viewsets
from .models import *
from .serializers import DsAppsSerializer

class DsAppsViewSet(viewsets.ModelViewSet):
    queryset = DsApps.objects.all()
    serializer_class = DsAppsSerializer
