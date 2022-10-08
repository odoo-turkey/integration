# Copyright 2022 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields


class PaymentAcquirer(models.Model):
    _inherit = "payment.acquirer"

    woocommerce_id = fields.Char('WooCommerce Payment Method ID', readonly=True)
