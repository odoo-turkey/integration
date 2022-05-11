# Copyright 2022 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def carrier_get_label(self):
        """Call to the service provider API which should have the method
        defined in the model as:
            <my_provider>_carrier_get_label
        It can be triggered manually or by the cron."""
        for picking in self.filtered("carrier_id"):
            method = '%s_carrier_get_label' % picking.delivery_type
            if hasattr(picking.carrier_id, method):
                getattr(picking.carrier_id, method)(picking)

