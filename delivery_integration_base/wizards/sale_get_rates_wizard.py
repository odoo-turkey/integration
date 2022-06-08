# Copyright 2022 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleGetRatesWizard(models.TransientModel):
    _name = 'sale.get.rates.wizard'
    _description = "Sale Get Rates Wizard"

    carrier_prices = fields.Many2many('delivery.carrier.lines', string='Prices')

    @api.model
    def default_get(self, fields_list):
        """
        Inherit to add default invoice_date
        :param fields_list: list of str
        :return: dict
        """
        result = super(SaleGetRatesWizard, self).default_get(fields_list)
        partner_id = False
        sale_order = self._load_sale_order()
        if sale_order:
            carrier_prices = self.get_delivery_prices(sale_order)
            create_list = []
            for carrier, price in carrier_prices.items():
                create_list.append({
                    'carrier_id': carrier.id,
                    'price': price,
                    'order_id': sale_order.id,
                })
            created_items = self.env['delivery.carrier.lines'].create(create_list)
            result['carrier_prices'] = [(6, 0, created_items.ids)]
        #
        # result.update({
        #     'invoice_date': fields.Date.today(),
        #     'partner_id': partner_id.id,
        # })
        return result

    @api.multi
    def _load_sale_order(self):
        """
        Load sale order from context
        :return: sale.order recordset
        """
        sale_obj = self.env['sale.order']
        active_ids = self.env.context.get('active_ids', [])
        sale = sale_obj.browse(active_ids)
        return sale

    def get_delivery_prices(self, sale_order):
        """
        Get delivery prices from the integrated delivery carriers.
        """
        sale_order.ensure_one()
        carrier_dict = {}
        carrier_obj = self.env['delivery.carrier']
        carrier_ids = carrier_obj.search([('show_in_price_table', '=', True)])
        for order in sale_order.filtered(lambda o: o.state in ('draft', 'sent') and len(o.order_line) > 0):
            for carrier in carrier_ids:
                carrier_dict[carrier] = carrier.rate_shipment(order)
        return carrier_dict


class DeliveryCarrierLines(models.TransientModel):
    _name = 'delivery.carrier.lines'
    _description = 'Delivery Carrier Lines'

    carrier_id = fields.Many2one('delivery.carrier', string='Carrier')
    price = fields.Char(string='Price')
    order_id = fields.Many2one('sale.order', string='Sale Order')
    selected = fields.Boolean(string='Selected', default=False)
