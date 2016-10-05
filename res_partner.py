from openerp import models, fields, api
import logging
_logger = logging.getLogger(__name__)
import requests
from datetime import datetime
import re

class res_partner_esms(models.Model):

    _inherit = "res.partner"

    # SMSmasivos no puede utilizar e164
    mobile_e164 = fields.Char(string="Mobile e164", store=False, compute='_partner_get_phone')

    @api.one
    def _partner_get_phone(self):

        if self.mobile:
            phone=self.clean_mobile(self.mobile)
            if phone : 
                self.mobile_e164 =  phone
                return 

        if self.phone :
            phone=self.clean_phone(self.phone)
            if phone : 
                self.mobile_e164 = phone 
                return 


    def clean_mobile(self,phone):
            
        mob=re.compile('(\+)*(54)*(9)*(0)*(299|291|11|294)*(15)*([4|5|6])([0-9][0-9][0-9][0-9][0-9][0-9])')
        mobiles=mob.findall(re.sub("\D", "",phone))

        for mobile in mobiles:
            if  mobile[6] != '' and len(mobile[7])==6:
                caracteristica = "299" if  mobile[4] == '' else  mobile[4]

                return str(caracteristica)  + str(mobile[6])+ str(mobile[7])
        return False

    def clean_phone(self,phone):
        
        mob=re.compile('(\+)*(54)*(9)*(0)*(299|291|11|294)*(15)*([4|5|6])([0-9][0-9][0-9][0-9][0-9][0-9])')
        mobiles=mob.findall(re.sub("\D", "",phone))

        for mobile in mobiles:
            if mobile[5] != '' and mobile[6] != '' and len(mobile[7])==6:
                caracteristica = "299" if  mobile[4] == '' else  mobile[4]

                return  str(caracteristica)  + str(mobile[6])+ str(mobile[7])
        return False
