# Copyright 2022 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from odoo import _, fields, models, api
from odoo.exceptions import ValidationError
from .garanti_connector import GarantiConnector
from odoo.http import request

# from odoo.addons.payment import utils as payment_utils

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    garanti_secure3d_hash = fields.Char(
        string="Garanti Secure 3D Hash",
        help="The hash used to authenticate "
        "the transaction with Garanti "
        "Secure 3D",
        readonly=True,
        copy=False,
    )

    garanti_xid = fields.Char(string="Garanti XID", readonly=True, copy=False)

    @api.multi
    def _set_transaction_error(self, msg):
        """
        This method is used to override default error message with the modified one.
        :param msg:
        :return:
        """
        res = super(PaymentTransaction, self)._set_transaction_error(msg)
        error_txs = self.filtered(
            lambda t: t.acquirer_id.provider == "garanti" and t.state == "error"
        )
        if error_txs:
            error_message = (
                self.env["payment.provider.error"]
                .sudo()
                .search([("error_message", "=", msg)], limit=1)
            )
            if error_message and error_message.modified_error_message:
                for tx in error_txs:
                    tx.state_message = error_message.with_context(
                        lang=tx.partner_id.lang or "tr_TR"
                    ).modified_error_message
        return res

    def action_query_transaction(self):
        """
        This method is used to query a transaction.

        Firstly, we are checking exist any done transaction with the same reference.
        If there is any error on the query, we are setting the transaction to cancel.
        This means that the transaction probably is not created in the bank side.

        :return: True if the transaction is successfully queried and processed, False otherwise.
        """
        self.ensure_one()
        if self.acquirer_id.provider != "garanti":
            return False

        previous_done_tx = self.search(
            [
                ("reference", "=like", self.reference.split("-")[0] + "%"),
                ("state", "=", "done"),
                ("partner_id", "=", self.partner_id.id),
            ]
        )
        # If we find any done transaction, just set the current transaction
        # to done without creating a payment record
        if previous_done_tx:
            self._set_transaction_done()
            # Set is_processed to True, otherwise Odoo will try to process the transaction again
            self.is_processed = True
            return True

        connector = GarantiConnector(
            acquirer=self.acquirer_id,
            tx=self,
            amount=self.amount,
        )
        try:
            res = connector._garanti_query_transaction()
        except:
            self._set_transaction_cancel()
            return False

        # If the transaction is approved in the bank side, we set the transaction to done
        if res and isinstance(res, bool) and self.state not in ("done", "cancel"):
            self._set_transaction_done()
            self._post_process_after_done()
            return True
        else:
            self._set_transaction_error(res)
            return False

    def _garanti_form_get_tx_from_data(self, data):
        """Given a data dict coming from garanti, verify it and find the related
        transaction record."""
        tx_code = data.get("secure3dhash")
        if not tx_code:
            raise ValidationError(
                "Garanti: " + _("Received data with missing transaction code.")
            )

        tx_ref = data.get("orderid")
        if not tx_ref:
            raise ValidationError(_("Payment Error: Received data with missing ref."))

        tx = self.search(
            [
                ("garanti_secure3d_hash", "=", tx_code),
                ("state", "not in", ("done", "cancel", "error")),
            ],
            limit=1,
            order="id desc",
        )

        if not tx:
            raise ValidationError(
                _("Payment Error: No transaction found matching reference %s.")
                % tx_code
            )
        return tx

    def _garanti_form_validate(self, notification_data):
        """Override of payment to process the transaction based on Garanti data.

        Note: self.ensure_one()

        :param dict notification_data: The notification data sent by the provider
        :return: None
        :raise: ValidationError if inconsistent data were received
        """
        if self.acquirer_id.provider != "garanti":
            return self

        self.acquirer_id.log_xml(notification_data, "3ds_return")

        self.garanti_xid = notification_data.get("xid")
        md_status = notification_data.get("mdstatus")
        error_msg = notification_data.get("mderrormessage")
        if md_status != "1":
            self._set_transaction_error(error_msg)
        else:
            connector = GarantiConnector(
                acquirer=self.acquirer_id,
                tx=self,
                amount=self.amount,
            )
            try:
                res = connector._garanti_payment_callback(notification_data)
                if res == "Approved":
                    self._set_transaction_done()
                    self._post_process_after_done()
                else:
                    self._set_transaction_error(res)
            except Exception as e:
                self._set_transaction_error(_("Payment Error. Please contact us."))

        return self  # for the controller
