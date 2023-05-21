# Copyright 2022 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.addons.payment_param.const import PARAM_ERROR_CODES
from odoo.addons.payment_param.models.param_connector import (
    PARAM_TEST_API,
    ParamConnector,
)

_logger = logging.getLogger(__name__)


class PaymentProvider(models.Model):
    _inherit = "payment.provider"

    code = fields.Selection(
        selection_add=[("param", "Param")], ondelete={"param": "set default"}
    )
    param_client_code = fields.Char(
        string="Param Client Code",
        help="Dealer code issued by the Param system",
        required_if_provider="param",
    )
    param_username = fields.Char(
        string="Param Username",
        help="Api username given by Param system",
        groups="base.group_system",
    )
    param_password = fields.Char(
        string="Param Password",
        help="Api password given by Param system",
        groups="base.group_system",
    )
    param_guid = fields.Char(
        string="Param Guid",
        help="Guid given by Param system",
        groups="base.group_system",
    )
    param_live_endpoint = fields.Char(
        string="Param Live Endpoint",
        help="Param live endpoint",
        groups="base.group_system",
    )

    def _param_get_api_url(self):
        """Return the API URL according to the provider state.

        Note: self.ensure_one()

        :return: The API URL
        :rtype: str
        """
        self.ensure_one()

        if self.state == "enabled":
            return self.param_live_endpoint
        else:
            return PARAM_TEST_API

    def _param_format_card_number(self, card_number):
        """
        This method is used to format the card number
        :param card_number: The card number
        :return: The formatted card number
        """
        card_number = card_number.replace(" ", "")
        if len(card_number) == 16 and card_number.isdigit():
            return card_number
        else:
            raise ValidationError(_("Card number is not valid."))

    def _param_validate_card_args(self, card_args):
        """
        Validation method for credit/debit card information
        :param card_args: The card information
        :return: error message if there is any error
        """
        error = ""
        card_number = card_args.get("card_number")
        card_cvv = card_args.get("card_cvv")
        if not card_number or len(card_number) < 16:
            error += _("Card number is not valid.\n")

        if not card_cvv or len(card_cvv) < 3:
            error += _("Card CVV is not valid.\n")

        if not card_args.get("card_name"):
            error += _("Card name is not valid.\n")

        if not card_args.get("card_valid_month") or not card_args.get(
            "card_valid_year"
        ):
            error += _("Card expiration date is not valid.\n")
        return error

    def _param_format_phone(self, tx_phone):
        """
        This method is used to format the phone number
        :param tx_phone: The phone number
        :return: The formatted phone number
        """
        tx_phone = tx_phone.replace(" ", "").lstrip("0")
        if len(tx_phone) == 10 and tx_phone.isdigit():
            return tx_phone
        else:
            raise ValidationError(_("Phone number is not valid."))

    def _param_get_return_url(self):
        """
        This method is used to get the return url for the Param API
        :return: The return url
        """
        self.ensure_one()
        return (
            self.env["ir.config_parameter"].sudo().get_param("web.base.url")
            + "/payment/param/return"
        )

    def _param_format_amount(self, amount):
        """
        This method is used to format the amount
        :param amount: The amount
        :return: The formatted amount
        """
        return str(amount).replace(".", ",")

    def _param_get_payment_url(self):
        """
        This method is used to get the payment url for the Param API
        :return: The payment url
        """
        self.ensure_one()
        return (
            self.env["ir.config_parameter"].sudo().get_param("web.base.url")
            + "/shop/payment"
        )

    def _param_get_payment_vals(
        self, tx, amount, currency, card_args, client_ip, connector
    ):
        return_url = self._param_get_return_url()
        amount = self._param_format_amount(amount)

        # Build the hash
        islem_hash = connector._calculate_sha2b64(
            {
                "amount": amount,
                "total_amount": amount,
                "order_id": tx.reference,
                "error_url": return_url,
                "success_url": return_url,
            }
        )

        # Build the payment values
        return {
            "G": {
                "CLIENT_CODE": self.param_client_code,
                "CLIENT_USERNAME": self.param_username,
                "CLIENT_PASSWORD": self.param_password,
            },
            "GUID": self.param_guid,
            "KK_Sahibi": card_args.get("card_name"),
            "KK_No": self._param_format_card_number(card_args.get("card_number")),
            "KK_SK_Ay": card_args.get("card_valid_month"),
            "KK_SK_Yil": card_args.get("card_valid_year"),
            "KK_CVC": card_args.get("card_cvv"),
            "KK_Sahibi_GSM": tx.partner_phone,
            "Hata_URL": return_url,
            "Basarili_URL": return_url,
            "Siparis_ID": tx.reference,
            "Siparis_Aciklama": tx.reference,
            "Taksit": 1,
            "Islem_Tutar": amount,
            "Toplam_Tutar": amount,
            "Islem_Hash": islem_hash,
            "Islem_Guvenlik_Tip": "3D",
            "Islem_ID": None,
            "IPAdr": client_ip,
            "Ref_URL": self._param_get_payment_url(),
            "Data1": None,
            "Data2": None,
            "Data3": None,
            "Data4": None,
            "Data5": None,
            "Data6": None,
            "Data7": None,
            "Data8": None,
            "Data9": None,
            "Data10": None,
        }

    def _param_make_payment_request(self, tx, amount, currency, card_args, client_ip):
        """
        This method is used to make a payment request to the Param API
        :param tx: The transaction
        :param amount: The amount of the transaction
        :param currency: The currency of the transaction
        """
        self.ensure_one()
        connector = ParamConnector(
            client_code=self.param_client_code,
            username=self.param_username,
            password=self.param_password,
            guid=self.param_guid,
            param_endpoint=self._param_get_api_url(),
        )
        vals = self._param_get_payment_vals(
            tx, amount, currency, card_args, client_ip, connector
        )
        try:
            resp = connector._pos_odeme(vals)
            if resp.Sonuc != "1":
                raise ValidationError(
                    "%s" % PARAM_ERROR_CODES.get(resp.Sonuc, _("Unknown Error"))
                )
            else:
                # Save the transaction id for validation
                tx.sudo().write(
                    {
                        "param_islem_id": resp.Islem_ID,
                    }
                )
                return resp.UCD_URL
        except:
            raise ValidationError(_("Payment request failed."))
