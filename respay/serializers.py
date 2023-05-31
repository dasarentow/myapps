from rest_framework import serializers
from .models import ResProduct


class ResProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResProduct
        fields = '__all__'
