# Copyright 2022 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp


class SaleGetRatesWizard(models.TransientModel):
    _name = "sale.get.rates.wizard"
    _description = "Sale Get Rates Wizard"

    carrier_prices = fields.Many2many("delivery.carrier.lines", string="Prices")
    sale_id = fields.Many2one("sale.order", string="Sale Order")

    @api.model
    def create(self, vals):
        """
        Inherit to add carrier prices to the wizard.
        :param vals: dict
        :return: recordset
        """
        res = super(SaleGetRatesWizard, self).create(vals)
        for wizard in res.filtered(lambda w: w.sale_id):
            carrier_prices = res.get_delivery_prices()
            create_list = []
            for carrier, result in carrier_prices.items():
                if result["success"]:
                    create_list.append(
                        {
                            "carrier_id": carrier.id,
                            "price": result["price"],
                            "order_id": wizard.sale_id.id,
                            "currency_id": result["currency_id"],
                        }
                    )
            created_items = self.env["delivery.carrier.lines"].create(create_list)
            wizard.carrier_prices = created_items
        return res

    def get_delivery_prices(self):
        """
        Get delivery prices from the integrated delivery carriers.
        """
        self.ensure_one()
        carrier_dict = {}
        carrier_obj = self.env["delivery.carrier"]
        carrier_ids = carrier_obj.search([("show_in_price_table", "=", True)])
        order = self.sale_id
        for carrier in carrier_ids:
            data = carrier.rate_shipment(order)

            if not data.get("currency_id"):
                # Actually they're planning to add currency code to the response.
                # It's not implemented yet. So we're adding it manually.
                data["currency_id"] = order.currency_id.id
            carrier_dict[carrier] = data
        return carrier_dict

    def action_confirm(self):
        """Action to add selected delivery carrier to sale order"""
        self.ensure_one()
        carrier_price = self.carrier_prices.filtered(lambda c: c.selected)
        if len(carrier_price) != 1:
            raise UserError(_("Please select one delivery carrier."))
        order = self.sale_id
        order.carrier_id = carrier_price.carrier_id
        order.delivery_rating_success = True
        order.delivery_price = carrier_price.price
        order.set_delivery_line()
        return {}


class DeliveryCarrierLines(models.TransientModel):
    _name = "delivery.carrier.lines"
    _description = "Delivery Carrier Lines"

    carrier_id = fields.Many2one("delivery.carrier", string="Carrier")
    currency_id = fields.Many2one("res.currency", string="Currency")
    price = fields.Monetary(
        string="Price",
        currency_field="currency_id",
        digits=dp.get_precision("Product Price"),
    )
    order_id = fields.Many2one("sale.order", string="Sale Order")
    selected = fields.Boolean(string="Selected", default=False)
