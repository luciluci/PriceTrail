TO DOs:


NEW:
1. most visited product
2. most expensive product visited
3. products from the most visited store

* product name should not have characters like '&amp;'
    they must be replaced
* split notification products from 'list display' products, since the most of the data is redundant
* in get_notification_products:
    if diff_product_ids is None or unavailable_product_ids is None or best_products_ids is None:
    can be splitted in 3 so if one of the values misses not to compute all 3
* for notification products:
    create link to 'my-products'
    instead of today display current price
    add 'buy now' button that will go to actual product
* add email notification system
* add "in stock"/"out of stock" search n page and display

/:
* in the 'logged in' version of index:
    * make a bit smaller the distance between the 2 sections
    * create a real values chart with values monitored by the user along the time.

* limit max number of monitored products to 50
* add images for monitored shops(in product list add emag logo for emag products)

* create product page with: image, graphic, delete action..
* register to emag profitshare

/my-products:
    * add GET attribute to /my-products for filtering the displayed products
    * add favorites products and sort the view by them

* add email notification system:
    * registration
    * best price on product
    * notify user by email when product price gets lowest/unavailable
* get entire floating point price

* add url to product title in pages so it can be accessed

* contact page
* password reset

*. Main page with:
    * last tails added
    * most tails added


* Capcha form for registration page
* notification system:
    * check products that you want to be notified of
    * every day the product data will appear on notifications

* rate product system, create favorites
* real time graph with number of monitored products

MAIN PAGE:
    * Add product tail page:
        * add product
        * view product in your product tails
        * receive notifications when it changes
        * receive notifications when the price drops
    *

Features:
* Money saved: will be the buy price - start price
1. Register/Login with Facebook
2. Add afiliates for emag:
    2.1. register as afiliate
    2.2. add this functionality
    2.3. investigate other afiliates..
3. Create browser add-on for the app


Functionalities used:
1. Dropdown login:
    https://bootsnipp.com/snippets/featured/fancy-navbar-login-sign-in-form
2. Cronjob
    https://ole.michelsen.dk/blog/schedule-jobs-with-crontab-on-mac-osx.html

Theme:

1. dashboard icons:
    http://www.taklom360.com/help-icons.html

Bug:
* if product not added in step 2, the next button will be unavailable.
it should become available after another product is added.

Windows venv installation:
1. run venv for Windows:
    $ venvWin/Scripts/activate
2. once in venv, install additional packages:
    $ pip install Django==1.11
    $ pip install django-cors-headers
    $ pip install lxml
    $ pip install requests
3. serve all static files
    $ python manage.py collectstatic