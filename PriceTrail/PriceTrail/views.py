from __future__ import unicode_literals

from .utils import general, affiliates
from .utils.general import get_str_from_html
from .email.client import EmailClient
from spiders.GiantSpiders import SpiderGenerator, Spider
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.shortcuts import render, redirect
from TailedProducts.models import Product, UserToProduct, ProductPrice, DisplayProduct, DisplayDatePriceProduct
from TailedProducts.helpers import filters

import json
import httplib

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
                                          'unavailable_products': unavailable_products,
                                          'total_monitored_products': len(total_monitored_products),
                                          'most_changed_product': max_var_product,
                                          'least_changed_product': min_var_product,
                                          'best_price_products': best_price_products
                                          })


def index_view_logged_in(request):

    (diff_products, unavailable_products, best_price_products) = filters.get_notification_products(request)
    total_monitored_products = filters.count_total_products_monitored_by_user(request.user.id)

    (min_var_product, max_var_product) = filters._get_product_with_highest_price_variation(request.user.id)

    return render(request, 'index.html', {'diff_products': diff_products,
                                          'unavailable_products': unavailable_products,
                                          'total_monitored_products': total_monitored_products,
                                          'most_changed_product': max_var_product,
                                          'least_changed_product': min_var_product,
                                          'best_price_products': best_price_products
                                           })


@login_required(login_url='/login')
def dashboard_view(request):

    (diff_products, unavailable_products, best_price_products) = filters.get_notification_products(request)
    total_monitored_products = filters.count_total_products_monitored_by_user(request.user.id)

    (min_var_product, max_var_product) = filters._get_product_with_highest_price_variation(request.user.id)

    return render(request, 'user/dashboard.html', {'diff_products': diff_products,
                                                   'unavailable_products': unavailable_products,
                                                   'total_monitored_products': total_monitored_products,
                                                   'most_changed_product': max_var_product,
                                                   'least_changed_product': min_var_product,
                                                   'best_price_products': best_price_products
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
    reset_session(request)
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
            EmailClient.say_hi(email, username)

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
                                                 'unavailable_products': unavailable_products,
                                                 'best_price_products': best_price_products
                                                 })


#endpoint "/my-products"
@login_required(login_url='/login')
def my_products_view(request):
    product_list = filters.get_display_products_by_user(request.user.id)
    new_products_list = filters.sort_products_by_importance(product_list)
    (diff_products, unavailable_products, best_price_products) = filters.get_notification_products(request)

    return render(request, 'products/my-products.html', {'products':new_products_list,
                                                         'diff_products': diff_products,
                                                         'unavailable_products': unavailable_products,
                                                         'best_price_products': best_price_products
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
    #return redirect('my-products')

import locale
#action used to add a product
@login_required(login_url='/login')
def add_new_product(request):

    if request.method == 'POST':
        d = json.loads(request.POST['json'])
        product_name = get_str_from_html(d['product_name'])
        trimmedPrice = d['product_price'].replace(',', '.')
        product_price = locale.atof(trimmedPrice)
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
            new_prod.best_price = product_price
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
                                                         'unavailable_products': unavailable_products,
                                                         'best_price_products': best_price_products
                                                         })


@login_required(login_url='/login')
def validate_product(request):
    if request.method == 'POST':
        d = json.loads(request.POST['json'])
        product_url = d['product-url']
    pdata = {}

    shop_name = Spider.get_shop_from_url(product_url)
    if not shop_name:
        pdata['status'] = 'invalid'
        pdata['message'] = '<b>Oh snap!</b> URL is invalid. Add a valid URL and try again'
        return HttpResponse(json.dumps(pdata), content_type='application/json')

    if shop_name not in data.SHOPS:
        pdata['status'] = 'invalid'
        pdata['message'] = '<b>Oh snap!</b> <u>' + shop_name + '</u> is not supported. Add a product from the supported shops'
        return HttpResponse(json.dumps(pdata), content_type='application/json')

    spider_gen = SpiderGenerator()
    spider = spider_gen.get_spider(shop_name)

    if httplib.OK == spider.parse_data(product_url):
        prod = spider.get_product()
        pdata['status'] = 'valid'
        pdata['pname'] = prod.name
        pdata['pprice'] = prod.price
        pdata['purl'] = product_url
        pdata['pshop'] = shop_name
    else:
        pdata['status'] = 'invalid'
        pdata['message'] = '<b>Oh snap!</b> Data is invalid. The page did not respond accordingly'

    return HttpResponse(json.dumps(pdata), content_type='application/json')

@login_required(login_url='/login')
def edit_profile_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        current_user = request.user
        current_user.first_name = first_name
        current_user.last_name = last_name
        current_user.email = email
        current_user.save()
    return profile_view(request)


#iframe to be displayed in a modal window
def display_product(request, id):
    product = Product.objects.get(id=id)
    dprod = DisplayProduct()
    dprod.name = product.name
    dprod.shop = product.shop
    dprod.url = product.url
    dprod.price = 20
    dprod.aff_url = affiliates.Affiliate.createAffiliateURL(dprod.url, dprod.shop)

    dates_prices =  ProductPrice.objects.filter(product_id__exact=product.id)
    for item in dates_prices:
        p = DisplayDatePriceProduct(item.date, item.price)
        dprod.date_prices.append(p)

    return render(request, 'products/product-modal.html', {'data': dprod})

#iframe to be displayed in a modal window
def product_details_view(request, id):
    product = Product.objects.get(id=id)
    displ_prod = filters.get_display_product_by_product(product)

    product_list = filters.get_display_products_by_user(request.user.id)
    new_products_list = filters.sort_products_by_importance(product_list)
    (diff_products, unavailable_products, best_price_products) = filters.get_notification_products(request)

    return render(request, 'products/product-details.html', {'products': new_products_list,
                                                             'diff_products': diff_products,
                                                             'unavailable_products': unavailable_products,
                                                             'best_price_products': best_price_products,
                                                             'data': displ_prod
                                                         })

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

from scheduler.management.commands.poll_data import Command
def test_update_prices(request):
    cmd = Command()
    cmd.handle()
    return HttpResponse(json.dumps(''), content_type='application/json')

def test_email_notifications(request):
    data = {}
    users = User.objects.all()
    for user in users:
        product_list = filters.get_best_display_products_by_user(user.id)
        data[user.username] = str(len(product_list)) + ' products'
        if len(product_list) == 0:
            continue

        if user.first_name or user.last_name:
            username = user.first_name + ' ' + user.last_name
        else:
            username = user.username
        if user.email:
            email_data = EmailClient.send_best_price_notification([user.email], product_list, username)
            data.update(email_data)
        else:
            data['warn'] = 'user ' + user.username + ' does not have an email'

    return HttpResponse(json.dumps(data), content_type='application/json')
