from operator import itemgetter, attrgetter, methodcaller
# Sorts products and place in front products that have the price changed or are unavailable
# product_list is a list of DisplayProduct objects
def sort_products_by_importance(product_list):
    return sorted(product_list, key=attrgetter('available', 'trend'))
