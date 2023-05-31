from django.contrib import admin

from django.db.models import ManyToOneRel, ForeignKey, OneToOneField


# Register your models here.

from .models import *


def MySpecialAdmin(model): return type('SubClass'+model.__name__, (admin.ModelAdmin,), {
    'list_display': [x.name for x in model._meta.fields],
    'list_select_related': [x.name for x in model._meta.fields if isinstance(x, (ManyToOneRel, ForeignKey, OneToOneField,))]
})


class TopicAdmin(admin.ModelAdmin):
    list_display = [x.name for x in DsApps._meta.fields]




admin.site.register(DsApps, TopicAdmin)
