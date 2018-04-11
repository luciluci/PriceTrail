
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

