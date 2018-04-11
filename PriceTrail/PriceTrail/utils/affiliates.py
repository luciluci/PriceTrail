
EVOMAG_AFFILIATE_STR = 'http://event.2performant.com/events/click?ad_type=quicklink&aff_code=b42f1f3d6&unique=d4f678b43&redirect_to='

class Affiliate:

    @staticmethod
    def createAffiliateURL(url, shop):
        if shop == 'evomag':
            return EVOMAG_AFFILIATE_STR + url
        else:
            return url