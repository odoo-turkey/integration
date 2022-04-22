# Copyright 2022 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging
import requests

_logger = logging.getLogger(__name__)
BULUTSANTRALIM_ENDPOINT = 'http://api.bulutsantralim.com'


class BulutsantralimConnector(models.Model):
    """
    Bulutsantralim server object, stores the API key and functions to communicate with the server
    """
    _name = "bulutsantralim.connector"
    _description = "Verimor Bulutsantralim Connector"

    name = fields.Char(string='Bulutsantralim Connector Name', required=True)
    active = fields.Boolean(string='Active', default=True)
    api_key = fields.Char(
        string='Verimor Bulutsantralim API Key', required=True)
    call_timeout = fields.Integer('Call Timout', default=30, help='Timeout for call in seconds,'
                                                                  ' must be between 10 and 60 seconds (default 30)')
    manual_answer = fields.Boolean('Manual Answer', help='If its value is true, it waits for the extension'
                                   ' to pick up the phone (Normally, the extension will'
                                   ' open automatically and the caller will be called).', default=False)

    _sql_constraints = [
        ('check_call_timeout', 'CHECK(call_timeout >= 10 AND call_timeout <= 60)',
         'Call timeout must be between 10 and 60.')
    ]

    @api.one
    def _start_call_verimor(self, number, caller):
        params = {
            'key': self.api_key,
            'extension': caller,
            'destination': number,
            'manual_answer': self.manual_answer,
            'timeout': self.call_timeout
        }
        r = requests.get('%s/originate' % BULUTSANTRALIM_ENDPOINT, params=params)
        if r.status_code != 200:
            if r.text == 'USER_BUSY':
                raise UserError(_('User is busy.'))
            elif r.text == 'CALL_REJECTED':
                raise UserError(_('Call rejected.'))
            elif r.text == 'NO_ANSWER':
                raise UserError(_('No answer.'))
            else:
                raise ValidationError(_('Bulutsantralim API: %s' % r.text))

        return True
