
EVOMAG_AFFILIATE_STR = 'http://event.2performant.com/events/click?ad_type=quicklink&aff_code=b42f1f3d6&unique=d4f678b43&redirect_to='
CEL_AFFILIATE_URL = 'http://event.2performant.com/events/click?ad_type=quicklink&aff_code=b42f1f3d6&unique=468ff75f3&redirect_to='
GERMANOS_AFFILIATE_URL = 'http://event.2performant.com/events/click?ad_type=quicklink&aff_code=b42f1f3d6&unique=63ed62863&redirect_to='
QUICKMOBILE_AFFILIATE_URL = 'http://event.2performant.com/events/click?ad_type=quicklink&aff_code=b42f1f3d6&unique=862654a7d&redirect_to='
ROMSTAL_AFFILIATE_URL = 'https://event.2performant.com/events/click?ad_type=quicklink&aff_code=b42f1f3d6&unique=7a69b8b71&redirect_to='
OTTER_AFFILIATE_URL = 'https://event.2performant.com/events/click?ad_type=quicklink&aff_code=b42f1f3d6&unique=7e537fc0d&redirect_to='
VEXIO_AFFILIATE_URL = 'https://event.2performant.com/events/click?ad_type=quicklink&aff_code=b42f1f3d6&unique=41389eaf0&redirect_to='

class Affiliate:

    @staticmethod
    def createAffiliateURL(url, shop):
        if shop == 'evomag':
            return EVOMAG_AFFILIATE_STR + url
        elif shop == 'germanos':
            return GERMANOS_AFFILIATE_URL + url
        elif shop == 'romstal':
            return ROMSTAL_AFFILIATE_URL + url
        elif shop == 'otter':
            return OTTER_AFFILIATE_URL + url
        elif shop == 'vexio':
            return VEXIO_AFFILIATE_URL + url
        else:
            return url