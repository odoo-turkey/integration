# Copyright 2022 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class WooMatchPaymentShipmentMethods(models.TransientModel):
    _name = 'woo.match.payment.shipment.methods'
    _description = "Woo match Payment Shipment Methods"

    woo_payment_method_ids = fields.Many2many('woo.payment.methods', string='WooCommerce Payment Methods')
    woo_delivery_carriers_ids = fields.Many2many('woo.delivery.carriers', string='WooCommerce Shipping Methods')

    def woo_get_payment_methods(self, connector):
        create_list = []
        resp = connector.get("payment_gateways")
        if resp.status_code == 200:
            woo_payment_methods = resp.json()
        else:
            raise UserError(_("Error: %s" % resp.text))
        for method in woo_payment_methods:
            vals = {
                'woo_payment_name': method['title'],
                'woo_payment_id': method['id'],
            }
            create_list.append(vals)

        created_lines = self.env['woo.payment.methods'].create(create_list)
        return [(6, 0, created_lines.ids)]

    def woo_get_delivery_carriers(self, connector):
        create_list = []
        resp = connector.get("shipping_methods")
        if resp.status_code == 200:
            woo_shipping_methods = resp.json()
        else:
            raise UserError(_("Error: %s" % resp.text))
        for method in woo_shipping_methods:
            vals = {
                'woo_carrier_name': method['title'],
                'woo_carrier_id': method['id'],
            }
            create_list.append(vals)

        created_lines = self.env['woo.delivery.carriers'].create(create_list)
        return [(6, 0, created_lines.ids)]

    @api.model
    def default_get(self, fields_list):
        result = super(WooMatchPaymentShipmentMethods, self).default_get(fields_list)
        woo_backend = self.env['woocommerce.backend'].browse(self.env.context.get('active_id'))
        connector = woo_backend._build_api()

        result.update({'woo_payment_method_ids': self.woo_get_payment_methods(connector),
                       'woo_delivery_carriers_ids': self.woo_get_delivery_carriers(connector)})
        return result

    @api.model
    def write(self, vals):
        """
        This method is tricky. We can't override write due to the fact that
        the wizard is not a real model. So we override the default write
        method and call matching methods
        :param vals: list
        :return: bool
        """
        model = self.browse(vals[0])

        for payment_method in model.woo_payment_method_ids.filtered(lambda x: x.payment_id):
            payment_method.payment_id.write({'woocommerce_id': payment_method.woo_payment_id})

        for carrier in model.woo_delivery_carriers_ids.filtered(lambda x: x.carrier_id):
            carrier.carrier_id.write({'woocommerce_id': carrier.woo_carrier_id})

        return True


class WooDeliveryCarriers(models.TransientModel):
    _name = 'woo.delivery.carriers'
    _description = 'WooCommerce Delivery Carriers'

    batch_unique_hash = fields.Char('Batch Unique Hash')
    carrier_id = fields.Many2one('delivery.carrier', string='Carrier')
    woo_carrier_name = fields.Char('WooCommerce Carrier Name', readonly=True)
    woo_carrier_id = fields.Char('WooCommerce Carrier ID', readonly=True)


class WooPaymentMethods(models.TransientModel):
    _name = 'woo.payment.methods'
    _description = 'WooCommerce Payment Methods'

    batch_unique_hash = fields.Char('Batch Unique Hash')
    payment_id = fields.Many2one('payment.acquirer', string='Payment Acquirer')
    woo_payment_name = fields.Char('WooCommerce Payment Method Name', readonly=True)
    woo_payment_id = fields.Char('WooCommerce Payment Method ID', readonly=True)
