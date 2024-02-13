# Copyright 2024 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import models, api, fields
from odoo.tools import float_compare
import re


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    order_ids = fields.Many2many(
        "sale.order",
        "sale_order_bank_statement_line_rel",
        "statement_line_id",
        "order_id",
        string="Sale Orders",
    )

    @api.model
    def create(self, vals):
        """
        Inherited to automatically bind orders to statement line
        :param vals:
        :return:
        """
        res = super(AccountBankStatementLine, self).create(vals)
        order_ref_pattern = r"\b[A-Za-z]{2}\d{6,7}\b"
        matched_refs = re.findall(order_ref_pattern, res.name)
        if matched_refs:
            # Todo: this method could be multi as well
            orders = self.env["sale.order"].search(
                [
                    ("name", "in", matched_refs),
                    ("state", "in", ["draft", "sent"]),
                ]
            )
            if len(orders) != 1:
                return res

            if float_compare(orders.amount_total, res.amount, 2) != 0:
                return res

            commercial_partner = orders.mapped("partner_id.commercial_partner_id")

            # We can't create payment for multiple partners
            if len(commercial_partner) > 1:
                return res

            # Only work on positive amounts
            if res.amount < 0:
                return res

            data = [
                {
                    "counterpart_aml_dicts": [],
                    "new_aml_dicts": [
                        {
                            "account_id": commercial_partner.property_account_receivable_id.id,
                            "analytic_tag_ids": [[6, None, []]],
                            "credit": res.amount,
                            "company_id": res.company_id.id,
                            # we are working with credit, so residual amount is negative
                            "amount_residual": -res.amount,
                            "debit": 0,
                            "name": res.name,
                        }
                    ],
                    "partner_id": commercial_partner.id,
                    "payment_aml_ids": [],
                }
            ]
            self.env["account.reconciliation.widget"].process_bank_statement_line(
                st_line_ids=[res.id], data=data
            )

            # Bind orders to statement line
            res.order_ids = [(6, 0, orders.ids)]

            payment_id = res.mapped("journal_entry_ids.payment_id")
            if payment_id:
                # Bind the payment to orders and Confirm orders
                for order in orders:
                    order.write(
                        {
                            "payment_status": "done",
                            "payment_ids": [(6, 0, payment_id.ids)],
                            "payment_term_id": 23,  # Banka havalesi
                        },
                    )
                    order.with_context(bypass_risk=True).action_confirm()
        return res
