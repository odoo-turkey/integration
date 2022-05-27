# Copyright 2022 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, api


class DeliveryPriceRule(models.Model):
    _inherit = 'delivery.price.rule'

    variable = fields.Selection(selection_add=[("deci", "Deci")])
    variable_factor = fields.Selection(selection_add=[("deci", "Deci")])
    deci_type = fields.Selection(string='Deci Type',
                                 selection=[
                                     (3000, 'Domestic (3000)'),
                                     (5000, 'Foreign (5000)'),
                                 ], default=3000, required=True)

    region_id = fields.Many2one('delivery.region', string='Region', required=True)

    @api.onchange('variable')
    def _onchange_variable(self):
        """
        Set `deci` as default value for `variable_factor`
        This field also could have {'readonly': [('variable', '=', 'deci')]}
        """
        if self.variable == 'deci':
            self.variable_factor = 'deci'
