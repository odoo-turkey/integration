# Copyright 2023 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
from datetime import timedelta, datetime


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    carrier_barcode_type = fields.Selection(
        string="Barcode Type",
        selection=[
            ("pdf", "PDF"),
            ("zpl", "ZPL (Zebra)"),
        ],
        default="pdf",
        required=True,
    )
    payment_type = fields.Selection(
        string="Payment Type",
        selection=[("customer_pays", "Customer Pays"), ("sender_pays", "Sender Pays")],
        default="sender_pays",
        required=True,
    )
    default_printer_id = fields.Many2one("printing.printer", string="Default Printer")
    attach_barcode = fields.Boolean(
        string="Attach Barcode to Picking",
        default=False,
        help="If checked, barcode will be attached to picking as a file.",
    )
    currency_id = fields.Many2one("res.currency", string="Currency", required=True)
    ref_sequence_id = fields.Many2one("ir.sequence", string="Reference Sequence")
    send_sms_customer = fields.Boolean(string="Send SMS to Customer", default=False)
    url_shortener_id = fields.Many2one("short.url.yourls", string="URL Shortener")
    sms_service_id = fields.Many2one("iap.account", string="SMS Service")

    barcode_text_1 = fields.Char(
        string="Barcode Text 1",
        help="Some static text for this carrier to package labels.",
    )
    deci_type = fields.Selection(
        string="Deci Type",
        selection=[
            ("3000", "(3000)"),
            ("4000", "(4000)"),
            ("5000", "(5000)"),
        ],
        default="3000",
        required=True,
    )
    weight_calc_percentage = fields.Float(
        string="additional percentage for weight calculation"
    )
    show_in_price_table = fields.Boolean(
        string="Show in Price Table",
        help="Show this carrier in Sale Order Shipment " "Price table",
    )
    fuel_surcharge_percentage = fields.Float(
        string="Fuel Surcharge Percentage",
        help="Additional Price to add after calculation of tables",
    )
    environment_fee_per_kg = fields.Float(
        string="Environment Charge per Kg",
        help="Environment fee per KG added after fuel surcharge",
    )
    postal_charge_percentage = fields.Float(
        string="Postal Charge Percentage",
        help="For shipments below 30kg or Deci additional percentage to add",
    )
    Emergency_fee_per_kg = fields.Float(
        string="Emergency Charge Per Kg",
        help="Emergency fee added after postal chargee percentage",
    )

    tracking_url_prefix_no_integration = fields.Char(
        string="Tracking URL Prefix",
        help="Tracking URL prefix for carrier that has no integration.",
    )

    delivery_deadline_no_integration = fields.Integer(
        string="Delivery Deadline (In Days)",
        default=3,
        required=True,
        help="Delivery deadline for carrier that has no integration.",
    )

    def _filter_rules_by_region(self, order):
        """
        Filter rules by defined region
        :param order: sale order
        :return: delivery.price.rule recordset
        """
        rules = self.price_rule_ids.filtered(
            lambda r: order.partner_shipping_id.state_id in r.region_id.state_ids
            or order.partner_shipping_id.country_id in r.region_id.country_ids
        )
        return rules

    def _get_ref_number(self):
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
            raise ValidationError(_("No Reference Sequence defined for this carrier"))

    def _update_all_picking_status(self):
        """
        Update integrated pickings in a batch
        :return:
        """
        # Todo: implement this method
        return True
        # pickings = self.env["stock.picking"].search(
        #     [
        #         (
        #             "carrier_id.delivery_type",
        #             "not in",
        #             [False, "fixed", "base_on_rule"],
        #         ),
        #         ("carrier_tracking_ref", "!=", False),
        #         ("date_done", ">", fields.Date.today() - timedelta(days=5)),
        #         (
        #             "delivery_state",
        #             "in",
        #             ["shipping_recorded_in_carrier", "in_transit"],
        #         ),
        #     ]
        # )
        #
        # for picking in pickings:
        #     method = "%s_tracking_state_update" % picking.delivery_type
        #     if hasattr(picking.carrier_id, method):
        #         getattr(picking.carrier_id, method)(picking)

    def _sms_notificaton_send(self, picking):
        """
        Send SMS notification to customer
        :param order: sale order
        :return:
        """
        sms_api = self.env["sms.api"]
        mobile_number = self.env["sms.send_sms"]._sms_sanitization(
            picking.partner_id, "mobile"
        )
        if mobile_number:
            sms_template = self.env.ref(
                "delivery_{0}.{0}_sms_template".format(self.delivery_type)
            )
            message = sms_template._render_template(
                sms_template.body_html, sms_template.model, picking.id
            )
            if message and self.sms_service_id:
                sms_api._send_sms([mobile_number], message)
        return True

    def get_tracking_link(self, picking):
        """Ask the tracking link to the service provider
        :param picking: record of stock.picking
        :return str: an URL containing the tracking link or False
        """
        res = super(DeliveryCarrier, self).get_tracking_link(picking)
        shortener = self.url_shortener_id

        if not res and picking.carrier_id.tracking_url_prefix_no_integration:
            res = (
                picking.carrier_id.tracking_url_prefix_no_integration
                + picking.shipping_number
            )

        if res and shortener:
            url = shortener.shortened_urls.search(
                [("long_url", "=", res), ("id", "in", shortener.shortened_urls.ids)],
                limit=1,
            ).short_url
            if not url:
                url = shortener.shorten_url(res)
            return url
        return res

    def _get_price_available(self, order):
        self.ensure_one()

        if isinstance(order, int):
            order = self.env["sale.order"].browse(order)

        dp = 4  # decimal precision
        res = order.order_line._compute_line_deci(int(self.deci_type))
        factor = (100.0 + self.weight_calc_percentage) / 100.0
        deci = res["deci"] * factor
        weight = res["weight"] * factor
        volume = res["volume"] * factor
        # save deci in sale order
        order.sale_deci = sum(order.mapped("order_line.deci"))
        total = (order.amount_total or 0.0) - res["total_delivery"]
        total = order.currency_id._convert(
            total,
            self.currency_id,
            order.company_id,
            order.date_order or fields.Date.today(),
        )

        price = self._get_price_from_picking(
            total, weight, volume, res["quantity"], deci, order
        )
        if not float_is_zero(self.fuel_surcharge_percentage, dp):
            price = price * (self.fuel_surcharge_percentage + 100.0) / 100.0

        if not float_is_zero(self.environment_fee_per_kg, dp):
            price = price + deci * self.environment_fee_per_kg

        if not float_is_zero(self.postal_charge_percentage, dp) and deci < 30.0:
            price = price * (self.postal_charge_percentage + 100.0) / 100.0

        if not float_is_zero(self.Emergency_fee_per_kg, dp):
            price = price + deci * self.Emergency_fee_per_kg

        if order.company_id.currency_id.id != self.currency_id.id:
            price = self.currency_id._convert(
                price,
                order.company_id.currency_id,
                order.company_id,
                order.date_order or fields.Date.today(),
            )
        return price

    def _get_price_from_picking(self, total, weight, volume, quantity, deci, order):
        price = 0.0
        criteria_found = False
        price_dict = {
            "price": total,
            "volume": volume,
            "weight": weight,
            "wv": volume * weight,
            "quantity": quantity,
            "deci": deci,
        }
        for line in self._filter_rules_by_region(order):
            test = safe_eval(
                line.variable + line.operator + str(line.max_value), price_dict
            )
            if test:
                price = (
                    line.list_base_price
                    + line.list_price * price_dict[line.variable_factor]
                )
                criteria_found = True
                break
        if not criteria_found:
            raise UserError(
                _(
                    "No price rule matching this order; delivery cost cannot be computed."
                )
            )

        return price

    def _cron_update_delivery_state_no_integration(self):
        """
        Cron to update delivery state for all pickings that have no integration
        :return:
        """
        today = datetime.now()
        pickings = self.env["stock.picking"].search(
            [
                ("invoice_state", "=", "invoiced"),
                ("state", "=", "done"),
                ("date_done", "!=", False),
                ("picking_type_code", "=", "outgoing"),
                "|",
                ("delivery_state", "=", False),
                ("delivery_state", "!=", "customer_delivered"),
            ]
        )
        for picking in pickings:
            deadline = picking.date_done + timedelta(
                days=picking.carrier_id.delivery_deadline_no_integration
            )
            if today > deadline:
                picking.delivery_state = "customer_delivered"

        return True
