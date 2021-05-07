from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
import bcrypt
from django.db.models import Q
from .models import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count
from collections import defaultdict


# Login and Registration
def login(request):
    logged_user = User.objects.filter(email=request.POST['email'])
    if logged_user:
        logged_use = logged_user[0]
        if bcrypt.checkpw(request.POST['pw'].encode(), logged_user.password.encode()):
            request.session['user_id'] = logged_user.id
            request.session['user_name'] = f"{logged_user.first_name} {logged_user.last_name}"
            request.session['cart_selected_quantity'] = 0
            return redirect('/shoes/category/')
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
            first_name=request.POST['f_n'], 
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
    all_shoes = Shoe.objects.all()
    per_page = 15
    page = request.GET.get('page',1)
    paginator = Paginator(all_shoes,per_page)
    try:
        all_shoes=paginator.page(page)
    except PageNotAnInteger:
        all_shoes=paginator.page(1)
    except EmptyPage: 
        all_shoes=paginator.page(paginator.num_pages)
    context = {
        'all_shoes': all_shoes,
        'men_count': len(Shoe.objects.filter(cat='men')),
        'women_count': len(Shoe.objects.filter(cat='women')),
        'girls_count': len(Shoe.objects.filter(cat='girls')),
        'boys_count': len(Shoe.objects.filter(cat='boys')),
    }
    return render(request, 'category.html', context)
    return render(request, 'category.html',)


def selectCategory(request, cat):
    context = {
        "all_shoes": Shoe.objects.annotate(price=Count('price')).order_by('price'),
    }
    return render(request, 'category.html', context)


def cartTotal(items):
    total = 0
    for i in range(0, len(items)):
        total += int(items[i][-1])
    return total


current_items = []

def updateCart(request):
    global current_items
    item_index = request.POST['update_item']
    current_items[int(item_index)][3] = request.POST['update_input']
    current_items[int(item_index)][-1] = int(current_items[int(item_index)][2]) * int(request.POST['update_input'])
    context = {
    'cart_items': current_items,
    'cart_total': format(cartTotal(current_items), ',d')
    }
    return render(request, 'cart.html', context)


def deleteCart(request):
    global current_items
    item_index = request.POST['delete_item']
    current_items.pop(int(item_index))
    return redirect('/cart')


def cart(request):
    global current_items
    request.session['saved_items'].pop(0)
    cart_items = request.session['saved_items']
    if len(cart_items) == 1:
        print('length of cart is 1')
        cart_items[0].insert(0, 0)
        cart_items[0].insert(3, len(cart_items[0])-2)
        cart_items[0].append( int(cart_items[0][2]) * int(cart_items[0][3]))
    else:
        for i in range(0, len(cart_items)):
            cart_items[i].insert(0, i)
            cart_items[i].insert(3, len(cart_items[i])-2 )
            cart_items[i].append( int(cart_items[i][2]) * int(cart_items[i][3])) 
    current_items = cart_items
    print(current_items)
    context = {
    'cart_items': current_items,
    'cart_total': format(cartTotal(current_items), ',d')
    }
    return render(request, 'cart.html', context)



def addToCart(request):
    option_string = request.POST['size']
    option_list = option_string.split(',')
    if not 'saved_items' in request.session or not request.session['saved_items']:
        request.session['saved_items'] = ['initial']
        request.session['saved_items'].append(option_list)
    else:
        saved_list = request.session['saved_items']
        saved_list.append(option_list)
        request.session['saved_items'] = saved_list
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

# def search_shoes(request):
#     if request.method == "POST":
#         searched = request.POST('searched')
#         shoes = Shoe.objects.filter(name__contains=searched)
    
#         return render(request, 'search_shoes.html',{'searched':searched,'shoes':shoes})
#     else:
#         return render(request, 'search_shoes.html',{})
def normalize_query(query_string, findterms=re.compile(r'"([^"]+)"|(\S+)').findall, normspace=re.compile(r'\s{2,}').sub):
    ''' Splits the query string in invidual keywords, getting rid of unecessary spaces
        and grouping quoted words together.
        Example:
        . . . normalize_query('  some random  words "with   quotes  " and   spaces')
        ['some', 'random', 'words', 'with quotes', 'and', 'spaces']

'''
    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)]

def get_query(query_string, search_fields):
    ''' Returns a query, that is a combination of Q objects. That combination
        aims to search keywords within a model by testing the given search fields.
    '''
    query = None # Query to search for every search term
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query

def search_shoes(request):
    query_string = ''
    found_entries = None
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q']
        entry_query = get_query(query_string, ['name'])
        found_entries = Shoe.objects.filter(entry_query).order_by('id')
    context = { 
        'query_string': query_string,
        'found_entries': found_entries,
    
    }
    return render(request, 'category.html', context)