# Copyright 2022 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from odoo import _, fields, models
from odoo.exceptions import ValidationError
from .garanti_connector import GarantiConnector
from odoo.addons.payment import utils as payment_utils

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

    def _set_error(self, state_message):
        # Todo: finish this method
        res = super()._set_error(state_message)
        return res

    # === BUSINESS METHODS ===#

    def _get_specific_processing_values(self, processing_values):
        """Override of payment to return  Garanti-specific processing values.

        Note: self.ensure_one() from `_get_processing_values`

        :param dict processing_values: The generic processing values of the transaction
        :return: The dict of provider-specific processing values
        :rtype: dict
        """
        res = super()._get_specific_processing_values(processing_values)
        if self.provider_code != "garanti":
            return res

        return {
            "access_token": payment_utils.generate_access_token(
                processing_values["reference"],
                processing_values["amount"],
                processing_values["partner_id"],
            )
        }

    def _process_notification_data(self, notification_data):
        """Override of payment to process the transaction based on Garanti data.

        Note: self.ensure_one()

        :param dict notification_data: The notification data sent by the provider
        :return: None
        :raise: ValidationError if inconsistent data were received
        """
        super()._process_notification_data(notification_data)
        if self.provider_code != "garanti":
            return

        self.operation = "online_redirect"
        self.garanti_xid = notification_data.get("xid")
        md_status = notification_data.get("mdstatus")
        error_msg = notification_data.get("mderrormessage")
        if md_status != "1":
            _logger.warning(
                "the transaction with reference %s underwent an error." " reason: %s",
                self.reference,
                error_msg,
            )
            self._set_error(error_msg)
        else:
            connector = GarantiConnector(
                self.provider_id,
                self,
                self.amount,
                self.currency_id.id,
            )
            try:
                res = connector._garanti_payment_callback(notification_data)
                if res == "Approved":
                    self._set_done()
                else:
                    self._set_error(res)
            except Exception as e:
                _logger.warning(
                    "Garanti payment callback error: %s, data: %s",
                    (e, notification_data),
                    exc_info=True,
                )
                self._set_error(res)

    def _get_tx_from_notification_data(self, provider_code, notification_data):
        """Override of payment to find the transaction based on Garanti data.

        :param str provider_code: The code of the provider that handled the transaction
        :param dict notification_data: The notification data sent by the provider
        :return: The transaction if found
        :rtype: recordset of `payment.transaction`
        :raise: ValidationError if inconsistent data were received
        :raise: ValidationError if the data match no transaction
        """
        tx = super()._get_tx_from_notification_data(provider_code, notification_data)
        if provider_code != "garanti" or len(tx) == 1:
            return tx

        tx_code = notification_data.get("secure3dhash")
        if not tx_code:
            raise ValidationError(
                "Garanti: " + _("Received data with missing transaction code.")
            )

        tx_ref = notification_data.get("orderid")
        if not tx_ref:
            raise ValidationError("Garanti: " + _("Received data with missing ref."))

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
                "Garanti: "
                + _(
                    "No transaction found matching reference %s.",
                    tx_code,
                )
            )
        return tx
