# Copyright 2022 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
import pprint
from odoo import _, http, fields
from odoo.exceptions import ValidationError
from odoo.addons.payment.controllers.portal import PaymentProcessing
from odoo.tools import float_compare
from odoo.http import request
from datetime import datetime


_logger = logging.getLogger(__name__)


class GarantiController(http.Controller):
    _payment_url = "/payment/garanti/s2s/create_json_3ds"
    _return_url = "/payment/garanti/return"

    @http.route(_payment_url, type="json", auth="public")
    def garanti_s2s_create_json_3ds(self, **kwargs):
        # !!! Printing the card data for debugging purposes is a security risk !!!
        # _logger.debug(
        #     "Garanti payment request received: s2s_create_json_3ds: kwargs=%s",
        #     pprint.pformat(kwargs),
        # )
        acq = (
            request.env["payment.acquirer"]
            .sudo()
            .browse(int(kwargs.get("acquirer_id")))
        )
        # Validate the card data
        card_args = dict()
        card_args["card_number"] = kwargs.get("cc_number")
        card_args["card_cvv"] = kwargs.get("cc_cvc")
        card_args["card_name"] = kwargs.get("cc_holder_name")
        card_args["card_valid_month"] = kwargs.get("cc_expiry")[0:2]
        card_args["card_valid_year"] = kwargs.get("cc_expiry")[5:]

        card_error = acq._garanti_validate_card_args(card_args)
        if card_error:
            raise ValidationError(card_error)

        # Get the order
        order_sudo = (
            request.env["sale.order"].sudo().browse(int(kwargs.get("order_id")))
        )
        if not order_sudo:
            raise ValidationError(_("Sale order not found"))

        # Validate the amount
        try:
            amount = float(kwargs.get("amount_total"))
        except (ValueError, TypeError):
            raise ValidationError(_("Invalid amount"))

        precision = request.env["decimal.precision"].precision_get("account")
        if float_compare(amount, order_sudo.garanti_payment_amount, precision) != 0:
            raise ValidationError(_("Invalid amount"))

        # Create the transaction
        tx_sudo = (
            request.env["payment.transaction"]
            .sudo()
            .create(
                {
                    "amount": order_sudo.garanti_payment_amount,
                    "acquirer_id": acq.id,
                    "reference": order_sudo.name,
                    "acquirer_reference": order_sudo.name,
                    "partner_id": order_sudo.partner_id.id,
                    "sale_order_ids": [(4, order_sudo.id, False)],
                    "currency_id": order_sudo.currency_id.id,
                    "date": datetime.now(),
                    "state": "draft",
                }
            )
        )

        # Get client IP
        client_ip = request.httprequest.environ.get("REMOTE_ADDR")

        # Get the payment response, it can be a redirect or a form
        try:
            response_content = acq.sudo()._garanti_make_payment_request(
                tx_sudo, amount, card_args, client_ip
            )
        except Exception as e:
            _logger.exception("Garanti: error when sending payment request: %s", str(e))
            tx_sudo._set_transaction_error(e)
            raise e
        # Save the transaction in the session
        PaymentProcessing.add_payment_transaction(tx_sudo)
        return response_content

    @http.route(
        _return_url,
        type="http",
        auth="public",
        csrf=False,
        save_session=False,
        methods=["POST", "GET"],
    )
    def garanti_return_from_3ds_auth(self, **kwargs):
        """
        Handle the return from the 3DS authentication.
        notification_data is a dict coming from Garanti.
        """
        # handle the response
        # Careful about the log here, it can contain sensitive information
        _logger.debug(
            "Garanti 3DS auth return received: return_from_3ds_auth: kwargs=%s",
            pprint.pformat(kwargs),
        )
        try:
            tx = (
                request.env["payment.transaction"]
                .sudo()
                .form_feedback(data=kwargs, acquirer_name="garanti")
            )
            # if tx.state != "done":
            #     raise ValidationError(_("Transaction not completed"))
        except:
            return _(
                "An error occurred while processing your payment. Please contact us."
            )

        # Redirect the user to the status page
        return request.render(
            "payment_garanti.garanti_payment_result",
            qcontext={
                "tx_id": tx,
                "order_id": fields.first(tx.sale_order_ids[0]),
            },
        )
