from __future__ import unicode_literals

from django.shortcuts import render, redirect
from .forms import LoginForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
import json
from django.contrib.auth.decorators import login_required
from TailedProducts.models import Product, ProductPrice, UserToProduct, DisplayProduct, DisplayDatePriceProduct

from spiders import GiantSpiders
import httplib
from datetime import datetime

def home_page(request):

    render_page = 'base.html'
    form_data = {}
    form_data['form'] = LoginForm()
    return render(request, render_page, form_data)

def login_page(request):

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('base')

    form = LoginForm()
    render_page = 'login_err.html'
    return render(request, render_page, {'form': form})

def registration_page(request):

    form_data = {}
    form_data['form'] = LoginForm()

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        cpassword = request.POST['confirm-password']

        user = User.objects.create_user(username, email, password)
        user.save()

        auser = authenticate(username=username, password=password)
        login(request, auser)
        return redirect('base')

    return render(request, 'registration.html', form_data)

@login_required
def add_tail_view(request):
    form_data = {}
    form_data['form'] = LoginForm()

    if request.method == 'POST':
        product_name = request.POST['product_name']
        product_price = request.POST['product_price']
        product_url = request.POST['product_url']
        product_shop = request.POST['product_shop']

        #create module and add in DB
        prod = Product.objects.filter(name__exact=product_name)

        if prod.count() == 0:
            #Create new product in Product table
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
            #check if the current user is not already monitoring the product
            user_product = UserToProduct.objects.filter(product__exact=first_prod.id, user__exact=request.user.id)
            if user_product.count() == 0:
                # Create a new entry in UserToProduct table
                new_user_product = UserToProduct()
                new_user_product.product = first_prod
                new_user_product.user = request.user
                new_user_product.save()

        return redirect('add-tail-view')

    return render(request, 'add-tail.html', form_data)

def add_tail(request):
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

@login_required
def my_tails(request):
    user_products = UserToProduct.objects.filter(user__exact=request.user.id).values('product_id')
    products = Product.objects.filter(id__in=user_products)

    display_products = []
    idx = 1
    for product in products:
        prod = DisplayProduct()
        prod.name = product.name
        prod.url = product.url
        prod.shop = product.shop
        prod.id = product.id
        prod.idx = idx
        idx += 1
        display_products.append(prod)

        #TO DO: sort by time
        product_prices = ProductPrice.objects.filter(product_id__exact=product.id)
        if product_prices.count() > 1:
            last_price = product_prices[0].price
            for prod_price in product_prices:
                price = prod_price.price
                if last_price > price:
                    prod.trend = "DESC"
                elif last_price < price:
                    prod.trend = "ASC"
                else:
                    prod.trend = "EQ"
                prod.price = price
                last_price = price
        elif product_prices.count() == 1:
            prod.price = product_prices[0].price
        else:
            prod.price = -1
            prod.trend = "NO RECORD"

    return render(request, 'my-tails.html', {'data': display_products})

@login_required
def delete_tail(request, id):
    UserToProduct.objects.filter(product_id__exact=id, user_id__exact=request.user.id).delete()

    remaining_user_products = UserToProduct.objects.filter(product_id__exact=id)
    if remaining_user_products.count() == 0:
        ProductPrice.objects.filter(product_id__exact=id).delete()
        Product.objects.filter(id__exact=id).delete()
    return redirect('get-tail')

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

    return render(request, 'product-graph.html', {'data': dprod})