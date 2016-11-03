from openerp import models, fields, api
import logging
_logger = logging.getLogger(__name__)
import requests
from datetime import datetime
from lxml import etree
from openerp.http import request
from openerp.osv import osv
import uuid

class sms_response():
     delivary_state = ""
     response_string = ""
     human_read_error = ""
     message_id = ""

class smsmasivos_core(models.Model):

    _name = "esms.smsmasivos"
    
    api_url = fields.Char(string='API URL')
    
    def send_message(self, sms_gateway_id, from_number, to_number, sms_content, my_model_name='', my_record_id=0, my_field_name=''):

        sms_account = self.env['esms.accounts'].search([('id','=',sms_gateway_id)])

        format_number = to_number
        if " " in format_number: format_number.replace(" ", "")
        if "+" in format_number: format_number = format_number.replace("+", "")
        
 
        # 'IDINTERNO': my_model_name + "("+ str(my_record_id) + ")",
        
        sms_uuid = uuid.uuid4().urn

        smsgateway_url = "http://servicio.smsmasivos.com.ar/enviar_sms.asp?api=1&usuario="+sms_account.smsmasivos_user+"&clave="+sms_account.smsmasivos_pass+"&tos="+to_number+"&texto=" + sms_content+'&IDINTERNO='+ sms_uuid[9:];


        response_string = requests.get(smsgateway_url)

        response_code = ""
        status_code = ""
        if "OK" in response_string.text:
            status_code = "successful"
            response_code = "SUCCESSFUL"
            human_read_error= ''
        else:
            human_read_error=response_string.text
            status_code = "failed"
            response_code = "FAILED DELIVERY"

        my_model = self.env['ir.model'].search([('model','=',my_model_name)])
        my_field = self.env['ir.model.fields'].search([('name','=',my_field_name)])

        #esms_history = self.env['esms.history'].create({'field_id':my_field[0].id, 'record_id': my_record_id,'model_id':my_model[0].id,'account_id':sms_account.id,'from_mobile':'','to_mobile':to_number,'sms_content':sms_content,'status_string':response_string.text, 'direction':'O','my_date':datetime.utcnow(), 'status_code':status_code})
        #_logger.info('No se creo el registro esms_history %r ' ,esms_history )
        #self.env['ir.model.data'].create({'module':'smsmasivos','name':sms_uuid[9:], 'res_id':esms_history.id,'model':'esms.history'})

        my_sms_response = sms_response()
        my_sms_response.response_string = response_string.text
        my_sms_response.response_code = response_code

        #my_sms_response.delivary_state = delivary_state
        my_sms_response.response_string = response_string.text
        my_sms_response.human_read_error = human_read_error
        my_sms_response.message_id = sms_uuid[9:]



        return my_sms_response




    def check_messages(self, account_id, message_id=""):
        sms_account = self.env['esms.accounts'].browse(account_id)
        payload={'usuario': sms_account.smsmasivos_user , 
                'clave':sms_account.smsmasivos_pass,
                'solonoleido':'False',
                'marcarcomoleidos':'False',
                'traeridinterno':'True',
                'origen':'',
                }
            
        response_string = requests.get("http://servicio.smsmasivos.com.ar/ws/SMSMasivosAPI.asmx/RecibirSMS?&usuario="+ sms_account.smsmasivos_user + '&clave='+sms_account.smsmasivos_pass +  '&solonoleidos='+'True&marcarcomoleidos=True&traeridinterno=True&origen=' )

       
        root = etree.fromstring(response_string.text.encode('utf-8'))

        for sms_message in root:
            self._add_message(sms_message, account_id)        

    def _add_message(self, sms_message, account_id):

        idinterno = sms_message.find('{http://servicio.smsmasivos.com.ar/ws/}idinterno').text
        my_message = self.env['esms.history'].search([('sms_gateway_message_id','=',idinterno)],limit=1)

        if len(my_message) > 0 and idinterno:
            target_model = my_message.model_id.model
            record_id = my_message.record_id
            model_id = my_message.model_id 
            field_id = my_message.field_id
             

        else : 
            #partner_id = self.env['res.partner'].search([('mobile_e164','=', sms_message.find('{http://servicio.smsmasivos.com.ar/ws/}numero').text)])
            partner_id = self.env['res.partner'].search([('mobile','=', sms_message.find('{http://servicio.smsmasivos.com.ar/ws/}numero').text)])
            if len(partner_id) > 0:
                record_id = partner_id[0].id
                target_model = "res.partner"
                target_field = "mobile"
    


            else:
                #If you can't find a partner with that mobile number then look for a lead with that number
                lead_id = self.env['crm.lead'].search([('phone','=', sms_message.find('{http://servicio.smsmasivos.com.ar/ws/}numero').text)])
                if len(lead_id) > 0:
                    record_id = lead_id[0].id
                    target_model = "crm.lead"
                    target_field = "mobile"
                else:
                    #can't find the record so create a new lead
                    target_model = "crm.lead"
                    target_field = "phone"
                    record_id = self.env['crm.lead'].create({'name': 'SMS','description': sms_message.find('{http://servicio.smsmasivos.com.ar/ws/}texto').text ,'phone':sms_message.find('{http://servicio.smsmasivos.com.ar/ws/}numero').text}).id
                    
            model_id = self.env['ir.model'].search([('model','=', target_model)])
            field_id = self.env['ir.model.fields'].search([('model_id.model','=',target_model), ('name','=', target_field)])

        smsmasivos_gateway_id = self.env['esms.gateways'].search([('gateway_model_name', '=', 'esms.smsmasivos')])
            
        self.env[target_model].search([('id','=', record_id)]).message_post(body=sms_message.find('{http://servicio.smsmasivos.com.ar/ws/}texto').text, subject="SMS Received")
        
        #Create the sms record in history
        #'to_mobile': sms_message.find('{http://servicio.smsmasivos.com.ar/ws/}To').text,
        history_id = self.env['esms.history'].create({
                                'account_id': account_id, 
                                'status_code': "RECEIVED", 
                                'gateway_id': smsmasivos_gateway_id[0].id, 
                                'from_mobile': sms_message.find('{http://servicio.smsmasivos.com.ar/ws/}numero').text,  
                                'sms_gateway_message_id': sms_message.find('{http://servicio.smsmasivos.com.ar/ws/}idsms').text, 'sms_content': sms_message.find('{http://servicio.smsmasivos.com.ar/ws/}texto').text, 'direction':'I', 
                                'my_date':sms_message.find('{http://servicio.smsmasivos.com.ar/ws/}fecha').text, 
                                'model_id':model_id.id, 
                                'record_id':record_id,
                                'field_id':field_id.id})
            
class smsmasivos_conf(models.Model):

    _inherit = "esms.accounts"

    smsmasivos_user = fields.Char(string='User')
    smsmasivos_pass = fields.Char(string='Pass')
    
