# Copyright 2022 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
import pprint
from odoo import _, http
from odoo.exceptions import ValidationError
from odoo.http import request
from odoo.addons.payment import utils as payment_utils

_logger = logging.getLogger(__name__)


class ParamController(http.Controller):
    _webhook_url = "/payment/param/payments"
    _return_url = "/payment/param/return"

    @http.route(_webhook_url, type="json", auth="public")
    def param_payments(
        self,
        provider_id,
        reference,
        amount,
        currency_id,
        partner_id,
        access_token,
        card_args,
    ):
        """Make a payment request and handle the notification data.

        :param int provider_id: The provider handling the transaction, as a `payment.provider` id
        :param str reference: The reference of the transaction
        :param int amount: The amount of the transaction in minor units of the currency
        :param int currency_id: The currency of the transaction, as a `res.currency` id
        :param int partner_id: The partner making the transaction, as a `res.partner` id
        :param str access_token: The access token used to verify the provided values
        :param dict card_args: The card details
        :return: The JSON-formatted content of the response
        :rtype: dict
        """
        # Check that the transaction details have not been altered.
        # This allows preventing users
        # from validating transactions by paying less than agreed upon.
        if not payment_utils.check_access_token(
            access_token, reference, amount, partner_id
        ):
            raise ValidationError(
                "Param: " + _("Received tampered payment request data.")
            )

        # Prepare the payment request to Param
        provider_sudo = (
            request.env["payment.provider"].sudo().browse(provider_id).exists()
        )

        card_error = provider_sudo._param_validate_card_args(card_args)
        if card_error:
            raise ValidationError(card_error)

        tx_sudo = (
            request.env["payment.transaction"]
            .sudo()
            .search([("reference", "=", reference)])
        )

        client_ip = request.httprequest.environ.get("REMOTE_ADDR")

        resp = provider_sudo._param_make_payment_request(
            tx_sudo, amount, currency_id, card_args, client_ip
        )
        # Handle the response
        return {"redirect_url": resp}

    @http.route(
        _return_url,
        type="http",
        auth="public",
        csrf=False,
        save_session=False,
        methods=["POST"],
    )
    def param_return_from_3ds_auth(self, **kwargs):
        """
        Handle the return from the 3DS authentication.
        notification_data is a dict coming from Param.
        """
        tx_sudo = (
            request.env["payment.transaction"]
            .sudo()
            ._handle_notification_data("param", kwargs)
        )

        _logger.info(
            "handling redirection from Param for transaction with"
            " reference %s with data:\n%s",
            tx_sudo.reference,
            pprint.pformat(kwargs),
        )

        # Redirect the user to the status page
        return request.redirect("/payment/status")
