import openerp.http as http
from openerp.http import request, SUPERUSER_ID
import logging
from datetime import datetime
_logger = logging.getLogger(__name__)

class MyController(http.Controller):

    @http.route('/sms/smsmasivos/receipt', type="http", auth="public")
    def sms_twilio_receipt(self, **kwargs):
        values = {}
	for field_name, field_value in kwargs.items():
            values[field_name] = field_value
        
        request.env['esms.smsmasivos'].sudo().delivary_receipt(values['ORIGEN'], values['TEXTO'],values['IDINTERNO']:)
        
        return "<Response></Response>"
        
