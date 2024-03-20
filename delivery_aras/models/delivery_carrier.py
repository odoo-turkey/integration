# Copyright 2024 Ahmet Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import phonenumbers
from odoo import _, fields, models, api
from odoo.exceptions import ValidationError
from .aras_request import ArasRequest
from lxml import etree
from datetime import datetime

ARAS_OPERATION_CODES = {
    0: ("Kargo İşlem Görmemiş", "shipping_recorded_in_carrier"),
    1: ("Kargo Teslimattadır", "in_transit"),
    2: ("Kargo işlem görmüş, faturası henüz düzenlenmemiş", "in_transit"),
    3: ("Kargo Çıkışı Engellendi", "canceled_shipment"),
    4: ("Kargo daha önceden iptal edilmiştir.", "canceled_shipment"),
    5: ("Kargo Teslim edilmiştir.", "customer_delivered"),
}


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    delivery_type = fields.Selection(selection_add=[("aras", "Aras Kargo")])

    aras_username = fields.Char(string="Username", help="Aras Username")
    aras_password = fields.Char(string="Password", help="Aras Password")
    aras_customer_code = fields.Char(string="Customer Code", help="Aras Customer Code")

    def _get_aras_credentials(self):
        """Access key is mandatory for every request while group and user are
        optional"""
        credentials = {
            "prod": self.prod_environment,
            "username": self.aras_username,
            "password": self.aras_password,
            "customer_code": self.aras_customer_code,
        }
        return credentials

    def _aras_address(self, partner):
        """Sender address is the address of the company, required field."""
        return partner._display_address()

    def _aras_phone_number(self, partner, priority="mobile"):
        """
        Aras requires phone number without spaces and country code.
        We use priority selector to handle two different phone numbers.
        :param partner: recordset res.partner
        :param priority: string
        :return: phone number without spaces and country code
        """
        priority_field = getattr(partner, priority)
        if priority_field:
            return phonenumbers.format_number(
                phonenumbers.parse(priority_field, partner.country_id.code or "TR"),
                phonenumbers.PhoneNumberFormat.E164,
            ).lstrip("+9")
        elif partner.phone or partner.mobile:
            return phonenumbers.format_number(
                phonenumbers.parse(
                    partner.phone or partner.mobile, partner.country_id.code or "TR"
                ),
                phonenumbers.PhoneNumberFormat.E164,
            ).lstrip("+9")
        else:
            raise ValidationError(
                _(
                    "%s\nPartner's phone number is missing."
                    " It's a required field for dispatch." % partner.name
                )
            )

    def _prepare_aras_piece_details(self, picking, mok_code):
        """It's required to write down product barcodes for Piece Detail"""
        self.ensure_one()
        vals = [
            {
                "PieceDetail": {
                    "BarcodeNumber": mok_code,
                    "VolumetricWeight": max(picking.picking_total_weight, 1),
                    "Weight": picking.weight,
                }
            }
        ]
        return vals

    def _prepare_aras_shipping(self, picking):
        """Convert picking values for Aras Kargo api
        :param picking record with picking to send
        :returns dict values for the connector
        """
        self.ensure_one()
        # We'll compose the request via some diferenced parts, like label settings,
        # address options, incoterms and so. There are lots of thing to take into
        # account to acomplish a properly formed request.
        vals = {}
        mok_code = self._get_ref_number()
        vals.update(
            {
                "InvoiceNumber": picking.name,
                "IntegrationCode": mok_code,
                "ReceiverName": picking.partner_id.display_name[:100], # Aras Kargo has a 100 characters limit for receiver name
                "ReceiverAddress": self._aras_address(picking.partner_id),
                "ReceiverPhone1": self._aras_phone_number(
                    picking.partner_id, priority="mobile"
                ),
                "ReceiverPhone2": self._aras_phone_number(
                    picking.partner_id, priority="phone"
                ),
                "ReceiverCityName": picking.partner_id.state_id.name,
                "ReceiverTownName": picking.partner_id.district_id.name,
                "TradingWaybillNumber": picking.name,
                "PayorTypeCode": 1,  # 1 = Sender, 2 = Receiver
                "IsWorldWide": 0,
                "PieceCount": 1,  # Todo: implement piece count
            }
        )
        piece_details = self._prepare_aras_piece_details(picking, mok_code)
        # vals.update({"PieceDetails": piece_details, "PieceCount": len(piece_details)})
        vals.update({"PieceDetails": piece_details})
        return vals

    def aras_send_shipping(self, pickings):
        """Send booking request to Aras
        :param pickings: A recordset of pickings
        :return list: A list of dictionaries although in practice it's
        called one by one and only the first item in the dict is taken. Due
        to this design, we have to inject vals in the context to be able to
        add them to the message.
        """
        aras_request = ArasRequest(**self._get_aras_credentials())
        result = []
        for picking in pickings:
            vals = self._prepare_aras_shipping(picking)
            try:
                response = aras_request._send_shipping(vals)

            except Exception as e:
                raise e

            finally:
                self._aras_log_request(aras_request)

            if not response:
                result.append(vals)
                continue
            vals["tracking_number"] = response.OrgReceiverCustId
            vals["exact_price"] = 0.0
            result.append(vals)
        return result

    @api.model
    def _aras_log_request(self, aras_request):
        """Helper to write raw request/response to the current picking. If debug
        is active in the carrier, those will be logged in the ir.logging as well"""
        aras_last_request = aras_last_response = False
        try:
            aras_last_request = etree.tostring(
                aras_request.history.last_sent["envelope"],
                encoding="UTF-8",
                pretty_print=True,
            )
            aras_last_response = etree.tostring(
                aras_request.history.last_received["envelope"],
                encoding="UTF-8",
                pretty_print=True,
            )
        # Don't fail hard on this. Sometimes zeep could not be able to keep history
        except Exception:
            return
        # Debug must be active in the carrier
        self.log_xml(aras_last_request, "aras_request")
        self.log_xml(aras_last_response, "aras_response")

    def aras_cancel_shipment(self, pickings):
        """Cancel the expedition
        :param pickings - stock.picking recordset
        :returns bool
        """
        aras_request = ArasRequest(**self._get_aras_credentials())
        for picking in pickings.filtered("carrier_tracking_ref"):
            if hasattr(
                self, "%s_tracking_state_update" % self.delivery_type
            ):  # check state before cancel
                getattr(self, "%s_tracking_state_update" % self.delivery_type)(picking)

            if picking.delivery_state not in [
                "shipping_recorded_in_carrier",
                "canceled_shipment",
            ]:
                raise ValidationError(
                    _(
                        "You can't cancel a shipment that already has been sent to Aras Kargo"
                    )
                )

            try:
                aras_request._cancel_shipment(picking.carrier_tracking_ref)
            except Exception as e:
                raise e
            finally:
                self._aras_log_request(aras_request)
            # picking.write({"carrier_tracking_ref": False,
            #                "tracking_state": False,
            #                "tracking_state_history": _('Cancelled')})
        return True

    def yurtici_get_tracking_link(self, picking):
        """Provide tracking link for the customer"""
        return (
            f"https://www.yurticikargo.com/tr/online-servisler/"
            f"gonderi-sorgula?code={picking.shipping_number}"
        )

    def aras_tracking_state_update(self, picking):
        """Tracking state update"""
        self.ensure_one()
        if not picking.carrier_tracking_ref:
            return
        aras_request = ArasRequest(**self._get_aras_credentials())

        try:
            response = aras_request._query_shipment(picking)
        except Exception as e:
            raise e
        finally:
            self._yurtici_log_request(yurtici_request)

        if response.errCode:
            return False

        vals = {
            "tracking_state": response.operationMessage,
            "delivery_state": YURTICI_OPERATION_CODES[response.operationCode][1],
        }

        if response.operationCode != 0 and response.shippingDeliveryItemDetailVO:
            vals.update(self._yurtici_update_picking_fields(response))

        picking.write(vals)
        return True

    def _yurtici_update_picking_fields(self, response):
        vals = {
            "shipping_number": response.shippingDeliveryItemDetailVO.docId,
        }

        if len(response.shippingDeliveryItemDetailVO.invDocCargoVOArray) > 0:
            text = ""
            for line in response.shippingDeliveryItemDetailVO.invDocCargoVOArray:
                text += "[%s] [%s] %s\n" % (
                    line.eventDate,
                    line.unitName,
                    line.eventName,
                )
            vals.update({"tracking_state_history": text})

        if response.shippingDeliveryItemDetailVO:
            vals.update(
                {
                    "carrier_total_deci": float(
                        response.shippingDeliveryItemDetailVO.totalDesiKg
                    ),
                    "carrier_shipping_cost": float(
                        response.shippingDeliveryItemDetailVO.totalPrice
                    ),
                    "carrier_shipping_vat": float(
                        response.shippingDeliveryItemDetailVO.totalVat
                    ),
                    "carrier_shipping_total": float(
                        response.shippingDeliveryItemDetailVO.totalAmount
                    ),
                }
            )

        if response.operationCode == 5:  # Delivered
            vals.update(
                {
                    "carrier_received_by": response.shippingDeliveryItemDetailVO.receiverInfo,
                    "date_delivered": datetime.strptime(
                        response.shippingDeliveryItemDetailVO.deliveryDate, "%Y%m%d"
                    ),
                }
            )

        return vals

    def aras_carrier_get_label(self, picking):
        """
        Aras Kargo doesn't provide label for shipments.
        They are not implemented common label on their systems.
        """
        raise NotImplementedError(
            _("Aras Kargo API doesn't provide methods to print label.")
        )

    def aras_rate_shipment(self, order):
        """There's no public API so use rules for calculation."""
        return self.base_on_rule_rate_shipment(order)

    def aras_get_rate(self, order):
        """Get delivery price for Aras"""
        return self.base_on_rule_get_rate(order)
