from __future__ import unicode_literals

from django.shortcuts import render, redirect

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from TailedProducts.models import Product, ProductPrice, UserToProduct, DisplayProduct, DisplayDatePriceProduct
from TailedProducts.helpers import filters

import json
from spiders import GiantSpiders
import httplib
from django.contrib import messages
# from utils.helpers import get_current_date
# from utils.data import MAX_DIFFERENT_ITEMS, MAX_UNAVAILABLE_ITEMS

#endpoint "/"
def index_view(request):
    if request.user.is_authenticated():
        return index_view_logged_in(request)
    else:
        return index_view_logged_out(request)

def index_view_logged_out(request):
    reset_session(request)
    (diff_products, unavailable_products) = filters._get_notification_products(request, False)
    total_monitored_products = Product.objects.all()

    (min_var_product, max_var_product) = filters._get_product_with_highest_price_variation(-1, False)

    return render(request, 'index.html', {'diff_products': diff_products,
                                                   'diff_count': len(diff_products),
                                                   'unavailable_products': unavailable_products,
                                                   'unavailable_count': len(unavailable_products),
                                                   'total_monitored_products': len(total_monitored_products),
                                                   'most_changed_product': max_var_product,
                                                   'least_changed_product': min_var_product
                                                   })

def index_view_logged_in(request):

    (diff_products, unavailable_products) = filters._get_notification_products(request)
    total_monitored_products = filters._total_products_monitored_by_user(request.user.id)

    (min_var_product, max_var_product) = filters._get_product_with_highest_price_variation(request.user.id)

    return render(request, 'index.html', {'diff_products': diff_products,
                                                   'diff_count': len(diff_products),
                                                   'unavailable_products': unavailable_products,
                                                   'unavailable_count': len(unavailable_products),
                                                   'total_monitored_products': total_monitored_products,
                                                   'most_changed_product': max_var_product,
                                                   'least_changed_product': min_var_product
                                                   })

@login_required(login_url='/login')
def dashboard_view(request):

    (diff_products, unavailable_products) = filters._get_notification_products(request)
    total_monitored_products = filters._total_products_monitored_by_user(request.user.id)

    (min_var_product, max_var_product) = filters._get_product_with_highest_price_variation(request.user.id)

    return render(request, 'user/dashboard.html', {'diff_products': diff_products,
                                                   'diff_count': len(diff_products),
                                                   'unavailable_products': unavailable_products,
                                                   'unavailable_count': len(unavailable_products),
                                                   'total_monitored_products': total_monitored_products,
                                                   'most_changed_product': max_var_product,
                                                   'least_changed_product': min_var_product
                                                   })


#endpoint "/login"
def login_view(request):

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is None:
            messages.error(request, "error! invalid username or password!")
            return redirect('login')
        else:
            login(request, user)
            page = get_redirect_url(request)
            if not page:
                return redirect('index')
            return redirect(page)
    if not request.user.is_authenticated():
        reset_session(request)

    return render(request, 'user/login.html', )

def get_redirect_url(request):
    #'http://localhost:8006/login/?next=/dashboard/'
    if 'HTTP_REFERER' in request.environ:
        referer = request.environ['HTTP_REFERER']
        if 'next' in referer:
            next_page = referer.split("next=")
            next_page = next_page[1].replace('/', '')
            return next_page
        else:
            return ''
    else:
        return ''


#endpoint "/register"
def register_view(request):

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        cpassword = request.POST['confirm-password']

        if password != cpassword:
            messages.error(request, "error! password is not the same!")
            return redirect('register')

        users = User.objects.filter(username__exact=username)
        if users.count > 0:
            messages.error(request, "error! username already exists!")
            return redirect('register')
        else:
            user = User.objects.create_user(username, email, password)
            user.save()

        auser = authenticate(username=username, password=password)
        login(request, auser)
        return redirect('index')

    return render(request, 'user/register.html', )

#endpoint "/profile"
@login_required(login_url='/login')
def profile_view(request):
    product_list = filters._get_products_by_user(request.user.id)
    (diff_products, unavailable_products) = filters._get_notification_products(request)

    return render(request, 'user/profile.html', {'products':product_list,
                                                 'diff_products': diff_products,
                                                 'diff_count': len(diff_products),
                                                 'unavailable_products': unavailable_products,
                                                 'unavailable_count': len(unavailable_products)})


#endpoint "/my-products"
@login_required(login_url='/login')
def my_products_view(request):
    product_list = filters._get_products_by_user(request.user.id)
    new_products_list = filters.sort_products_by_importance(product_list)
    (diff_products, unavailable_products) = filters._get_notification_products(request)

    return render(request, 'products/my-products.html', {'products':new_products_list,
                                                       'diff_products': diff_products,
                                                       'diff_count': len(diff_products),
                                                       'unavailable_products': unavailable_products,
                                                       'unavailable_count': len(unavailable_products)
                                                       })
#action used to delete a product
@login_required(login_url='/login')
def delete_product(request, id):

    UserToProduct.objects.filter(product_id__exact=id, user_id__exact=request.user.id).delete()

    remaining_user_products = UserToProduct.objects.filter(product_id__exact=id)
    if remaining_user_products.count() == 0:
        ProductPrice.objects.filter(product_id__exact=id).delete()
        Product.objects.filter(id__exact=id).delete()

    #recalculate unavailable products
    product_list = filters._get_products_by_user(request.user.id)
    unavailable_product_ids = [x.id for x in product_list if x.available == False]
    request.session['unavailable_product_ids'] = unavailable_product_ids

    return HttpResponse('')

#action used to add a product
@login_required(login_url='/login')
def add_new_product(request):

    if request.method == 'POST':
        d = json.loads(request.POST['json'])
        product_name = d['product_name']
        product_price = d['product_price']
        product_url = d['product_url']
        product_shop = d['product_shop']

        # create module and add in DB
        prod = Product.objects.filter(name__exact=product_name)

        if prod.count() == 0:
            # Create new product in Product table
            new_prod = Product()
            new_prod.name = product_name
            new_prod.shop = product_shop
            new_prod.url = product_url
            new_prod.save()

            # Create new entry in ProductPrice table
            new_prod_price = ProductPrice()
            new_prod_price.price = product_price
            new_prod_price.product = new_prod
            new_prod_price.save()

            # Create a new entry in UserToProduct table
            new_user_product = UserToProduct()
            new_user_product.product = new_prod
            new_user_product.user = request.user
            new_user_product.save()
        else:
            first_prod = prod[0]
            # check if the current user is not already monitoring the product
            user_product = UserToProduct.objects.filter(product__exact=first_prod.id, user__exact=request.user.id)
            if user_product.count() == 0:
                # Create a new entry in UserToProduct table
                new_user_product = UserToProduct()
                new_user_product.product = first_prod
                new_user_product.user = request.user
                new_user_product.save()

    (diff_products, unavailable_products) = filters._get_notification_products(request)
    return render(request, 'products/add-product.html', {'diff_products': diff_products,
                                                         'diff_count': len(diff_products),
                                                         'unavailable_products': unavailable_products,
                                                         'unavailable_count': len(unavailable_products)
                                                         })


@login_required(login_url='/login')
def validate_product(request):
    if request.method == 'POST':
        d = json.loads(request.POST['json'])
        product_url = d['product-url']
    data = {}
    spider = GiantSpiders.EmagSpider()
    if httplib.OK == spider.req_product(product_url):
        prod = spider.get_product()
        data['status'] = 'valid'
        data['pname'] = prod.name
        data['pprice'] = prod.price
        data['purl'] = product_url
        data['pshop'] = 'emag'
    else:
        data['status'] = 'invalid'

    return HttpResponse(json.dumps(data), content_type='application/json')


# def _get_display_products_by_products(products):
#     display_products = []
#     idx = 1
#     for product in products:
#         prod = DisplayProduct()
#         prod.name = product.name
#         prod.url = product.url
#         prod.shop = product.shop
#         prod.id = product.id
#         prod.available = product.available
#         prod.idx = idx
#         display_products.append(prod)
#         prod_dict = _compute_product_trend_price_percent(product.id)
#         prod.trend = prod_dict["trend"]
#         prod.price = prod_dict["price"]
#         prod.percent = prod_dict["percent"]
#         idx += 1
#     return display_products

# def _compute_product_trend_price_percent(product_id):
#     product_prices = ProductPrice.objects.filter(product_id__exact=product_id)
#     if product_prices.count() <= 0:
#         return {"trend":"NO_RECORD", "price":-1, "percent": 0}
#     elif product_prices.count() == 1:
#         return {"trend": "FIRST_ENTRY", "price": product_prices[0].price, "percent":0}
#     elif product_prices.count() >= 2:
#         last_products = product_prices[product_prices.count()-2:]
#         prev_price = last_products[0].price
#         curr_price = last_products[1].price
#         trend = "EQ"
#         percent = 0
#         if prev_price > curr_price:
#             percent = int((prev_price - curr_price) / prev_price * 100)
#             trend = "DESC"
#             if percent == 0:
#                 percent = 1
#         elif prev_price < curr_price:
#             percent = int((curr_price - prev_price) / prev_price * 100)
#             trend = "ASC"
#             if percent == 0:
#                 percent = 1
#         return {"trend": trend, "price": curr_price, "percent": percent}
#     return {"trend": "NO_RECORD", "price": -1, "percent": 0}


#iframe to be displayed in a modal window
def display_product(request, id):
    product = Product.objects.get(id=id)
    dprod = DisplayProduct()
    dprod.name = product.name
    dprod.shop = product.shop
    dprod.url = product.url
    dprod.price = 20

    dates_prices =  ProductPrice.objects.filter(product_id__exact=product.id)
    for item in dates_prices:
        p = DisplayDatePriceProduct(item.date, item.price)
        dprod.date_prices.append(p)

    return render(request, 'products/product-modal.html', {'data': dprod})

#Returns array of DisplayProduct type containing all products monitored by a specific user
# def _get_products_by_user(user_id):
#     user_products = UserToProduct.objects.filter(user__exact=user_id).values('product_id')
#     products = Product.objects.filter(id__in=user_products)
#
#     display_products = _get_display_products_by_products(products)
#     return display_products

#Returns array of DisplayProduct type containing all products
# def _get_all_products():
#     products = Product.objects.all()
#     display_products = _get_display_products_by_products(products)
#     return display_products

#get list of products that has the price changed in comparison to the previous day
# def _get_notification_products(request, by_user_id = True):
#     session_date = request.session.get('updated_date')
#     if not session_date:
#         create_today_product_id_session(request, by_user_id)
#     else:
#         if request.session['updated_date'] == str(get_current_date()):
#             diff_product_ids = request.session.get('diff_product_ids')
#             unavailable_product_ids = request.session.get('unavailable_product_ids')
#             if diff_product_ids is None or unavailable_product_ids is None:
#                 create_product_id_session(request, by_user_id)
#         else:
#             create_today_product_id_session(request, by_user_id)
#     diff_product_ids = request.session.get('diff_product_ids')
#     diff_products = _get_products_by_product_ids(diff_product_ids)
#     unavailable_product_ids = request.session.get('unavailable_product_ids')
#     unavailable_products = _get_products_by_product_ids(unavailable_product_ids)
#     return (diff_products, unavailable_products)

#get display products from a list of product ids
# def _get_products_by_product_ids(ids):
#     products = Product.objects.filter(id__in=ids)
#     return _get_display_products_by_products(products)

#create session data for list of changed priced products
# def create_today_product_id_session(request, by_user_id = True):
#     request.session['updated_date'] = str(get_current_date())
#     create_product_id_session(request, by_user_id)

#create session data for list of changed priced products by current date
#the session data will be refreshed every day
# def create_product_id_session(request, by_user_id = True):
#     product_list = []
#     if by_user_id == True:
#         product_list = _get_products_by_user(request.user.id)
#     else:
#         product_list = _get_all_products()
#     unavailable_product_ids = [x.id for x in product_list if x.available == False]
#     diff_product_ids = [x.id for x in product_list if x.trend == "DESC" or x.trend == "ASC"]
#     request.session['diff_product_ids'] = diff_product_ids[:MAX_DIFFERENT_ITEMS]
#     request.session['unavailable_product_ids'] = unavailable_product_ids[:MAX_UNAVAILABLE_ITEMS]

# def _total_products_monitored_by_user(user_id):
#     product = UserToProduct.objects.filter(user_id__exact=user_id)
#     return product.count()

def reset_session(request):
    session_date = request.session.get('updated_date')
    if session_date:
        del request.session['updated_date']
    session_date = request.session.get('diff_product_ids')
    if session_date:
        del request.session['diff_product_ids']
    session_date = request.session.get('unavailable_product_ids')
    if session_date:
        del request.session['unavailable_product_ids']

from .utils import data
import time

def update_prices():
    monitored_products = Product.objects.all()
    for product in monitored_products:
        time.sleep(1)
        shop = product.shop

        if shop == 'emag':
            spider = GiantSpiders.EmagSpider()
            response = spider.req_product(product.url)
            if httplib.OK == response:
                prod = spider.get_product()
                price = prod.price

                new_prod_price = ProductPrice()
                new_prod_price.price = price
                new_prod_price.product = product
                new_prod_price.save()
                print(prod.name + ' - OK')
            elif data.PRODUCT_UNAVAILABLE == response:
                print(product.name + ' - UNAVAILABLE')
                product.available = False
                product.save()
            else:
                print(product.name + ' - NOK')
        else:
            print('SHOP NOT SUPPORTED: ' + shop)