# Copyright 2022 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
import pprint
from odoo import _, http
from odoo.exceptions import ValidationError
from odoo.http import request

# from odoo.addons.payment import utils as payment_utils

_logger = logging.getLogger(__name__)


class GarantiController(http.Controller):
    _return_url = "/payment/garanti/return"

    @http.route("/payment/garanti/s2s/create_json_3ds", type="json", auth="public")
    def garanti_s2s_create_json_3ds(self, verify_validity=False, **kwargs):
        token = False
        acquirer = request.env["payment.acquirer"].browse(
            int(kwargs.get("acquirer_id"))
        )
        try:
            if not kwargs.get("partner_id"):
                kwargs = dict(kwargs, partner_id=request.env.user.partner_id.id)
            token = acquirer.s2s_process(kwargs)
        except ValidationError as e:
            message = e.args[0]
            if isinstance(message, dict) and "missing_fields" in message:
                if request.env.user._is_public():
                    message = _("Please sign in to complete the payment.")
                    # update message if portal mode = b2b
                    if (
                        request.env["ir.config_parameter"]
                        .sudo()
                        .get_param("auth_signup.allow_uninvited", "False")
                        .lower()
                        == "false"
                    ):
                        message += _(
                            " If you don't have any account, ask your salesperson to grant you a portal access. "
                        )
                else:
                    msg = _(
                        "The transaction cannot be processed because some contact details are missing or invalid: "
                    )
                    message = msg + ", ".join(message["missing_fields"]) + ". "
                    message += _("Please complete your profile. ")

            return {"error": message}

        card_args = dict()
        card_args["card_number"] = kwargs.get("cardNumber")
        card_args["card_cvv"] = kwargs.get("cardCVV")
        card_args["card_name"] = kwargs.get("cardName")
        card_args["card_valid_month"] = kwargs.get("cc_expiry")[0:2]
        card_args["card_valid_year"] = kwargs.get("cc_expiry")[6:]

        card_error = acquirer_sudo._garanti_validate_card_args(card_args)
        if card_error:
            raise ValidationError(card_error)

        # tx_sudo = (
        #     request.env["payment.transaction"]
        #     .sudo()
        #     .search([("reference", "=", reference)])
        # )

        client_ip = request.httprequest.environ.get("REMOTE_ADDR")

        response_content = acquirer_sudo._garanti_make_payment_request(
            amount, currency_id, card_args, client_ip
        )
        return response_content

    @http.route(
        _return_url,
        type="http",
        auth="public",
        csrf=False,
        save_session=False,
        methods=["POST"],
    )
    def garanti_return_from_3ds_auth(self, **kwargs):
        """
        Handle the return from the 3DS authentication.
        notification_data is a dict coming from Garanti.
        """
        tx_sudo = (
            request.env["payment.transaction"]
            .sudo()
            ._handle_notification_data("garanti", kwargs)
        )

        _logger.info(
            "handling redirection from Garanti for transaction with"
            " reference %s with data:\n%s",
            tx_sudo.reference,
            pprint.pformat(kwargs),
        )

        # Redirect the user to the status page
        return request.redirect("/payment/status")
