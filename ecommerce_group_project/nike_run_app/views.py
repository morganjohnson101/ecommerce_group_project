from django.shortcuts import render, HttpResponse, redirect
# from django.contrib import messages
# import bcrypt
# from .models import *

# Create your views here.
def index(request):
    return HttpResponse("Nike Run Shop warming up!!!")
