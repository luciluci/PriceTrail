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
#from .views import add_tail_view as add_tail_view
from .views import validate_product#, my_tails, display_product

#user related views
from .views import index_view, login_view, register_view, profile_view
#products related views
from .views import dashboard_view, delete_product, add_new_product

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),
    #url(r'^$', home_view, name='base'), //old
    #url(r'^login$', login_view, name='login'),
    #url(r'^registration/$', reg_view, name='registration'),
    #product pages:
    #url(r'^add-tail-view/$', add_tail_view, name='add-tail-view'),

    #url(r'^my-tails/$', my_tails, name='my-tails'),
    #url(r'^delete-tail/(?P<id>\d+)/', delete_tail, name='delete-tail'),
    #url(r'^poll-data/$', poll_data, name='poll-data'),
    #url(r'^display-product/(?P<id>\d+)/', display_product, name='display-product'),

    #Profile view
    #url(r'^profile/$', profile_view, name='profile'),

    #New template
    url(r'^$', index_view, name='index'),#this will became index
    url(r'^login/$', login_view, name='login'),
    url(r'^register/$', register_view, name='register'),
    url(r'^profile/$', profile_view, name='profile'),
    url(r'^dashboard/$', dashboard_view, name='dashboard'),
    url(r'^delete-product/(?P<id>\d+)/', delete_product, name='delete-product'),
    url(r'^add-new-product/$', add_new_product, name='add-new-product'),
    url(r'^validate-product/$', validate_product, name='validate-product'),
]
