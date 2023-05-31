from rest_framework import serializers
from .models import DsApps



class DsAppsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DsApps
        fields = '__all__'
        
        

# # serializer.py
# from rest_framework import serializers


# class DsAppsSerializer(serializers.ModelSerializer):
#     name = serializers.CharField(max_length=100)
#     description = serializers.TextField()
#     in_production = serializers.BooleanField()
#     app_pic = serializers.ImageField()

#     class Meta:
#         model = DsApps
#         fields = '__all__'