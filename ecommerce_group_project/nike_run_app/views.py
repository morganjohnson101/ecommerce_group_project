from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
import bcrypt
from .models import *


#ENTERING AND LEAVING WEBSITE
def index(request):
    return HttpResponse("Nike Run Shop warming up!!!")


def login(request):
    logged_user=User.objects.filter(email=request.POST['email'])
    if logged_user:
        logged_user=logged_user[0]
        if bcrypt.checkpw(request.POST['pw'].encode(), logged_user.password.encode()):
            request.session['user_id']=logged_user.id
            request.session['user_name']=f"{logged_user.first_name} {logged_user.last_name}"
            return redirect('/welcome')
    return redirect('/')


def logout(request):
    request.session.clear()
    return redirect('/')


#CREATE
def register(request):
    if request.method == 'POST':
        errors=User.objects.validator(request.POST)
        if errors:
            for error in errors:
                messages.error(request, errors[error])
            return redirect('/')

        user_pw=request.POST['pw']
        hash_pw=bcrypt.hashpw(user_pw.encode(), bcrypt.gensalt()).decode()

        new_user= User.objects.create(first_name=request.POST['f_n'], last_name=request.POST['l_n'], email=request.POST['email'],
        address=request.POST['address'], city=request.POST['city'], state=request.POST['state'], zip_code=request.POST['zip_code'], password=hash_pw)
        request.session['user_id']=new_user.id
        request.session['user_name']=f"{new_user.first_name} {new_user.last_name}"
        return redirect('/welcome')
    return redirect('/')

#RENDER

def checkout(request):
    if request.method == "POST":
        errors = Payment.objects.create_validator(request.POST)
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value)
            return redirect('/cart.html')
        else:
            payment = Payment.objects.create(card_number=request.POST['bcode'], exp_date=request.POST['bexpire'], user=User.objects.get(id=request.session['user_id']))
            return redirect('/cart.html')
    return redirect('/cart.html', context)

def shipping(request):
    context = {
        'current_user': User.objects.get(id=request.session['user_id'])
    }
    return render(request, "cart.html", context)





