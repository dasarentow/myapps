from django.contrib import admin

from django.db.models import ManyToOneRel, ForeignKey, OneToOneField

from . import models
# Register your models here.

from .models import *


def MySpecialAdmin(model): return type('SubClass'+model.__name__, (admin.ModelAdmin,), {
    'list_display': [x.name for x in model._meta.fields],
    'list_select_related': [x.name for x in model._meta.fields if isinstance(x, (ManyToOneRel, ForeignKey, OneToOneField,))]
})


# class LeadAdmin(admin.ModelAdmin):
#     list_display = [x.name for x in Lead._meta.fields]


# admin.site.register(Post,  MySpecialAdmin(Post))
admin.site.register(ResProduct,  MySpecialAdmin(ResProduct))
admin.site.register(PaymentHistory,  MySpecialAdmin(PaymentHistory))
