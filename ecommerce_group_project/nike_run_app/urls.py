from django.urls import path
from nike_run_app import views


urlpatterns = [
    path('', views.index),
    path('login', views.login),
    path('logout', views.logout),
    path('register', views.register),
    path('shoes/category/<str:cat>', views.selectCategory),
    path('shoes/category', views.category),
    path('shoes/show/<int:id>', views.show),
    # path('update-cart', views.updateCart),
    # path('delete-cart', views.deleteCart),
    path('add-to-cart', views.addToCart),
    path('cart', views.cart),
    path('search_shoes', views.search_shoes, name='search-shoes'),
    path('cart/billing', views.billing),
    #path('shipping', views.shipping),
    #path('checkout', views.checkout),
]
