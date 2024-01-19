# Copyright 2024 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import models, api, fields, _
from uuid import uuid4


class ResUsers(models.Model):
    _inherit = "res.users"

    otp_management_token = fields.Char(
        string="OTP Management Token",
        store=True,
        compute="_compute_otp_management_token",
        help="Token used for OTP management.",
    )

    @api.depends("login_date")
    def _compute_otp_management_token(self):
        for record in self:
            record.otp_management_token = str(uuid4())
