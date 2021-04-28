from django.contrib import admin
from .models import *

class UserAdmin(admin.ModelAdmin):
    list_display= ('first_name', 'last_name', 'email', 'address', 'city', 'state', 'zip_code', 'password')

class ShoeAdmin(admin.ModelAdmin):
    # list_display=('shoe_name', 'size', 'price', 'shoe_category', 'buyer')
    list_display=('shoe_name', 'size', 'price', 'shoe_category')

class PaymentAdmin(admin.ModelAdmin):
    list_display=('cc_type', 'card_number', 'exp_date', 'user')

# class CartAdmin(admin.ModelAdmin):
#     list_display=('shoes')

class OrderAdmin(admin.ModelAdmin):
    list_display=('order_id', 'order_date', 'total', 'payment', 'user')

# class ImageAdmin(admin.ModelAdmin):
#     list_display=('image_path')


# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Shoe, ShoeAdmin)
admin.site.register(Payment, PaymentAdmin)
# admin.site.register(Cart, CartAdmin)
admin.site.register(Order, OrderAdmin)
# admin.site.register(Image, ImageAdmin)
