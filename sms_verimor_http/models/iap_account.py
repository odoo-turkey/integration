# Copyright 2022 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, _
from odoo.exceptions import Warning


class IapAccount(models.Model):
    _inherit = "iap.account"

    provider = fields.Selection(selection_add=[("sms_verimor_http", "SMS Verimor API")])
    sms_verimor_http_username = fields.Char(string="Username", required=True,
                                            help="Username of your Verimor account. (required)")
    sms_verimor_http_password = fields.Char(string="Password", required=True,
                                            help="Password of your Verimor account. (required)")
    sms_verimor_http_sms_header = fields.Char(string="SMS Header",
                                              help="Sender ID (Title). If source_addr is empty,"
                                                   " your first title registered in the system is used.")

    def _get_service_from_provider(self):
        if self.provider == "sms_verimor_http":
            return "sms"

    @api.one
    def get_verimor_sms_balance(self):

        if not self or not (self.sms_verimor_http_username and self.sms_verimor_http_password):
            raise Warning(_("You need to save your Verimor account first."))

        SmsAPI = self.env["sms.api"]
        balance = SmsAPI._get_balance_verimor_sms_api(account=self)
        raise Warning(balance)

    @property
    def _server_env_fields(self):
        res = super()._server_env_fields
        res.update(
            {
                "sms_verimor_http_username": {},
                "sms_verimor_http_password": {},
                "sms_verimor_http_sms_header": {},
            }
        )
        return res
