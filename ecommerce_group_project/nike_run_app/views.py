from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
import bcrypt
from .models import *
from django.db.models import Count


# Login and Registration
def login(request):
    logged_user = User.objects.filter(email=request.POST['email'])
    if logged_user:
        logged_use = logged_user[0]
        if bcrypt.checkpw(request.POST['pw'].encode(), logged_user.password.encode()):
            request.session['user_id'] = logged_user.id
            request.session['user_name'] = f"{logged_user.first_name} {logged_user.last_name}"
            request.session['cart_selected_quantity'] = 0
            return redirect('/welcome')
    return redirect('/')


def logout(request):
    request.session.clear()
    return redirect('/')


def register(request):
    if request.method == 'POST':
        errors = User.objects.create_validator(request.POST)
        if errors:
            for error in errors:
                messages.error(request, errors[error])
            return redirect('/')

        user_pw = request.POST['pw']
        hash_pw = bcrypt.hashpw(user_pw.encode(), bcrypt.gensalt()).decode()
        new_user = User.objects.create(
            first_name=request.POST['f_name'], 
            last_name=request.POST['l_n'], 
            email=request.POST['email'], 
            address=request.POST['address'], 
            city=request.POST['city'], 
            state=request.POST['state'], 
            zip_code=request.POST['zip_code'], 
            password=hash_pw)
        request.session['user_id'] = new_user.id
        request.session['user_name'] = f"{new_user.first_name} {new_user.last_name}"
        return redirect('/shoes/category')
    return redirect('/')


# Render Templates
def index(request):
    return render(request, 'loginreg.html')


def show(request, id):
    this_shoe = Shoe.objects.get(id=id)
    context = {
        'shoe': this_shoe,
        'size': Size.objects.get(cat=this_shoe.cat),
    }
    return render(request, 'show.html', context)


def category(request):
    return render(request, 'category.html',)


def selectCategory(request, cat):
    context = {
        "all_shoes": Shoe.objects.annotate(price=Count('price')).order_by('price'),
        'men_count': len(Shoe.objects.filter(cat=cat)),
    }
    return render(request, 'category.html', context)


def cart(request):
    cart_items = []
    cart_item_quantity = []
    for i in range(1, len(request.session['saved_cart_items'])):
        cart_items.append(request.session['saved_cart_items'][i])
    print(cart_items)
    for i in range(0, len(cart_items)):
        count = 0
        if cart_items[i] == cart_items[i+1]:
            count += 1
            cart_items.pop(i)
    context = {
        'session_cart_items': cart_items,
        #'shoe_price': request.session["cart_shoe_price"],
    }
    return render(request, 'cart.html', context)


def addToCart(request):
    option_string = request.POST['size']
    option_list = option_string.split(',')
    if not 'saved_cart_items' in request.session or not request.session['saved_cart_items']:
        request.session['saved_cart_items'] = ['initial']
        request.session['saved_cart_items'].append(option_list)
    else:
        saved_list = request.session['saved_cart_items']
        saved_list.append(option_list)
        request.session['saved_cart_items'] = saved_list
    #request.session["cart_shoe_name"] = option_list[0]
    #request.session["cart_shoe_price"] = option_list[1]
    #print(request.session["saved_cart_items"])
    print(request.session['saved_cart_items'])
    print(len(request.session['saved_cart_items']))
    #request.session.flush()
    #print(request.session.items())
    return redirect('/cart')

def billing(request):
    if request.method == "POST":
        errors = Payment.objects.create_validator(request.POST)
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value)
            return redirect('/cart')
        else:
            payment = Payment.objects.create(cc_type=request.POST['cc_type'], card_number=request.POST['card_number'], ss_code=request.POST['ss_code'], exp_date=request.POST['exp_date'], user=User.objects.get(id=request.session['user_id']))
            messages.success(request, "payment processed") 
            return redirect('/cart')
    return redirect('/cart')
