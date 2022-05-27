# Copyright 2022 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import ValidationError

class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    carrier_barcode_type = fields.Selection(string='Barcode Type',
                                            selection=[
                                                ('pdf', 'PDF'),
                                                ('zpl', 'ZPL (Zebra)'),
                                            ], default='pdf', required=True)

    payment_type = fields.Selection(string='Payment Type',
                                    selection=[('customer_pays', 'Customer Pays'), ('sender_pays', 'Sender Pays')],
                                    default='sender_pays', required=True)

    default_printer_id = fields.Many2one('printing.printer', string='Default Printer')

    attach_barcode = fields.Boolean(string='Attach Barcode to Picking', default=False,
                                    help='If checked, barcode will be attached to picking as a file.')

    currency_id = fields.Many2one('res.currency', string='Currency', required=True)

    ref_sequence_id = fields.Many2one('ir.sequence', string='Reference Sequence')

    def _calculate_deci(self, order):
        price = deci = weight = 0.0
        for line in order.order_line:
            product_id = line.product_id
            weight += line.product_id.weight * line.product_uom_qty
            deci += product_id.volume * line.product_uom_qty

        criteria_found = False
        for line in self._filter_rules_by_region(order):
            price_dict = {
                'deci': max((deci / line.deci_type), weight),
            }
            test = safe_eval(line.variable + line.operator + str(line.max_value), price_dict)
            if test:
                price = line.list_base_price + line.list_price * price_dict[line.variable_factor]
                suitable_rule = line
                criteria_found = True
                break
        if not criteria_found:
            return _("No matching price found.")

        if order.currency_id.id != self.currency_id.id:
            price = self.currency_id._convert(price, order.currency_id,
                                              order.company_id, fields.Date.today())

        return "%s%.2f" % (order.currency_id.symbol, price)

    def _filter_rules_by_region(self, order):
        """
        Filter rules by defined region
        :param order: sale order
        :return: delivery.price.rule recordset
        """
        rules = self.price_rule_ids.filtered(lambda r:
                                             order.partner_shipping_id.state_id in r.region_id.state_ids
                                             or
                                             order.partner_shipping_id.country_id in r.region_id.country_ids)
        return rules

    def get_ref_number(self):
        """
        Generate reference number based on sequence, if sequence is not defined,
        throw a ValidationError
        :return:
        """
        self.ensure_one()
        if self.ref_sequence_id:
            ref_no = self.ref_sequence_id.next_by_id()
            return ref_no
        else:
            raise ValidationError(_('No Reference Sequence defined for this carrier'))
