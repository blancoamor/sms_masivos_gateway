from openerp import models, fields, api
import logging
_logger = logging.getLogger(__name__)
import requests
from datetime import datetime
import re

class esms_mass_sms_wizard(models.TransientModel):
    _name = 'esms.mass.sms.wizard'

    phone_list=fields.Text(string="phones",required=True)
    esms_mass_sms =  fields.Many2one(comodel_name='esms.mass.sms',required=True)

    @api.multi
    def by_phone(self):
        phones=[]
        phones= filter(None,[x.strip() for x in self.phone_list.split('\n')])
        if phones : 
            partner= self.env['res.partner'].search(['|',('phone' ,'in',phones),('mobile' ,'in',phones)])
            partner_ids = [x.id for x in partner]
            self.esms_mass_sms.write({'selected_records':[[6,0,partner_ids]]}) 
    @api.multi
    def by_dni(self):
        phones=[]

        phones= filter(None,[re.sub("[^0-9]", "",x) for x in self.phone_list.split('\n')])
        if phones : 
            partner = self.env['res.partner'].search([('document_number' ,'in',phones)])
            _logger.info("partner %r" ,partner)
            partner_ids = [x.id for x in partner]
            _logger.info("partner_ids %r" ,partner_ids)
            _logger.info("self.esms_mass_sms %r" ,self.esms_mass_sms)
            
            self.esms_mass_sms.write({'selected_records':[[4,partner_ids]]}) 
        

