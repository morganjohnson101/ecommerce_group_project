from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
import bcrypt
from django.db.models import Q
from .models import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count


# Login and Registration
def login(request):
    if request.method == "GET":
        return redirect('/')
    if not User.objects.authenticate(request.POST['email'], request.POST['pw']):
        messages.error(request, 'Invalid Email/Password')
        return redirect('/')
    user = User.objects.get(email=request.POST['email'])
    request.session['user_id'] = user.id
    return redirect('/shoes/category')


def logout(request):
    request.session.flush()
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
        'all_shoes': all_shoes
    }
    return render(request, 'category.html', context)
    return render(request, 'category.html',)


def selectCategory(request, cat):
    context = {
        "all_shoes": Shoe.objects.annotate(price=Count('price')).order_by('price'),
        'men_count': len(Shoe.objects.filter(cat=cat)),
        'women_count': len(Shoe.objects.filter(cat=cat)),
        'girls_count': len(Shoe.objects.filter(cat=cat)),
        'boys_count': len(Shoe.objects.filter(cat=cat)),
    }
    return render(request, 'category.html', context)


def cart(request):
    request.session['saved_cart_items'].pop(0)
    cart_items = request.session['saved_cart_items']
    cart_total = 0
    for i in range(len(cart_items)-1, -1, -1):
        if cart_items[i][0] == cart_items[i-1][0]:
            cart_items[i].append('dup')
            cart_items.pop(i-1)
    for i in range(0, len(cart_items)):
        cart_items[i].insert(2, len(cart_items[i]) - 1 )
        cart_items[i].append( int(cart_items[i][1]) * int(cart_items[i][2]) )
        cart_total += cart_items[i][-1]
    context = {
        'cart_items': cart_items,
        'cart_total': format(cart_total, ',d'),

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
    return redirect('/cart')


def remove(self, shoe):
    shoe_id = str(shoe.id)
    if shoe_id in self.cart:
        # Subtract 1 from the quantity
        self.cart[shoe_id]['quantity'] -= 1
        # If the quantity is now 0, then delete the item
        if self.cart[shoe_id]['quantity'] == 0:
            del self.cart[product_id]
        self.save()


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