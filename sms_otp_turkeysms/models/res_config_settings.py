# Copyright 2024 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    allow_sms_otp = fields.Boolean(
        string="Allow SMS OTP",
        config_parameter="sms_otp_turkeysms.allow_sms_otp",
    )

    turkeysms_api_key = fields.Char(
        string="OTP API Key",
        config_parameter="sms_otp_turkeysms.turkeysms_api_key",
    )
