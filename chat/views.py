import math
import random
from django.db.models import Max
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from random import randint
from .models import *
from .serializers import *
from .serializer import *
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.db.models import F

# Create your views here.


class CommentViewSet(ModelViewSet):
    queryset = Comments.objects.all()
    serializer_class = CommentSerializer

    def get_queryset(self):
        topics = Topic.objects.all()
        # topic = topics.get(id=3)
        # print(topic.comment.all())
        # comment = self.queryset.filter(id=91).first()
        # reveal = comment.replies.all()
        # print('reveal', reveal)
        # see = topics.comment.all()
        # see = topics.topic_set.all()
        # b = self.queryset.filter(topic__in=topics)
        # print('sd', b)
        # return self.queryset.filter(topic__in=topics)
        return self.queryset
        # return self.queryset.filter(topic__in=topics)

    def perform_create(self, serializer, *args, **kwargs):
        data = self.request.data
        topic_id = data.get("topic")
        comments = data.get("comments")

        # topic = get_object_or_404(Topic, id=topic_id)
        try:
            topic = Topic.objects.get(id=topic_id)
        except Topic.DoesNotExist:
            raise serializers.ValidationError(
                {"topic": "Invalid Topic"}, code=status.HTTP_404_NOT_FOUND
            )

        serializer.save(topic=topic, comments=comments, host=self.request.user)

    # def perform_create(self, serializer, *args, **kwargs):
    #     data = self.request.data
    #     topics = Topic.objects.all()
    #     # print('create', data)
    #     comments = data["comments"]
    #     topic = data["topic"]
    #     get_topic = topics.get(id=topic)
    #     # print('get_topic', get_topic.topic)
    #     topicss = get_topic.comment.all()
    #     # sap = [c.participants for c in topicss]
    #     # print('save', sap)
    #     # for c in topicss:
    #     #     if c.participants:
    #     #         # print('night', c.participants)
    #     #         if self.request.user in c.participants.all():
    #     #             print('trUE')
    #     #         else:
    #     #             c.participants.add(self.request.user)

    #     #     else:
    #     #         c.participants.add(self.request.user)
    #     #     c.save()

    #     #     # print('false')
    #     # likes = get_topic.like.all()
    #     # if likes:
    #     #     print('if likes')
    #     # else:
    #     #     likes.create(user=self.request.user, topic=get_topic,
    #     #                  )
    #     serializer.save(
    #         topic=get_topic,
    #         comments=comments,
    #         host=self.request.user,
    #     )


"""above works  """

# def get_queryset(self):
#     qs = Product.objects.all()
#     q = self.request.GET.get(
#         'q') if self.request.GET.get('q') != None else ''
#     if q:
#         qs = qs.filter(Q(name__contains=q) |
#                        Q(category__name__contains=q) |
#                        #    Q(discount__contains=q) |
#                        Q(id__icontains=q)).distinct()

#     # return self.queryset
#     return qs


class TopicViewSet(ModelViewSet):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    parser_classes = (MultiPartParser, FormParser)
    lookup_field = "slug"
    count = Topic.objects.count()

    def get_queryset(self):
        qs = Topic.objects.all()
        q = self.request.GET.get("q") if self.request.GET.get("q") != None else ""
        if q:
            qs = qs.filter(
                Q(topic__icontains=q)
                | Q(description__icontains=q)
                | Q(created_by__username__icontains=q)
                | Q(id__icontains=q)
            ).distinct()

        # return self.queryset
        return qs

        # return self.queryset.all()

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(created_by=user)

    def perform_update(self, serializer):
        data = self.request.data
        print("my data", data)
        serializer.save()


class FieldViewSet(ModelViewSet):
    queryset = Field.objects.all()
    serializer_class = FieldSerializer


# @api_view(
#     [
#         "GET",
#         "PUT",
#     ]
# )
# # @permission_classes([IsAuthenticated])
# def added_like(request, *args, **kwargs):
#     if request.method == "GET":
#         topic = Topic.objects.all()
#         serializer = TopicSerializer(topic, many=True, context={"request": request})
#         if kwargs:
#             filtered_topics = get_object_or_404(Topic, id=kwargs["pk"])
#             data = TopicSerializer(
#                 filtered_topics, many=False, context={"request": request}
#             )
#             return Response(data.data)

#         return Response(serializer.data)

#     if request.method == "PUT":
#         topic = Topic.objects.all()
#         data = request.data
#         get_id = data["id"]

#         filtered_topic = get_object_or_404(Topic, id=kwargs["pk"])
#         b = filtered_topic.like.all()

#         likes = filtered_topic.like.all()
#         c = likes.first()

#         if likes:
#             if request.user in c.participants.all():
#                 pass
#             else:
#                 new_number = c.likes + 1
#                 c.likes = new_number
#                 c.participants.add(request.user)
#                 c.save()
#         else:
#             create_like = likes.create(
#                 user=request.user,
#                 topic=filtered_topic,
#                 likes=1,
#             )
#             create_like.participants.add(request.user)
#             create_like.save()
#         # serializer.save(topic=filtered_topic, comments=comments,
#         #                 host=request.user,)

#     data = TopicSerializer(filtered_topic, many=False, context={"request": request})
#     return Response(data.data)


@api_view(["GET", "PUT"])
def add_like(request, *args, **kwargs):
    if request.method == "GET":
        if kwargs:
            filtered_topic = get_object_or_404(Topic, id=kwargs["pk"])
            data = TopicSerializer(
                filtered_topic, many=False, context={"request": request}
            )
            return Response(data.data)

        topics = Topic.objects.all()
        serializer = TopicSerializer(topics, many=True, context={"request": request})
        return Response(serializer.data)

    if request.method == "PUT":
        data = request.data
        get_id = data["id"]
        filtered_topic = get_object_or_404(Topic, id=get_id)
        likes = filtered_topic.like.all()

        if likes.exists():
            like = likes.first()
            if request.user in like.participants.all():
                pass
            else:
                new_number = like.likes + 1
                like.likes = new_number
                like.participants.add(request.user)
                like.save()
        else:
            create_like = Like.objects.create(
                user=request.user, topic=filtered_topic, likes=1
            )
            create_like.participants.add(request.user)
            create_like.save()

    data = TopicSerializer(filtered_topic, many=False, context={"request": request})
    return Response(data.data)


# @api_view(["GET", "PUT"])
# def added_like(request, *args, **kwargs):
#     if request.method == "GET":
#         if kwargs:
#             filtered_topic = get_object_or_404(Topic, id=kwargs["pk"])
#             data = TopicSerializer(
#                 filtered_topic, many=False, context={"request": request}
#             )
#             return Response(data.data)

#         topics = Topic.objects.all()
#         serializer = TopicSerializer(topics, many=True, context={"request": request})
#         return Response(serializer.data)

#     if request.method == "PUT":
#         data = request.data
#         get_id = data["id"]
#         filtered_topic = get_object_or_404(Topic, id=get_id)
#         like, created = Like.objects.get_or(
#             user=request.user,
#             topic=filtered_topic,
#             defaults={"likes": 1},
#         )
#         if created:
#             like.participants.add(request.user)

#         if not created and request.user not in like.participants.all():
#             like.likes += 1
#             like.participants.add(request.user)
#             like.save()

#     data = TopicSerializer(filtered_topic, many=False, context={"request": request})
#     return Response(data.data)


# class AddLikesViewSet(viewsets.ModelViewSet):
#     queryset = Topic.objects.all()
#     serializer_class = TopicSerializer
#     permission_classes = [permissions.IsAuthenticated]
#     lookup_field = "pk"

#     @action(detail=True, methods=["put"])
#     def add_like(self, request, pk=None):
#         filtered_topic = get_object_or_404(Topic, id=pk)

#         like, created = Like.objects.update_or_create(
#             user=request.user,
#             topic=filtered_topic,
#             defaults={"likes": 1},
#         )

#         if not created:
#             like.participants.add(request.user)
#             like.save()

#         serializer = TopicSerializer(
#             filtered_topic, many=False, context={"request": request}
#         )
#         return Response(serializer.data)


# class AddLikesViewSet(ModelViewSet):
#     queryset = Like.objects.all()
#     serializer_class = LikeSerializer
#     permission_classes = [permissions.IsAuthenticated]
#     lookup_field = "pk"

#     def get_queryset(self):
#         # topic = self.get_object()
#         like = Like.objects.all()
#         return like

#     @action(detail=True, methods=["put"])
#     def add_likes(self, request, pk=None):
#         topic = self.get_object()
#         user = request.user

#         like, created = Like.objects.get_or_create(user=user, topic=topic)

#         if not created and user not in like.participants.all():
#             like.topic = request.data["topic"]
#             like.likes += 1
#             like.participants.add(user)
#             like.save()

#         serializer = LikeSerializer(like, many=False, context={"request": request})
#         return Response(serializer.data)


# class AddLikesViewSet(ModelViewSet):
#     queryset = Topic.objects.all()
#     serializer_class = TopicSerializer
#     permission_classes = [permissions.IsAuthenticated]
#     lookup_field = "pk"

#     @action(detail=True)
#     def retrieve_topic(self, request, pk=None):
#         topic = self.get_object()
#         serializer = TopicSerializer(topic, many=False, context={"request": request})
#         return Response(serializer.data)

#     @action(detail=True, methods=["put"])
#     def add_likes(self, request, pk=None):
#         topic = self.get_object()
#         user = request.user

#         like, created = Like.objects.get_or_create(user=user, topic=topic)

#         if not created and user not in like.participants.all():
#             like.likes += 1
#             like.participants.add(user)
#             like.save()

#         serializer = TopicSerializer(topic, many=False, context={"request": request})
#         return Response(serializer.data)


class ResponseViewSet(ModelViewSet):
    queryset = Responses.objects.all()
    serializer_class = ResponseSerializer


class LikeViewSet(ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer

    def get_queryset(self):
        topic = Topic.objects.get(id=3)
        see = topic.like.all()
        # print('senior', see)
        return super().get_queryset()
