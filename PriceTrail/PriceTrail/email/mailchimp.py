from PriceTrail.settings import MAILCHIMP_API_KEY
from .chimpy import chimpy
import md5
import httplib
import json
import datetime

from PriceTrail.settings import logger
from PriceTrail.email.chimpy.chimpy import ChimpyException
from PriceTrail.email.client import EmailFormatter


class ChimpyClient():

    def __init__(self):
        self.chimp = chimpy.Connection(MAILCHIMP_API_KEY)

    def ping(self):
        print self.chimp.ping()

    def _create_subscribe_email_list(self, username, user_email):
        list_id = self._create_email_list(username)
        if not list_id:
            return False
        sub_result = self._subscribe_email(user_email, list_id)
        if sub_result != httplib.OK:
            return False
        return list_id

    # def _create_list(self):
    def send_best_price_notification(self, to_email, products, username):

        list_id = self._get_list_id(username)
        if not list_id:
            list_id = self._create_subscribe_email_list(username, to_email)
            if not list_id:
                return False

        #test with extra email
        # sub_result = self._subscribe_email('lucian.apetre@gmail.com', list_id)
        campaign_result = self._create_campaign_with_content(list_id, products, username)
        if not campaign_result:
            return False

        # unsub_result = self._unsubscribe_email(to_email, list_id)
        # if unsub_result != httplib.OK:
        #     return False

        return True

    def _get_list_id(self, list_name):
        test_lists = [x for x in self.chimp.lists() if x['name'] == list_name]
        if len(test_lists):
            test_list = test_lists.pop()
        else:
            return None
        return test_list['id']

    def _create_email_list(self, listname='Shopping-List product alerts'):
        result = self.chimp.create_new_list(name=listname)
        if result.status_code != httplib.OK:
            logger.error("Error in _create_email_list, creating list failed with err: " + str(result.status_code))
            return result.status_code
        json_data = result.content.replace("'", r"\"")
        json_obj = json.loads(json_data)
        if "id" in json_obj:
            list_id = json_obj['id']
            return list_id
        else:
            logger.error("Error in _create_email_list getting list id failed")
            return None
        return None

    def _subscribe_email(self, to_email, list_id):
        result = self.chimp.list_subscribe(list_id, to_email, {'FIRST': 'unit'})
        if result.status_code != httplib.OK:
            logger.error("Error in _create_email_list, adding subscribers failed with err: " + str(result.status_code))
            return result.status_code
        return httplib.OK

    def _unsubscribe_email(self, email, list_id):
        result = self.chimp.list_unsubscribe(list_id, email)
        if result.status_code != httplib.OK:
            logger.error("Error in _create_email_list, unsubscribe failed with err: " + str(result.status_code))
            return result.status_code
        return httplib.OK

    def _create_campaign(self, list_id, settings):
        recipients = {'list_id': list_id}

        result = self.chimp.campaign_create(recipients, 'regular', settings)

        if result.status_code != httplib.OK:
            logger.error("Error in _create_campaign, creating campain failed with err: " + str(result.status_code))
            return None

        json_data = result.content.replace("'", r"\"")
        json_obj = json.loads(json_data)
        if "id" in json_obj:
            campaign_id = json_obj['id']
            return campaign_id
        else:
            logger.error("Error in _create_campaign getting campain id failed")
            return None

        return None

    def _create_campaign_with_content(self, list_id, products, username):
        # template = self.chimp.get_template_by_name('test1_imported')
        # if not template:
        #     return httplib.NO_CONTENT
        #
        # template_id = template['id']

        settings = {
            'subject_line': 'Some of the products you are interestied in dropped price!',
            'title': 'price notification' + str(list_id),
            'from_name': 'Shopping-list.ro announcement',
            'reply_to': 'lucian_apetre@yahoo.com',
            'inline_css': True
            #'template_id': template_id
        }

        campaign_id = self._create_campaign(list_id, settings)
        if not campaign_id:
            return httplib.NO_CONTENT

        # html = """ <html><body><h1>My tesvt newslettemnbjbjr</h1><p>Just testing</p>
        #               <a href="*|UNSUB|*">Unsubscribe</a>*|REWARDS|*</body>"""
        html = EmailFormatter.create_html_notification(products, username)
        result = self.chimp._set_campaign_html_content(campaign_id, html)
        if result.status_code != httplib.OK:
            logger.error("ERROR: Failed to add html content to campaign. err: ", str(result.status_code))
            return result.status_code

        result = self._schedule_campain_now(campaign_id)
        if result != httplib.OK:
           return result

        return httplib.OK


    def _create_campain_content(self, campain_id):
        html_template = """ <html><body><h1>My test newsletter</h1><p>Just testing</p>
                           <a href="http://www.shopping-list.ro">Unsubscribe</a></body>"""

        result = self.chimp.campaign_set_content(campain_id, html_template)
        if result.status_code != httplib.OK:
            logger.error("ERROR: Failed to add html content to campaign. err: ", str(result.status_code))
            return result.status_code
        return httplib.OK


    def _add_template_to_campaign(self, campaign_id, template_id, sections):
        result = self.chimp.campaign_set_template_content(campaign_id, template_id, sections=sections)
        if result.status_code != httplib.OK:
            logger.error("ERROR: Failed to add template to campaign. err: ", str(result.status_code))
            return result.status_code
        return httplib.OK


    def _send_campain_now(self, campaign_id):
        try:
            result = self.chimp.campaign_send_now(campaign_id)
            if result.status_code != httplib.OK:
                logger.error("ERROR: Failed to send campaign. err: ", str(result.status_code))
                return result.status_code
        except ChimpyException as e:
            logger.error("ERROR: ChimpyException: " + e.message)
        return httplib.OK


    def _schedule_campain_now(self, campaign_id):
        try:
            result = self.chimp.campaign_schedule(campaign_id, datetime.datetime.now())
            if result.status_code != httplib.OK:
                logger.error("ERROR: Failed to schedule campaign. err: ", str(result.status_code))
                return result.status_code
        except ChimpyException as e:
            logger.error("ERROR: ChimpyException: " + e.message)
        return httplib.OK
