# Copyright 2022 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    carrier_barcode_type = fields.Selection(string='Barcode Type',
                                            selection=[
                                                ('pdf', 'PDF'),
                                                ('zpl', 'ZPL (Zebra)'),
                                            ], default='pdf', required=True)
