from __future__ import unicode_literals

from django.shortcuts import render, redirect

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from TailedProducts.models import Product, ProductPrice, UserToProduct, DisplayProduct, DisplayDatePriceProduct

import json
from spiders import GiantSpiders
import httplib
from django.contrib import messages
from utils.helpers import get_current_date

#endpoint "/"
def index_view(request):

    (diff_products, unavailable_products) = _get_notification_products(request)
    return render(request, 'blank.html', {'diff_products': diff_products,
                                          'diff_count': len(diff_products),
                                          'unavailable_products': unavailable_products,
                                          'unavailable_count': len(unavailable_products)
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
            return redirect('index')

    return render(request, 'user/login.html', )

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
@login_required
def profile_view(request):
    product_list = _get_products_by_user(request.user.id)
    (diff_products, unavailable_products) = _get_notification_products(request)

    return render(request, 'user/profile.html', {'products':product_list,
                                                 'diff_products': diff_products,
                                                 'diff_count': len(diff_products),
                                                 'unavailable_products': unavailable_products,
                                                 'unavailable_count': len(unavailable_products)})

#endpoint "/dashboard"
@login_required
def dashboard_view(request):
    product_list = _get_products_by_user(request.user.id)
    (diff_products, unavailable_products) = _get_notification_products(request)

    return render(request, 'products/dashboard.html', {'products':product_list,
                                                       'diff_products': diff_products,
                                                       'diff_count': len(diff_products),
                                                       'unavailable_products': unavailable_products,
                                                       'unavailable_count': len(unavailable_products)
                                                       })
#action used to delete a product
@login_required
def delete_product(request, id):

    current_url = request.path

    UserToProduct.objects.filter(product_id__exact=id, user_id__exact=request.user.id).delete()

    remaining_user_products = UserToProduct.objects.filter(product_id__exact=id)
    if remaining_user_products.count() == 0:
        ProductPrice.objects.filter(product_id__exact=id).delete()
        Product.objects.filter(id__exact=id).delete()

    #recalculate unavailable products
    product_list = _get_products_by_user(request.user.id)
    unavailable_product_ids = [x.id for x in product_list if x.available == False]
    request.session['unavailable_product_ids'] = unavailable_product_ids
    return dashboard_view(request)

#action used to add a product
@login_required
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

    (diff_products, unavailable_products) = _get_notification_products(request)
    return render(request, 'products/add-product.html', {'diff_products': diff_products,
                                                         'diff_count': len(diff_products),
                                                         'unavailable_products': unavailable_products,
                                                         'unavailable_count': len(unavailable_products)
                                                         })

# @login_required
# def add_tail_view(request):
#     form_data = {}
#     form_data['form'] = LoginForm()
#
#     if request.method == 'POST':
#         product_name = request.POST['product_name']
#         product_price = request.POST['product_price']
#         product_url = request.POST['product_url']
#         product_shop = request.POST['product_shop']
#
#         #create module and add in DB
#         prod = Product.objects.filter(name__exact=product_name)
#
#         if prod.count() == 0:
#             #Create new product in Product table
#             new_prod = Product()
#             new_prod.name = product_name
#             new_prod.shop = product_shop
#             new_prod.url = product_url
#             new_prod.save()
#
#             # Create new entry in ProductPrice table
#             new_prod_price = ProductPrice()
#             new_prod_price.price = product_price
#             new_prod_price.product = new_prod
#             new_prod_price.save()
#
#             # Create a new entry in UserToProduct table
#             new_user_product = UserToProduct()
#             new_user_product.product = new_prod
#             new_user_product.user = request.user
#             new_user_product.save()
#         else:
#             first_prod = prod[0]
#             #check if the current user is not already monitoring the product
#             user_product = UserToProduct.objects.filter(product__exact=first_prod.id, user__exact=request.user.id)
#             if user_product.count() == 0:
#                 # Create a new entry in UserToProduct table
#                 new_user_product = UserToProduct()
#                 new_user_product.product = first_prod
#                 new_user_product.user = request.user
#                 new_user_product.save()
#
#         return redirect('add-tail-view')
#
#     return render(request, 'add-tail.html', form_data)

@login_required
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

# @login_required
# def my_tails(request):
#     user_products = UserToProduct.objects.filter(user__exact=request.user.id).values('product_id')
#     products = Product.objects.filter(id__in=user_products)
#
#     display_products = _get_display_products_by_products(products)
#
#     return render(request, 'my-tails.html', {'data': display_products})

def _get_display_products_by_products(products):
    display_products = []
    idx = 1
    for product in products:
        prod = DisplayProduct()
        prod.name = product.name
        prod.url = product.url
        prod.shop = product.shop
        prod.id = product.id
        prod.available = product.available
        prod.idx = idx
        display_products.append(prod)
        prod_dict = _compute_product_trend_price_percent(product.id)
        prod.trend = prod_dict["trend"]
        prod.price = prod_dict["price"]
        prod.percent = prod_dict["percent"]

        idx += 1

        # TO DO: sort by time
        # product_prices = ProductPrice.objects.filter(product_id__exact=product.id)
        # if product_prices.count() > 1:
        #     last_price = product_prices[0].price
        #     for prod_price in product_prices:
        #         price = prod_price.price
        #         if last_price > price:
        #             prod.trend = "DESC"
        #             prod.percent = int((last_price - price)/last_price * 100)
        #             if prod.percent == 0:
        #                 prod.percent = 1
        #         elif last_price < price:
        #             prod.trend = "ASC"
        #             prod.percent = int((price - last_price)/last_price * 100)
        #             if prod.percent == 0:
        #                 prod.percent = 1
        #         else:
        #             prod.trend = "EQ"
        #         prod.price = price
        #         last_price = price
        # elif product_prices.count() == 1:
        #     prod.price = product_prices[0].price
        #     prod.trend = "FIRST_ENTRY"
        # else:
        #     prod.price = -1
        #     prod.trend = "NO RECORD"
    return display_products

def _compute_product_trend_price_percent(product_id):
    product_prices = ProductPrice.objects.filter(product_id__exact=product_id)
    if product_prices.count() <= 0:
        return {"trend":"NO_RECORD", "price":-1, "percent": 0}
    elif product_prices.count() == 1:
        return {"trend": "FIRST_ENTRY", "price": product_prices[0].price, "percent":0}
    elif product_prices.count() >= 2:
        last_products = product_prices[product_prices.count()-2:]
        prev_price = last_products[0].price
        curr_price = last_products[1].price
        trend = "EQ"
        percent = 0
        if prev_price > curr_price:
            percent = int((prev_price - curr_price) / prev_price * 100)
            trend = "DESC"
            if percent == 0:
                percent = 1
        elif prev_price < curr_price:
            percent = int((curr_price - prev_price) / prev_price * 100)
            trend = "ASC"
            if percent == 0:
                percent = 1
        return {"trend": trend, "price": curr_price, "percent": percent}
    return {"trend": "NO_RECORD", "price": -1, "percent": 0}


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
def _get_products_by_user(user_id):
    user_products = UserToProduct.objects.filter(user__exact=user_id).values('product_id')
    products = Product.objects.filter(id__in=user_products)

    display_products = _get_display_products_by_products(products)
    # idx = 1
    # for product in products:
    #     prod = DisplayProduct()
    #     prod.name = product.name
    #     prod.url = product.url
    #     prod.shop = product.shop
    #     prod.id = product.id
    #     prod.idx = idx
    #
    #     # TO DO: sort by time
    #     product_prices = ProductPrice.objects.filter(product_id__exact=product.id)
    #     if product_prices.count() > 1:
    #         last_price = product_prices[0].price
    #         for prod_price in product_prices:
    #             price = prod_price.price
    #             if last_price > price:
    #                 prod.trend = "DESC"
    #                 prod.percent = int(last_price/price * 100) - 100
    #             elif last_price < price:
    #                 prod.trend = "ASC"
    #                 prod.percent = int(price/last_price * 100) - 100
    #             else:
    #                 prod.trend = "EQ"
    #             prod.price = price
    #             last_price = price
    #     elif product_prices.count() == 1:
    #         prod.price = product_prices[0].price
    #     else:
    #         prod.price = -1
    #         prod.trend = "NO RECORD"
    #
    #     display_products.append(prod)
    #     idx += 1

    return display_products

#get list of products that has the price changed in comparison to the previous day
def _get_notification_products(request):
    session_date = request.session.get('updated_date')
    if not session_date:
        create_today_product_id_session(request)
    else:
        if request.session['updated_date'] == str(get_current_date()):
            diff_product_ids = request.session.get('diff_product_ids')
            unavailable_product_ids = request.session.get('unavailable_product_ids')
            if diff_product_ids is None or unavailable_product_ids is None:
                create_product_id_session(request)
        else:
            create_today_product_id_session(request)
    diff_product_ids = request.session.get('diff_product_ids')
    diff_products = _get_products_by_product_ids(diff_product_ids)
    unavailable_product_ids = request.session.get('unavailable_product_ids')
    unavailable_products = _get_products_by_product_ids(unavailable_product_ids)
    return (diff_products, unavailable_products)

#get display products from a list of product ids
def _get_products_by_product_ids(ids):
    products = Product.objects.filter(id__in=ids)
    return _get_display_products_by_products(products)

#create session data for list of changed priced products
def create_today_product_id_session(request):
    request.session['updated_date'] = str(get_current_date())
    create_product_id_session(request)

#create session data for list of changed priced products by current date
#the session data will be refreshed every day
def create_product_id_session(request):
    product_list = _get_products_by_user(request.user.id)
    unavailable_product_ids = [x.id for x in product_list if x.available == False]
    diff_product_ids = [x.id for x in product_list if x.trend == "DESC" or x.trend == "ASC"]
    request.session['diff_product_ids'] = diff_product_ids
    request.session['unavailable_product_ids'] = unavailable_product_ids


def reset_session(request):
    del request.session['updated_date']
    del request.session['diff_product_ids']
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