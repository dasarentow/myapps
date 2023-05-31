from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from myusers.serializers import *
from . models import *

from drf_writable_nested.serializers import WritableNestedModelSerializer


class ResponseSerializer(WritableNestedModelSerializer):
    participants = UserProfileSerializer(read_only=True, many=True)
    host = UserProfileSerializer(read_only=True, many=False)
    # comment = serializers.PrimaryKeyRelatedField(read_only=True)
    # comment = CommentSerializer(read_only=True, many=True)

    class Meta:
        model = Responses
        fields = "__all__"
        read_only_fields = (
            'host', 'created', 'updated', 'slug',)
