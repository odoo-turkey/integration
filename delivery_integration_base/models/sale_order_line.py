# Copyright 2023 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from odoo.tools import float_is_zero
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    deci = fields.Float(
        string="Deci",
        digits=dp.get_precision("Product Unit of Measure"),
    )

    @api.multi
    def _compute_line_deci(self, deci_type):
        uom_kg = self.env.ref("uom.product_uom_kgm")
        uom_dp = 4
        # volume in litre, weight in Kg
        total = weight = volume = quantity = deci = 0.0
        total_delivery = 0.0
        for line in self:
            product = line.product_id
            if line.state == "cancel":
                continue
            if line.is_delivery:
                total_delivery += line.price_total
            if not product or line.is_delivery:
                continue

            if product.type == "product" and (float_is_zero(product.weight, uom_dp)
                                              or float_is_zero(product.volume, uom_dp)):
                raise ValidationError(
                    _(
                        "Cannot calculate Deci, Weight or Volume for product %s missing."
                    )
                    % (product.display_name)
                )

            line_qty = line.product_uom._compute_quantity(
                qty=line.product_uom_qty, to_unit=product.uom_id, round=False
            )
            line_kg = product.weight_uom_id._compute_quantity(
                qty=line_qty * product.weight,
                to_unit=uom_kg,
                round=False,
            )
            if line.product_id.volume_uom_id.uom_type =="smaller":
                line_litre = line_qty * line.product_id.volume * line.product_id.volume_uom_id.factor_inv
            elif line.product_id.volume_uom_id.uom_type =="bigger":
                line_litre = line_qty * line.product_id.volume * line.product_id.volume_uom_id.factor
            else:
                line_litre = line_qty * line.product_id.volume

            line.deci = (line_litre * 1000.0) / deci_type  # save deci in sale order line
            calculated_deci = max(line_kg, line.deci)
            deci += calculated_deci
            weight += line_kg
            volume += line_litre
            quantity += line_qty
        return {
            "deci": deci,
            "weight": weight,
            "volume": volume,
            "quantity": quantity,
            "total_delivery": total_delivery,
        }
