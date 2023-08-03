# Copyright 2023 Yiğit Budak (https://github.com/samettal)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
import requests
from odoo import _, fields, models
from datetime import datetime
from odoo.exceptions import ValidationError
from .garanti_connector import GarantiConnector
from odoo.addons.payment_garanti.const import TEST_URL, PROD_URL, CURRENCY_CODES

_logger = logging.getLogger(__name__)


class PaymentAcquirerGaranti(models.Model):
    _inherit = "payment.acquirer"
    provider = fields.Selection(selection_add=[("garanti", "Garanti")])

    garanti_merchant_id = fields.Char(
        string="Merchant ID",
        help="Merchant ID provided by Garanti Sanal Pos",
        required_if_provider="garanti",
        groups="base.group_user",
    )

    garanti_terminal_id = fields.Char(
        string="Terminal ID",
        help="Terminal ID provided by Garanti Sanal Pos",
        required_if_provider="garanti",
        groups="base.group_user",
    )

    garanti_prov_user = fields.Char(
        string="Provision User",
        help="Provision User provided by Garanti Sanal Pos",
        required_if_provider="garanti",
        groups="base.group_user",
    )

    garanti_prov_password = fields.Char(
        string="Provision Password",
        help="Provision Password provided by Garanti Sanal Pos",
        required_if_provider="garanti",
        groups="base.group_user",
    )

    garanti_store_key = fields.Char(
        string="Store Key",
        help="Store Key provided by Garanti Sanal Pos",
        required_if_provider="garanti",
        groups="base.group_user",
    )

    def garanti_s2s_form_process(self, data):
        values = {
            "cc_number": data.get("cc_number"),
            "cc_holder_name": data.get("cc_holder_name"),
            "cc_expiry": data.get("cc_expiry"),
            "cc_cvc": data.get("cc_cvc"),
            "cc_brand": data.get("cc_brand"),
            "acquirer_id": int(data.get("acquirer_id")),
            "partner_id": int(data.get("partner_id")),
        }
        PaymentMethod = self.env["payment.token"].sudo().create(values)
        return PaymentMethod

    def garanti_s2s_form_validate(self, data):
        error = dict()
        mandatory_fields = [
            "cc_number",
            "cc_cvc",
            "cc_holder_name",
            "cc_expiry",
        ]
        # Validation
        for field_name in mandatory_fields:
            if not data.get(field_name):
                error[field_name] = "missing"
        if data["cc_expiry"]:
            # FIX we split the date into their components and check if there is two components containing only digits
            # this fixes multiples crashes, if there was no space between the '/' and the components the code was crashing
            # the code was also crashing if the customer was proving non digits to the date.
            cc_expiry = [i.strip() for i in data["cc_expiry"].split("/")]
            if len(cc_expiry) != 2 or any(not i.isdigit() for i in cc_expiry):
                return False
            try:
                expiry_date = datetime.strptime(
                    "/".join(cc_expiry),
                    "%m/%{}".format("y" if len(cc_expiry[1]) == 2 else "Y"),
                ).strftime("%y%m")
                if datetime.now().strftime("%y%m") > expiry_date:
                    return False
            except ValueError:
                return False
        return False if error else True


class GarantiPaymentToken(models.Model):
    _inherit = "payment.token"

    def garanti_create(self, values):
        if values.get("cc_number"):
            values["cc_number"] = values["cc_number"].replace(" ", "")
            acquirer = self.env["payment.acquirer"].browse(values["acquirer_id"])
            expiry = str(values["cc_expiry"][:2]) + str(values["cc_expiry"][-2:])
            partner = self.env["res.partner"].browse(values["partner_id"])
            transaction = GarantiConnector(acquirer)
            res = transaction.create_customer_profile(
                partner, values["cc_number"], expiry, values["cc_cvc"]
            )
            if res.get("profile_id") and res.get("payment_profile_id"):
                return {
                    "authorize_profile": res.get("profile_id"),
                    "name": "XXXXXXXXXXXX%s - %s"
                    % (values["cc_number"][-4:], values["cc_holder_name"]),
                    "acquirer_ref": res.get("payment_profile_id"),
                }
            else:
                raise ValidationError(
                    _("The Customer Profile creation in Authorize.NET failed.")
                )
        else:
            return values

        # STRIPE
        token = values.get("stripe_token")
        description = None
        payment_acquirer = self.env["payment.acquirer"].browse(
            values.get("acquirer_id")
        )
        # when asking to create a token on Stripe servers
        if values.get("cc_number"):
            url_token = "https://%s/tokens" % payment_acquirer._get_stripe_api_url()
            payment_params = {
                "card[number]": values["cc_number"].replace(" ", ""),
                "card[exp_month]": str(values["cc_expiry"][:2]),
                "card[exp_year]": str(values["cc_expiry"][-2:]),
                "card[cvc]": values["cvc"],
                "card[name]": values["cc_holder_name"],
            }
            r = requests.post(
                url_token,
                auth=(payment_acquirer.stripe_secret_key, ""),
                params=payment_params,
                headers=STRIPE_HEADERS,
            )
            token = r.json()
            description = values["cc_holder_name"]
        else:
            partner_id = self.env["res.partner"].browse(values["partner_id"])
            description = "Partner: %s (id: %s)" % (partner_id.name, partner_id.id)

        if not token:
            raise UserError(
                _("Stripe: no payment token was provided or the token creation failed.")
            )

        res = self._stripe_create_customer(token, description, payment_acquirer.id)

        # pop credit card info to info sent to create
        for field_name in [
            "cc_number",
            "cvc",
            "cc_holder_name",
            "cc_expiry",
            "cc_brand",
            "stripe_token",
        ]:
            values.pop(field_name, None)
        return res
