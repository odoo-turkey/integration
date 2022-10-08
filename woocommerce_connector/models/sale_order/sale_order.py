# Copyright 2022 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models, api, _
from odoo.osv import expression
from .woo_sale_order import WooSaleOrder
from odoo.exceptions import UserError


# ONCHANGE_FIELDS = ['name',
#                    'parent_id',
#                    'manage_woo_stock']


class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = ["sale.order", "woocommerce.mapping"]

    # @api.multi
    # def create(self, vals):
    #     res = super(ProductTemplate, self).create(vals)
    #     for rec in res:
    #         if rec.sync_to_woocommerce and rec.woocommerce_backend_id:
    #             connector = WooProductTemplate(rec.woocommerce_backend_id)
    #             resp = connector.create(rec)
    #             rec.woocommerce_id = resp['id']
    #     return res
    #
    # @api.multi
    # def write(self, vals):
    #     res = super(ProductTemplate, self).write(vals)
    #     for rec in self:
    #         if rec.woocommerce_backend_id and rec.sync_to_woocommerce and rec.woocommerce_id:
    #             if any(x in vals for x in ONCHANGE_FIELDS):  # If category name or parent category changed
    #                 connector = WooProductTemplate(rec.woocommerce_backend_id)
    #                 connector.write(rec, vals)
    #     return res
    # Todo: sipariş cancel edince woo da da cancel yap
    @api.multi
    def _send_mail_woo(self):
        res = self.action_quotation_send()
        if res and res.get('context'):
            email_ctx = res['context']
            email_ctx.update(default_email_from=self.company_id.email)
            self.with_context(**email_ctx).message_post_with_template(email_ctx.get('default_template_id'))
        return True

    def _get_woo_partners(self, woo_partner_id, backend):
        ResPartner = self.env['res.partner']
        return ResPartner._search_woo_partner(woo_partner_id, backend)

    def _get_woo_carrier(self, shipping_lines):
        carrier = self.env['delivery.carrier'].search([('woocommerce_id', '=', shipping_lines[0].get('method_id'))],
                                                      limit=1)
        if not carrier:
            raise UserError(_('Carrier not found in Odoo. Please sync carriers first.'))
        return carrier.id

    def _get_woo_payment_method(self, payment_method):
        payment_method = self.env['payment.acquirer'].search([('woocommerce_id', '=', payment_method)], limit=1)
        if not payment_method:
            raise UserError(_('Payment method not found in Odoo. Please sync payment methods first.'))
        return payment_method.id

    def _prepare_woo_order_line(self, line_items):
        res = []
        for line in line_items:
            product = self.env['product.product'].search([('woocommerce_id', '=', line.get('variation_id'))], limit=1)

            if not product:
                raise UserError(_('Product not found in Odoo. Please sync products first.'))

            res.append((0, 0, {
                'product_id': product.id,
                'product_uom_qty': line.get('quantity', 1.0),
                'price_unit': line.get('price', 1.0),
                'name': line.get('name'),
                # Todo : Add taxes
            }))
        return res

    def _create_woo_orders(self, woo_orders, backend):
        for order in woo_orders:
            billing_address, shipping_address = self._get_woo_partners(order.get('customer_id'), backend)
            if not (billing_address or shipping_address):
                raise UserError(_('Partner not found in Odoo. Please sync customers first.'))
            vals = {
                'woocommerce_id': order.get('id'),
                'woocommerce_backend_id': backend.id or False,
                'sync_to_woocommerce': True,
                'pricelist_id': backend.sale_pricelist_id.id,
                'source_id': backend.sale_utm_source_id.id,
                'warehouse_id': backend.sale_warehouse_id.id,
                'note': order.get('customer_note'),
                'order_line': self._prepare_woo_order_line(order.get('line_items')),
                'date_order': order.get('date_created'),
                'partner_id': billing_address.id,
                'partner_invoice_id': billing_address.id,
                'partner_shipping_id': shipping_address.id,
                'carrier_id': self._get_woo_carrier(order.get('shipping_lines')),
                'acquirer_id': self._get_woo_payment_method(order.get('payment_method')),
            }
            order = self.create(vals)
            order.action_confirm()
            if backend.sale_mail_sending:
                order._send_mail_woo()
            self.env.cr.commit()

    def action_sync_from_woocommerce(self):
        woo_backend = self.env['res.company'].browse(1).default_woocommerce_backend_id  # TODO : Select backend
        connector = WooSaleOrder(woo_backend)
        woo_orders = connector.get_orders(woo_backend.last_sale_import_date)
        self._create_woo_orders(woo_orders, woo_backend)
        woo_backend.last_sale_import_date = fields.Datetime.now()
