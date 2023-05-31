import random
from django.utils.translation import gettext_lazy as _
import datetime  # Create your models here.
import datetime
from django_extensions.db.fields import AutoSlugField
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


def upload_to(instance, filename):
    return "chat/{filename}".format(filename=filename)


class RandomManager(models.Manager):
    def get_query_set(self):
        return super(RandomManager, self).get_query_set().order_by("?")


class RandomManagers(models.Manager):
    def random(self):
        return random.choice(self.all())


class Topic(models.Model):
    created_by = models.ForeignKey(
        User, related_name="topic", on_delete=models.CASCADE, null=True, blank=True
    )
    topic = models.CharField(max_length=250)
    description = models.TextField(max_length=1000, null=True, blank=True)
    slug = AutoSlugField(populate_from=["topic", "description"], max_length=1000)
    updated = models.DateTimeField(
        auto_now=True,
        blank=True,
        null=True,
    )
    created = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    likes = models.IntegerField(default=0)
    load_pic = models.ImageField(_("Image"), upload_to=upload_to, null=True, blank=True)
    objects = models.Manager()  # The default manager.

    random = RandomManager()  # The random-specific manager.
    randoms = RandomManagers()

    class Meta:
        ordering = ("-created",)

    def get_absolute_url(self):
        return "http://127.0.0.1:8000" + f"/api/topics/{self.topic}-{self.description}/"

    @property
    def slugify(self):
        return f"{self.slug}-{self.description}%"

    @property
    def sow(self):
        print("gggg", self)
        return "i am sowing"

    @property
    def children(self):
        # if self.slug:
        #     return True
        return self.objects.comment.all()

    @property
    def is_parent(self):
        if self.parent is None:
            return True
        return False


class Field(models.Model):
    science = "science"
    social = "social"
    law = "law"
    spiritual = "spiritual"
    any = "any"

    SUBJECT_CATEGORY = [
        (science, "science"),
        (social, "social"),
        (law, "law"),
        (spiritual, "spiritual"),
    ]

    category = models.CharField(max_length=200, choices=SUBJECT_CATEGORY, default=any)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="topics")
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    slug = AutoSlugField(
        populate_from=[
            "category",
            "topic",
        ]
    )


class Comments(models.Model):
    host = models.ForeignKey(
        User, related_name="host", null=True, blank=True, on_delete=models.CASCADE
    )
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="comment")
    area_of_discussion = models.ManyToManyField(
        Field, related_name="discussion", blank=True
    )
    participants = models.ManyToManyField(User, related_name="participants")
    comments = models.CharField(max_length=500, null=True, blank=True)
    # body = models.ForeignKey('self', max_length=500,
    #                          null=True, blank=True, on_delete=models.CASCADE)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies"
    )

    class Meta:
        verbose_name = "Comment"
        # verbose_name_plural = 'Comment'

    @property
    def is_children(self):
        # return self.objects.filter(parent=self).first()
        # return self.parent == self
        return "888"
        # return self.objects
        # return self.objects.filter(parent__comments=self).reverse()

    @property
    def is_parent(self):
        if self.parent is None:
            return True
        return False


class Responses(models.Model):
    host = models.ForeignKey(
        User, related_name="hosts", null=True, blank=True, on_delete=models.CASCADE
    )
    comment = models.ForeignKey(
        Comments, on_delete=models.CASCADE, related_name="reply"
    )
    participants = models.ManyToManyField(User, related_name="participant")
    response = models.CharField(max_length=500, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    topic = models.ForeignKey(
        Topic, on_delete=models.CASCADE, related_name="response", blank=True, null=True
    )


class Like(models.Model):
    user = models.ForeignKey(User, related_name="like", on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, related_name="like", on_delete=models.CASCADE)
    participants = models.ManyToManyField(User, related_name="all_participants")
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    loves = models.IntegerField(default=0)
