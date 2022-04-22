# Copyright 2022 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ResUsers(models.Model):
    _inherit = "res.users"

    internal_number = fields.Char(
        string='Internal Number', copy=False,
        help="User's internal phone number.")

    _sql_constraints = [
        ('unique_internal_number', 'unique (internal_number, id)', 'Internal number must be unique per user!'),
    ]
