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
from .views import home_page as home_view
from .views import login_page as login_view
from .views import registration_page as reg_view
from .views import add_tail_view as add_tail_view
from .views import add_tail, my_tails, delete_tail, display_product

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),
    url(r'^$', home_view, name='base'),
    url(r'^login$', login_view, name='login'),
    url(r'^registration/$', reg_view, name='registration'),
    #product pages:
    url(r'^add-tail-view/$', add_tail_view, name='add-tail-view'),
    url(r'^add-tail/$', add_tail, name='add-tail'),
    url(r'^get-tails/$', my_tails, name='get-tail'),
    url(r'^delete-tail/(?P<id>\d+)/', delete_tail, name='delete-tail'),
    #url(r'^poll-data/$', poll_data, name='poll-data'),
    url(r'^display-product/(?P<id>\d+)/', display_product, name='display-product'),

    url(r'^accounts/login/$', login_view, name='acc-login'),
]
