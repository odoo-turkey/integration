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
            return

        self.garanti_xid = notification_data.get("xid")
        md_status = notification_data.get("mdstatus")
        error_msg = notification_data.get("mderrormessage")
        if md_status != "1":
            _logger.warning(
                "Transaction %s is not authorized: %s", self.reference, error_msg
            )
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
                _logger.warning(
                    "Garanti payment callback error: %s, data: %s",
                    (e, notification_data),
                    exc_info=True,
                )
                self._set_transaction_error(e)

        return self  # for the controller
