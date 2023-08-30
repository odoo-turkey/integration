# Copyright 2022 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
import pprint
from odoo import _, http
from odoo.exceptions import ValidationError
from odoo.http import request
from odoo.addons.payment import utils as payment_utils

_logger = logging.getLogger(__name__)


class GarantiController(http.Controller):
    _webhook_url = '/payment/garanti/payments'
    _return_url = '/payment/garanti/return'

    @http.route(_webhook_url, type='json', auth='public')
    def garanti_payments(
            self, provider_id, reference, amount, currency_id, partner_id,
            access_token, card_args
    ):
        """ Make a payment request and handle the notification data.

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

        # Prepare the payment request to Garanti
        provider_sudo = request.env['payment.provider'].sudo().browse(
            provider_id).exists()

        card_error = provider_sudo._garanti_validate_card_args(card_args)
        if card_error:
            raise ValidationError(card_error)

        tx_sudo = request.env['payment.transaction'].sudo().search(
            [('reference', '=', reference)])

        client_ip = request.httprequest.environ.get('REMOTE_ADDR')

        response_content = provider_sudo._garanti_make_payment_request(tx_sudo,
                                                                       amount,
                                                                       currency_id,
                                                                       card_args,
                                                                       client_ip)
        return response_content

    @http.route(_return_url, type='http', auth='public',
                csrf=False, save_session=False, methods=['POST'])
    def garanti_return_from_3ds_auth(self, **kwargs):
        """
        Handle the return from the 3DS authentication.
        notification_data is a dict coming from Garanti.
        """
        tx_sudo = request.env[
            'payment.transaction'].sudo()._handle_notification_data(
            'garanti', kwargs
        )

        _logger.info(
            "handling redirection from Garanti for transaction with"
            " reference %s with data:\n%s",
            tx_sudo.reference, pprint.pformat(kwargs)
        )

        # Redirect the user to the status page
        return request.redirect('/payment/status')
