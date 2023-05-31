from django.contrib import admin

from django.db.models import ManyToOneRel, ForeignKey, OneToOneField


# Register your models here.

from .models import *


def MySpecialAdmin(model): return type('SubClass'+model.__name__, (admin.ModelAdmin,), {
    'list_display': [x.name for x in model._meta.fields],
    'list_select_related': [x.name for x in model._meta.fields if isinstance(x, (ManyToOneRel, ForeignKey, OneToOneField,))]
})


class TopicAdmin(admin.ModelAdmin):
    list_display = [x.name for x in Topic._meta.fields]


class FieldAdmin(admin.ModelAdmin):
    list_display = [x.name for x in Field._meta.fields]


class CommentsAdmin(admin.ModelAdmin):
    list_display = [x.name for x in Comments._meta.fields]


class ResponsesAdmin(admin.ModelAdmin):
    list_display = [x.name for x in Responses._meta.fields]


class LikeAdmin(admin.ModelAdmin):
    list_display = [x.name for x in Like._meta.fields]


admin.site.register(Topic, TopicAdmin)
admin.site.register(Comments, CommentsAdmin)
admin.site.register(Field, FieldAdmin)
admin.site.register(Responses, ResponsesAdmin)
admin.site.register(Like, LikeAdmin)
