"""PriceTrail URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from .views import validate_product, display_product

#user related views
from .views import index_view, login_view, register_view, profile_view
#products related views
from .views import my_products_view, delete_product, add_new_product, dashboard_view, test_email_notifications, edit_profile_view, product_details_view

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),

    # implemented views
    url(r'^$', index_view, name='index'),#this will became index
    url(r'^login/$', login_view, name='login'),
    url(r'^register/$', register_view, name='register'),
    url(r'^profile/$', profile_view, name='profile'),
    url(r'^my-products/$', my_products_view, name='my-products'),
    url(r'^delete-product/(?P<id>\d+)/', delete_product, name='delete-product'),
    url(r'^add-new-product/$', add_new_product, name='add-new-product'),
    url(r'^validate-product/$', validate_product, name='validate-product'),
    url(r'^dashboard/$', dashboard_view, name='dashboard'),
    url(r'^edit-profile/$', edit_profile_view, name='edit-profile'),

    #modal window
    url(r'^display-product/(?P<id>\d+)/', display_product, name='display-product'),
    url(r'^product-details/(?P<id>\d+)/', product_details_view, name='product-details'),

    #superuser endpoints
    url(r'^test/$', test_email_notifications, name='test-view'),
]
