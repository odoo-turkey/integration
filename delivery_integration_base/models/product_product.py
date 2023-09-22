# Copyright 2023 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import models, api, _
from odoo.tools import float_is_zero


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _calculate_product_deci(self, deci_type, uom_id, qty):
        # volume in litre, weight in Kg
        uom_kg = self.env.ref("uom.product_uom_kgm")
        product = self
        line_qty = uom_id._compute_quantity(
            qty=qty, to_unit=product.uom_id, round=False
        )
        line_kg = product.weight_uom_id._compute_quantity(
            qty=line_qty * product.weight,
            to_unit=uom_kg,
            round=False,
        )
        line_litre = (line_qty * product.volume * 1000.0) / (
            product.dimensional_uom_id.factor**3
        )
        deci = (
            line_litre * 1000.0
        ) / deci_type  # save deci in sale order line
        calculated_deci = max(line_kg, deci)

        return calculated_deci, line_kg, line_litre, line_qty
