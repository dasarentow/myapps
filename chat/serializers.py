from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from myusers.serializers import *
from .models import *
from rest_framework.response import Response

from drf_writable_nested.serializers import WritableNestedModelSerializer
import json


class ResponseSerializer(WritableNestedModelSerializer):
    participants = UserProfileSerializer(read_only=True, many=True)
    host = UserProfileSerializer(read_only=True, many=False)
    # comment = serializers.PrimaryKeyRelatedField(read_only=True)
    # CommentSerializer(read_only=True, many=True)

    class Meta:
        model = Responses
        fields = "__all__"
        read_only_fields = (
            "host",
            "created",
            "updated",
            "slug",
        )


# class CommentSerializer (WritableNestedModelSerializer):
class CommentSerializer(ModelSerializer):
    participants = UserProfileSerializer(read_only=True, many=True)
    host = UserProfileSerializer(read_only=True, many=False)
    response = ResponseSerializer(read_only=True, many=True)
    # parent = serializers.CharField(source='')
    see = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Comments
        fields = "__all__"
        read_only_fields = (
            "host",
            "created",
            "updated",
            "slug",
            "is_children",
            "is_parent",
            "response",
            "see",
        )

    def get_see(self, obj):
        news = Comments.objects.all()
        new = obj.reply.all()
        # print('new', new.filter(comment__in=news), new)
        return obj.is_children


class FieldSerializer(ModelSerializer):
    class Meta:
        model = Field
        fields = "__all__"
        read_only_fields = ("created", "updated", "slug")


class LikeSerializer(ModelSerializer):
    class Meta:
        model = Like
        fields = "__all__"
        read_only_fields = ("likes", "dislikes", "participants", "loves", "user")


# class TopicSerializer(ModelSerializer):
class TopicSerializer(WritableNestedModelSerializer):
    link = serializers.HyperlinkedIdentityField(
        view_name="chat:topic-detail",
        lookup_field="slug",
    )
    created_by = UserProfileSerializer(read_only=True, many=False)
    comment = CommentSerializer(read_only=True, many=True)
    response = ResponseSerializer(read_only=True, many=True)
    like = LikeSerializer(read_only=True, many=True)
    load_pic = serializers.ImageField(
        required=False,
    )

    class Meta:
        model = Topic
        fields = [
            "id",
            "topic",
            "description",
            "load_pic",
            "created",
            "updated",
            "link",
            "created_by",
            "comment",
            "response",
            "likes",
            "like",
            "slug",
        ]
        read_only_fields = (
            "created",
            "updated",
            "slug",
            "sow",
            "comment",
            "response",
        )
