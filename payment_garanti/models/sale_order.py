# Copyright 2023 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import models, fields, api, _
from datetime import datetime


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # Do we need to store these values?
    garanti_payment_amount = fields.Monetary(
        string="Garanti Payment Amount",
        currency_field="garanti_payment_currency_id",
        compute="_compute_garanti_payment_amount",
        readonly=True,
    )
    garanti_payment_currency_id = fields.Many2one(
        string="Garanti Payment Currency",
        comodel_name="res.currency",
        compute="_compute_garanti_payment_amount",
        readonly=True,
    )
    # We've added this rate field because we want to get today's rate.
    garanti_payment_currency_rate = fields.Float(
        string="Garanti Currency Rate",
        compute="_compute_garanti_payment_amount",
        readonly=True,
    )

    def _compute_garanti_payment_amount(self):
        """
        This method is used to compute the garanti payment amount.
        If partner's country is Turkey, convert the amount into Turkish Lira.
        TODO: add AMEX support.
        :return:
        """
        country_turkey = self.env.ref("base.tr")
        currency_try = self.env.ref("base.TRY")
        for order in self:
            if order.partner_id.commercial_partner_id.country_id == country_turkey:
                amount = order.currency_id._convert(
                    order.amount_total,
                    currency_try,
                    order.company_id,
                    datetime.now(),
                )
                currency_id = currency_try
            else:
                amount = order.amount_total
                currency_id = order.currency_id
            order.garanti_payment_amount = amount
            order.garanti_payment_currency_id = currency_id
            try:
                order.garanti_payment_currency_rate = (
                    order.garanti_payment_amount / order.amount_total
                )
            except ZeroDivisionError:
                order.garanti_payment_currency_rate = 1.0
