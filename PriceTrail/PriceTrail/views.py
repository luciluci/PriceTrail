from __future__ import unicode_literals

from django.shortcuts import render, redirect

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from TailedProducts.models import Product, UserToProduct, ProductPrice, DisplayProduct, DisplayDatePriceProduct
from TailedProducts.helpers import filters
from .utils import general

import json
from spiders import GiantSpiders
import httplib
from django.contrib import messages

#endpoint "/"
def index_view(request):
    #reset_session(request)
    if request.user.is_authenticated():
        return index_view_logged_in(request)
    else:
        return index_view_logged_out(request)


def index_view_logged_out(request):
    reset_session(request)
    (diff_products, unavailable_products, best_price_products) = filters.get_notification_products(request, False)
    total_monitored_products = Product.objects.all()

    (min_var_product, max_var_product) = filters._get_product_with_highest_price_variation(-1, False)

    return render(request, 'index.html', {'diff_products': diff_products,
                                          'diff_count': len(diff_products),
                                          'unavailable_products': unavailable_products,
                                          'unavailable_count': len(unavailable_products),
                                          'total_monitored_products': len(total_monitored_products),
                                          'most_changed_product': max_var_product,
                                          'least_changed_product': min_var_product,
                                          'best_price_products': best_price_products,
                                          'count_best_price': len(best_price_products)
                                          })


def index_view_logged_in(request):

    (diff_products, unavailable_products, best_price_products) = filters.get_notification_products(request)
    total_monitored_products = filters.count_total_products_monitored_by_user(request.user.id)

    (min_var_product, max_var_product) = filters._get_product_with_highest_price_variation(request.user.id)

    return render(request, 'index.html', {'diff_products': diff_products,
                                          'diff_count': len(diff_products),
                                          'unavailable_products': unavailable_products,
                                          'unavailable_count': len(unavailable_products),
                                          'total_monitored_products': total_monitored_products,
                                          'most_changed_product': max_var_product,
                                          'least_changed_product': min_var_product,
                                          'best_price_products': best_price_products,
                                          'count_best_price': len(best_price_products)
                                           })


@login_required(login_url='/login')
def dashboard_view(request):

    (diff_products, unavailable_products, best_price_products) = filters.get_notification_products(request)
    total_monitored_products = filters.count_total_products_monitored_by_user(request.user.id)

    (min_var_product, max_var_product) = filters._get_product_with_highest_price_variation(request.user.id)

    return render(request, 'user/dashboard.html', {'diff_products': diff_products,
                                                   'diff_count': len(diff_products),
                                                   'unavailable_products': unavailable_products,
                                                   'unavailable_count': len(unavailable_products),
                                                   'total_monitored_products': total_monitored_products,
                                                   'most_changed_product': max_var_product,
                                                   'least_changed_product': min_var_product,
                                                   'best_price_products': best_price_products,
                                                   'count_best_price': len(best_price_products)
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
            page = general.get_redirect_url(request)
            if not page:
                return redirect('index')
            return redirect(page)
    if not request.user.is_authenticated():
        reset_session(request)

    return render(request, 'user/login.html', )


#endpoint "/register"
def register_view(request):

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        cpassword = request.POST['confirm-password']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']

        if password != cpassword:
            messages.error(request, "error! password is not the same!")
            return redirect('register')

        users = User.objects.filter(username__exact=username)

        if len(users) > 0:
            messages.error(request, "error! username already exists!")
            return redirect('register')
        else:
            user = User.objects.create_user(username, email, password)
            user.last_name = last_name
            user.first_name = first_name
            user.save()

        auser = authenticate(username=username, password=password)
        login(request, auser)
        return redirect('index')
    return render(request, 'user/register.html', )


#endpoint "/profile"
@login_required(login_url='/login')
def profile_view(request):
    product_list = filters.get_display_products_by_user(request.user.id)
    (diff_products, unavailable_products, best_price_products) = filters.get_notification_products(request)

    return render(request, 'user/profile.html', {'products':product_list,
                                                 'diff_products': diff_products,
                                                 'diff_count': len(diff_products),
                                                 'unavailable_products': unavailable_products,
                                                 'unavailable_count': len(unavailable_products),
                                                 'best_price_products': best_price_products,
                                                 'count_best_price': len(best_price_products)
                                                 })


#endpoint "/my-products"
@login_required(login_url='/login')
def my_products_view(request):
    product_list = filters.get_display_products_by_user(request.user.id)
    new_products_list = filters.sort_products_by_importance(product_list)
    (diff_products, unavailable_products, best_price_products) = filters.get_notification_products(request)

    return render(request, 'products/my-products.html', {'products':new_products_list,
                                                         'diff_products': diff_products,
                                                         'diff_count': len(diff_products),
                                                         'unavailable_products': unavailable_products,
                                                         'unavailable_count': len(unavailable_products),
                                                         'best_price_products': best_price_products,
                                                         'count_best_price': len(best_price_products)
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
    product_list = filters.get_display_products_by_user(request.user.id)
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
            new_prod.current_price = product_price
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

    (diff_products, unavailable_products, best_price_products) = filters.get_notification_products(request)
    return render(request, 'products/add-product.html', {'diff_products': diff_products,
                                                         'diff_count': len(diff_products),
                                                         'unavailable_products': unavailable_products,
                                                         'unavailable_count': len(unavailable_products),
                                                         'best_price_products': best_price_products,
                                                         'count_best_price': len(best_price_products)
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


#used for hardocoding the update prices operations.
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
                #new entry in ProductPrice table
                new_prod_price = ProductPrice()
                new_prod_price.price = price
                new_prod_price.product = product
                new_prod_price.save()
                #update current_proce in Product table
                _detect_best_price(product, price)
                print(prod.name + ' - OK')
            elif data.PRODUCT_UNAVAILABLE == response:
                print(product.name + ' - UNAVAILABLE')
                product.available = False
                product.save()
            else:
                print(product.name + ' - NOK')
        else:
            print('SHOP NOT SUPPORTED: ' + shop)

#detects best price and flags if best price found for later use
def _detect_best_price(product, live_price):
    product.current_price = live_price
    if product.best_price == 0:
        product.best_price = live_price
        product.has_best_price = False
    else:
        if float(live_price) < product.best_price:
            product.best_price = live_price
            product.has_best_price = True
        else:
            product.has_best_price = False

    product.save()