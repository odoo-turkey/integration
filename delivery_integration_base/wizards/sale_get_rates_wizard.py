# Copyright 2022 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleGetRatesWizard(models.TransientModel):
    _name = 'sale.get.rates.wizard'
    _description = "Sale Get Rates Wizard"

    carrier_prices = fields.Many2many('delivery.carrier.lines', string='Prices')
    #
    #
    # journal_type = fields.Selection(
    #     selection=[
    #         ('purchase', 'Create Supplier Invoice'),
    #         ('sale', 'Create Customer Invoice')
    #     ],
    #     default=_get_journal_type,
    #     readonly=True,
    # )
    # group = fields.Selection(
    #     selection=[
    #         ('picking', 'Picking'),
    #         ('partner', 'Partner'),
    #         ('partner_product', 'Partner/Product'),
    #     ],
    #     default="partner",
    #     help="Group pickings/moves to create invoice(s):\n"
    #          "Picking: One invoice per picking;\n"
    #          "Partner: One invoice for each picking's partner;\n"
    #          "Partner/Product: One invoice per picking's partner and group "
    #          "product into a single invoice line.",
    #     required=True,
    # )
    # invoice_date = fields.Date()
    # sale_journal = fields.Many2one(
    #     comodel_name='account.journal',
    #     domain="[('type', '=', 'sale')]",
    #     default=lambda self: self._default_journal('sale'),
    #     ondelete="cascade",
    # )
    # purchase_journal = fields.Many2one(
    #     comodel_name='account.journal',
    #     domain="[('type', '=', 'purchase')]",
    #     default=lambda self: self._default_journal('purchase'),
    #     ondelete="cascade",
    # )
    # show_sale_journal = fields.Boolean()
    # show_purchase_journal = fields.Boolean()
    # connect_to_einvoice = fields.Boolean(string='Connect to e-invoice')
    # partner_id = fields.Many2one('res.partner', string='Partner', readonly=True)
    # supplier_invoice_id = fields.Many2one('account.invoice', string='Supplier Invoice')

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
        carrier_ids = carrier_obj.search([('delivery_type', 'not in', ['base_on_rule', 'fixed'])])
        for order in sale_order.filtered(lambda o: o.state in ('draft', 'sent') and len(o.order_line) > 0):
            for carrier in carrier_ids:
                if hasattr(carrier, '%s_get_rate' % carrier.delivery_type):
                    carrier_dict[carrier] = getattr(carrier, '%s_get_rate' % carrier.delivery_type)(order)

        return carrier_dict


class DeliveryCarrierLines(models.TransientModel):
    _name = 'delivery.carrier.lines'
    _description = 'Delivery Carrier Lines'

    carrier_id = fields.Many2one('delivery.carrier', string='Carrier')
    price = fields.Char(string='Price')
    order_id = fields.Many2one('sale.order', string='Sale Order')
    selected = fields.Boolean(string='Selected', default=False)
