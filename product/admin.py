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
admin.site.register(Category,  MySpecialAdmin(Category))
admin.site.register(Product,  MySpecialAdmin(Product))

admin.site.register(Discount,  MySpecialAdmin(Discount))
admin.site.register(Tax,  MySpecialAdmin(Tax))
admin.site.register(Cart,  MySpecialAdmin(Cart))
admin.site.register(CartItem,  MySpecialAdmin(CartItem))
