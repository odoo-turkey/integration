# Copyright 2022 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class SaleOrder(models.Model):
    _inherit = 'sale.order'



    def action_delivery_prices_window(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'manual_reconciliation_view',
        }
