# Copyright 2024 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import models, api, fields
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

            # total_order_sum = sum(orders.mapped("amount_total"))
            # # Amounts are not equal, maybe false positive match
            # if not (total_order_sum * 0.99 <= res.amount <= total_order_sum * 1.01):
            #     return res

            if orders.amount_total != res.amount:
                return res

            # We can't create payment for multiple partners
            if len(orders.mapped("partner_id.commercial_partner_id")) > 1:
                return res

            commercial_partner = orders.mapped("partner_id").commercial_partner_id

            if res.amount < 0:
                credit = 0
                debit = abs(res.amount)
            else:
                credit = res.amount
                debit = 0

            # Only work on positive amounts
            if credit < 0:
                return res

            data = [
                {
                    "counterpart_aml_dicts": [],
                    "new_aml_dicts": [
                        {
                            "account_id": commercial_partner.property_account_receivable_id.id,
                            "analytic_tag_ids": [[6, None, []]],
                            "credit": credit,
                            "debit": debit,
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
