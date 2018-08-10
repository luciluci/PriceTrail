from TailedProducts.helpers import filters
from django.contrib.auth import authenticate, login
from PriceTrail.settings import logger

# Method used to extract from the POST request the next page trying to be accesed.
# POST sample: #'http://localhost:8006/login/?next=/dashboard/'
# if in the POST a 'next' is found then return the next accesed page, if not, return empty string
def get_redirect_url(request):
    if 'HTTP_REFERER' in request.environ:
        referer = request.environ['HTTP_REFERER']
        if 'next' in referer:
            next_page = referer.split("next=")
            next_page = next_page[1].replace('/', '')
            return next_page
        else:
            return ''
    else:
        return ''

def get_str_from_html(name):
    html_txt = {'&nbsp;': ' ',
                '&lt;': '<',
                '&gt;': '>',
                '&amp;': '&',
                '&quot;': '"',
                '&apos;': '\''}
    for token in html_txt:
        name = name.replace(token, html_txt[token])
    return name

#cookie string format:
# 'HTTP_COOKIE':'Phpstorm-1f9ffc81=792c7efe-b0d1-4a12-915f-19bc9a677ae0; sessionid=gln1k5pg80u5zt4xz6sqrl2tya79zy7u',
def get_cookie_id(http_cookie_val):
    temp_split = str.split(http_cookie_val, "=")
    if len(temp_split) < 3:
        if len(temp_split) == 2:
            return temp_split[1]
        return None
    temp_split = str.split(temp_split[1], ';')
    if len(temp_split) < 2:
        return None
    return temp_split[0]

def login_unidentified_user(request):
    cookie_id = get_cookie_id(request.META['HTTP_COOKIE'])
    username = request.META['USER']
    user = filters.get_unidentified_user_from_cookie(cookie_id, username)
    if not user:
        logger.error('could not authenticate user')
        return None
    login(request, user)
    return None
