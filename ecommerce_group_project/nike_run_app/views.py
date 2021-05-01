from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
import bcrypt
from django.db.models import Q
from .models import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

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
        errors = User.objects.validator(request.POST)
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
        'all_shoes': all_shoes
    }
    return render(request, 'category.html', context)


def selectCategory(request, cat):
    context = {
        'men_count': len(Shoe.objects.filter(cat=cat)),
    }
    return render(request, 'category.html', context)


def cart(request):
    context = {
        'shoe_name': request.session["cart_shoe_name"],
        'shoe_price': request.session["cart_shoe_price"],
    }
    return render(request, 'cart.html', context)


def addToCart(request):
    option_string = request.POST['size']
    option_list = option_string.split(',')
    request.session["cart_shoe_name"] = option_list[0]
    request.session["cart_shoe_price"] = option_list[1]
    print(request.session.items())
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