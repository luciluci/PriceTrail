
EVOMAG_AFFILIATE_STR = 'http://event.2performant.com/events/click?ad_type=quicklink&aff_code=b42f1f3d6&unique=d4f678b43&redirect_to='
CEL_AFFILIATE_URL = 'http://event.2performant.com/events/click?ad_type=quicklink&aff_code=b42f1f3d6&unique=468ff75f3&redirect_to='
GERMANOS_AFFILIATE_URL = 'http://event.2performant.com/events/click?ad_type=quicklink&aff_code=b42f1f3d6&unique=63ed62863&redirect_to='

class Affiliate:

    @staticmethod
    def createAffiliateURL(url, shop):
        if shop == 'evomag':
            return EVOMAG_AFFILIATE_STR + url
        elif shop == 'cel':
            return CEL_AFFILIATE_URL + url
        elif shop == 'germanos':
            return GERMANOS_AFFILIATE_URL + url
        else:
            return url