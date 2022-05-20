# Copyright 2022 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import phonenumbers
from odoo import _, fields, models
from odoo.exceptions import ValidationError
from .yurtici_request import YurticiRequest


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    delivery_type = fields.Selection(selection_add=[("yurtici", "Yurtiçi Kargo")])

    yurtici_username = fields.Char(string="Username", help="Yurtiçi Username")
    yurtici_password = fields.Char(string="Password", help="Yurtiçi Password")
    yurtici_user_lang = fields.Char('UserLanguage', help="UserLanguage field for Yurtiçi")
    yurtici_query_type = fields.Selection(
        selection=[(1, "Query by Order Number"), (2, "Query by Shipment Number")],
        string="Query Type", default=1, help="Yurtiçi Kargo has two query types. You can only query"
                                             "with shipment number when the order is delivered to Yurtiçi.")

    def _get_yurtici_credentials(self):
        """Access key is mandatory for every request while group and user are
        optional"""
        credentials = {
            "prod": self.prod_environment,
            "username": self.yurtici_username,
            "password": self.yurtici_password,
            'user_language': self.yurtici_user_lang,
        }
        return credentials

    def _yurtici_address(self, partner):
        """Sender address is the address of the company, required field.
        """
        return partner._display_address()

    def _yurtici_phone_number(self, partner, priority='mobile'):
        """
        Sendeo requires phone number without spaces and country code.
        We use priority selector to handle two different phone numbers.
        :param partner: recordset res.partner
        :param priority: string
        :return: phone number without spaces and country code
        """
        priority_field = getattr(partner, priority)
        if priority_field:
            return phonenumbers.format_number(
                phonenumbers.parse(priority_field, partner.country_id.code or "TR"),
                phonenumbers.PhoneNumberFormat.E164).lstrip('+90')
        elif partner.phone or partner.mobile:
            return phonenumbers.format_number(
                phonenumbers.parse(partner.phone or partner.mobile, partner.country_id.code or "TR"),
                phonenumbers.PhoneNumberFormat.E164).lstrip('+90')
        else:
            raise ValidationError(_("%s\nPartner's phone number is missing."
                                    " It's a required field for dispatch."
                                    % partner.name))

    def _prepare_yurtici_pack_info(self, picking):
        # TODO: implement stock.quant.package
        vals = {
            'desi': 1,
            'kg': 1,
            'cargoCount': picking.number_of_packages,
        }
        return vals

    def _sendeo_district_code(self, partner):
        code = partner.district_id.sendeo_code
        if code:
            return int(code)
        else:
            raise ValidationError(_("%s\nPartner's district code is missing."))

    def _prepare_yurtici_shipping(self, picking):
        """Convert picking values for Yurtiçi Kargo api
        :param picking record with picking to send
        :returns dict values for the connector
        """
        self.ensure_one()
        # We'll compose the request via some diferenced parts, like label settings,
        # address options, incoterms and so. There are lots of thing to take into
        # account to acomplish a properly formed request.
        vals = {}
        vals.update(
            {
                "cargoKey": picking.name,
                "invoiceKey": picking.name,  # TODO: implement invoice key
                "receiverCustName": picking.partner_id.display_name,
                "receiverAddress": self._yurtici_address(picking.partner_id),
                "receiverPhone1": self._sendeo_phone_number(picking.company_id.partner_id, priority='mobile'),
                "receiverPhone2": self._sendeo_phone_number(picking.company_id.partner_id, priority='phone'),
                "cityName": picking.partner_id.state_id.name,
                "townName": picking.partner_id.district_id.name,
                "waybillNo": picking.name,  # TODO: implement waybill number
            }
        )
        pack_info = self._prepare_yurtici_pack_info(picking)
        vals.update(pack_info)
        return vals

    def yurtici_send_shipping(self, pickings):
        """Send booking request to Yurtiçi
        :param pickings: A recordset of pickings
        :return list: A list of dictionaries although in practice it's
        called one by one and only the first item in the dict is taken. Due
        to this design, we have to inject vals in the context to be able to
        add them to the message.
        """
        yurtici_request = YurticiRequest(**self._get_yurtici_credentials())
        result = []
        for picking in pickings:
            vals = self._prepare_yurtici_shipping(picking)
            try:
                response = yurtici_request._send_shipping(vals)
            except Exception as e:
                raise e

            if not response:
                result.append(vals)
                continue
            vals["tracking_number"] = response.cargoKey
            vals["exact_price"] = 0.0
            result.append(vals)
        return result

    def yurtici_cancel_shipment(self, pickings):
        """Cancel the expedition
        :param pickings - stock.picking recordset
        :returns bool
        """
        yurtici_request = YurticiRequest(**self._get_yurtici_credentials())
        for picking in pickings.filtered("carrier_tracking_ref"):
            yurtici_request._cancel_shipment(picking.name)
            # picking.write({"carrier_tracking_ref": False,
            #                "tracking_state": False,
            #                "tracking_state_history": _('Cancelled')})
        return True

    def yurtici_get_tracking_link(self, picking):
        """Provide tracking link for the customer"""
        return (
                "http://selfservis.yurticikargo.com/reports/"
                "SSWDocumentDetail.aspx?DocId=%s"
                % picking.carrier_tracking_ref
        )

    def yurtici_tracking_state_update(self, picking):
        """Tracking state update"""
        self.ensure_one()
        if not picking.carrier_tracking_ref:
            return
        yurtici_request = YurticiRequest(**self._get_yurtici_credentials())
        response = yurtici_request._query_shipment(picking, self.yurtici_query_type)
        status = response.operationMessage
        picking.write(
            {
                "tracking_state_history": "{} - [{}]".format(fields.Date.today().strftime('%d.%m.%Y'), status),
                "tracking_state": status,
            }
        )
        return True

    def sendeo_carrier_get_label(self, picking):
        """
        Yurtiçi Kargo doesn't provide label for shipments.
        They are not implemented common label on their systems.
        """
        raise NotImplementedError(
            _(
                "Sendeo API doesn't provide methods to print label."
            )
        )

    def yurtici_rate_shipment(self, order):
        """There's no public API so another price method should be used."""
        raise NotImplementedError(
            _(
                "Sendeo API doesn't provide methods to compute delivery "
                "rates, so you should relay on another price method instead or "
                "override this one in your custom code."
            )
        )

    def yurtici_get_rate(self, order):
        """Get delivery price for Yurtiçi"""
        return self._calculate_deci(order)
