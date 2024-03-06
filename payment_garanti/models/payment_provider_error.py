# Copyright 2024 Ahmet Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import models, fields, api


class PaymentProviderError(models.Model):
    _name = "payment.provider.error"
    _description = "Payment Provider Error"

    error_code = fields.Char(string="Error Code", required=True)
    error_message = fields.Text(string="Error Message", required=True)
    modified_error_message = fields.Text("Modified Error Message", translate=True)

    @api.onchange("error_message")
    def _onchange_error_message(self):
        for error in self:
            error.modified_error_message = error.error_message
