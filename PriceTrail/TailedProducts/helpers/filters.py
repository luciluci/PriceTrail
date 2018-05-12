from operator import itemgetter, attrgetter, methodcaller
from TailedProducts.models import Product, UserToProduct, ProductPrice, DisplayProduct, DisplayDatePriceProduct

from datetime import datetime
from PriceTrail.utils.affiliates import Affiliate

def get_current_date():
    now = datetime.now()
    return now.strftime("%Y-%m-%d")

MAX_DIFFERENT_ITEMS = 10
MAX_UNAVAILABLE_ITEMS = 5
MAX_BEST_ITEMS = 5

# Sorts products and place in front products that have the price changed or are unavailable
# product_list is a list of DisplayProduct objects
def sort_products_by_importance(product_list):
    return sorted(product_list, key=attrgetter('available', 'trend'))

def sort_products_by_shop_az(product_list):
    return sorted(product_list, key=attrgetter('shop'))

def sort_products_by_shop_za(product_list):
    return sorted(product_list, key=attrgetter('shop'), reverse=True)

def sort_products_by_products_az(product_list):
    return sorted(product_list, key=attrgetter('name'))

def sort_products_by_products_za(product_list):
    return sorted(product_list, key=attrgetter('name'), reverse=True)

def sort_products_by_price_az(product_list):
    return sorted(product_list, key=attrgetter('price'))

def sort_products_by_price_za(product_list):
    return sorted(product_list, key=attrgetter('price'), reverse=True)

def sort_products_by_status_az(product_list):
    return sorted(product_list, key=attrgetter('available', 'trend'))

def sort_products_by_status_za(product_list):
    return sorted(product_list, key=attrgetter('available', 'trend'), reverse=True)

def _get_product_with_highest_price_variation(user_id, by_user_id = True):
    if by_user_id == True:
        user_product_ids = UserToProduct.objects.filter(user__exact=user_id).values('product_id')
        products = Product.objects.filter(id__in=user_product_ids)
    else:
        products = Product.objects.all()

    products_variation = []
    for product in products:
        price_changes = 0
        days_monitored = 0
        yesterday_price = 0

        product_prices = ProductPrice.objects.filter(product_id__exact=product.id)
        for product_price in product_prices:
            today_price = product_price.price
            if yesterday_price != 0 and today_price != yesterday_price:
                price_changes += 1
            yesterday_price = today_price
            days_monitored += 1

        product_variation = {"id":product.id,
                             "name":product.name,
                             "days_monitored":days_monitored,
                             "price_changes": price_changes}
        #compute price per day variation vs the entire number of days monitored
        product_variation["total_variation"] = int((price_changes * 100)/ days_monitored)
        products_variation.append(product_variation)

    product_most_changed = None
    product_least_changed = None
    if len(products_variation):
        product_most_changed = max(products_variation, key=lambda x:x["total_variation"])
        product_least_changed = min(products_variation, key=lambda x: x["total_variation"])
    return (product_least_changed, product_most_changed)

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
        prod.aff_url = Affiliate.createAffiliateURL(prod.url, prod.shop)
        idx += 1
    return display_products

def get_display_product_by_product(product):
    prod = DisplayProduct()
    prod.name = product.name
    prod.url = product.url
    prod.shop = product.shop
    prod.id = product.id
    prod.available = product.available

    prod_dict = _compute_product_trend_price_percent(product.id)
    prod.trend = prod_dict["trend"]
    prod.price = prod_dict["price"]
    prod.percent = prod_dict["percent"]
    prod.aff_url = Affiliate.createAffiliateURL(prod.url, prod.shop)

    dates_prices = ProductPrice.objects.filter(product_id__exact=product.id)
    for item in dates_prices:
        p = DisplayDatePriceProduct(item.date, item.price)
        prod.date_prices.append(p)

    return prod

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

def _get_all_products():
    products = Product.objects.all()
    display_products = _get_display_products_by_products(products)
    return display_products

def get_display_products_by_user(user_id):
    #user_products = UserToProduct.objects.filter(user__exact=user_id).values('product_id')
    #products = Product.objects.filter(id__in=user_products)
    products = _get_products_by_user(user_id)
    display_products = _get_display_products_by_products(products)
    return display_products

def _get_products_by_user(user_id):
    user_products = UserToProduct.objects.filter(user__exact=user_id).values('product_id')
    return Product.objects.filter(id__in=user_products)

def _create_display_products_by_ids(ids):
    if len(ids) == 0:
        return []
    products = Product.objects.filter(id__in=ids)
    return _get_display_products_by_products(products)

def _create_product_id_session(request, by_user_id = True):
    product_list = []
    if by_user_id == True:
        product_list = get_display_products_by_user(request.user.id)
        best_list = get_ids_of_best_price_products(request.user.id)
    else:
        product_list = _get_all_products()
        best_list = get_ids_of_best_price_products()
    unavailable_product_ids = [x.id for x in product_list if x.available == False]
    diff_product_ids = [x.id for x in product_list if x.trend == "DESC" or x.trend == "ASC"]
    request.session['diff_product_ids'] = diff_product_ids[:MAX_DIFFERENT_ITEMS]
    request.session['unavailable_product_ids'] = unavailable_product_ids[:MAX_UNAVAILABLE_ITEMS]
    request.session['best_product_ids'] = best_list[:MAX_BEST_ITEMS]


def _create_today_product_id_session(request, by_user_id = True):
    request.session['updated_date'] = str(get_current_date())
    _create_product_id_session(request, by_user_id)


def get_notification_products(request, by_user_id = True):
    session_date = request.session.get('updated_date')
    if not session_date:
        _create_today_product_id_session(request, by_user_id)
    else:
        if request.session['updated_date'] == str(get_current_date()):
            diff_product_ids = request.session.get('diff_product_ids')
            unavailable_product_ids = request.session.get('unavailable_product_ids')
            best_products_ids = request.session.get('best_product_ids')
            if diff_product_ids is None or unavailable_product_ids is None or best_products_ids is None:
                _create_product_id_session(request, by_user_id)
        else:
            _create_today_product_id_session(request, by_user_id)
    diff_product_ids = request.session.get('diff_product_ids')
    diff_products = _create_display_products_by_ids(diff_product_ids)
    unavailable_product_ids = request.session.get('unavailable_product_ids')
    unavailable_products = _create_display_products_by_ids(unavailable_product_ids)
    best_products_ids = request.session.get('best_product_ids')
    best_products = _create_display_products_by_ids(best_products_ids)
    return (diff_products, unavailable_products, best_products)

def count_total_products_monitored_by_user(user_id):
    product = UserToProduct.objects.filter(user_id__exact=user_id)
    return product.count()

#return list of <product ids> with today's best_price
def get_ids_of_best_price_products(user_id = None):

    if user_id:
        products_all = _get_products_by_user(user_id)
    else:
        products_all = Product.objects.all()
    best_price_ids = [x.id for x in products_all if x.has_best_price == True]
    return best_price_ids

def get_best_display_products_by_user(user_id = None):
    best_prods_ids = get_ids_of_best_price_products(user_id)
    return _create_display_products_by_ids(best_prods_ids)