from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r"field", FieldViewSet, basename="field")
router.register(r"topic", TopicViewSet, basename="topic")
router.register(r"comment", CommentViewSet, basename="comment")
router.register(r"response", ResponseViewSet, basename="response")

router.register(r"like", LikeViewSet, basename="like")
# router.register(r"add-like", AddLikesViewSet, basename="add-like")

app_name = "chat"
urlpatterns = [
    # path("get-comments/", comments, name="get-comments"),
    path("add-likes/<str:pk>/", add_like, name="add-likes-detail"),
    path("add-likes/", add_like, name="add-likes"),
    path(
        "",
        include(router.urls),
    ),
]
