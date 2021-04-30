from django.contrib import admin
from .models import *


class UserAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'address', 'city', 'state', 'zip_code', 'password')


class ShoeAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'cat', 'desc')


class SizeAdmin(admin.ModelAdmin):
    list_display = ('cat', 's1', 's2', 's3', 's4', 's5')


class PaymentAdmin(admin.ModelAdmin):
    list_display = ('cc_type', 'card_number', 'exp_date', 'user')


class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'order_date', 'total', 'payment', 'user')


# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Shoe, ShoeAdmin)
admin.site.register(Size, SizeAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Order, OrderAdmin)
