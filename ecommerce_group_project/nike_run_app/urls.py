from django.urls import path
from nike_run_app import views


urlpatterns = [
    path('', views.index),
    path('login', views.login),
    path('logout', views.logout),
    path('register', views.register),
    path('shoes/category/<str:cat>', views.category),
    path('shoes/show/<int:id>', views.show),
    path('shipping', views.shipping),
    path('checkout', views.checkout),
]
