# Copyright 2024 Ahmet Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import models, api, fields, _
from odoo.exceptions import UserError
from odoo.addons.phone_validation.tools import phone_validation
from datetime import datetime, timedelta
import requests
import logging

_logger = logging.getLogger(__name__)
_SERVICE_URL = "https://turkeysms.com.tr/api/v3/otp/otp_get.php"


class OTPRequest(models.TransientModel):
    _name = "otp.request"
    _description = "OTP Request Transient Model"

    user_id = fields.Many2one(
        comodel_name="res.users",
        string="User",
    )
    user_lang = fields.Char(
        string="User Language",
    )
    one_time_password = fields.Integer(
        string="One Time Password",
    )
    mobile_number = fields.Char(
        string="Mobile Number",
        required=True,
    )
    expiry_date = fields.Datetime(
        string="Expiry Date",
        default=lambda self: datetime.now() + timedelta(minutes=15),
        help="OTP will expire after this date."
        " It's set to 15 minutes from now by default.",
    )

    def send_otp(self):
        """Send OTP to the user's mobile number."""
        self.ensure_one()
        # Todo verify mobile number
        api_key = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("sms_otp_turkeysms.turkeysms_api_key")
        )
        if not api_key:
            return False
            # raise UserError(_("Please enter your TurkeySMS API key in the settings."))
        try:
            number_valid = phone_validation.phone_parse(self.mobile_number, "TR")
            if not number_valid:
                return False
        except:  # This means phone number is not valid
            return False

        try:
            response = requests.get(
                _SERVICE_URL,
                params={
                    "api_key": api_key,
                    "mobile": self.mobile_number,
                    # "lang": 0,  # English, only this one is suppsorted for now
                    "response_type": "json",  # json or php array
                },
            )
            response.raise_for_status()
            response_json = response.json()
            if response_json["result"]:  # Returns True if successful
                self.one_time_password = response_json["otp_code"]
                return True
        except Exception as e:
            _logger.error(e)
            return False
