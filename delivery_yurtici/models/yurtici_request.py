# Copyright 2022 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from zeep import Client, Settings
from zeep.exceptions import Fault
from zeep.plugins import HistoryPlugin
from zeep import xsd
from xml.etree import ElementTree as ET
from odoo import _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

YURTICI_API_URL = {"prod": "https://webservices.yurticikargo.com/"
                           "KOPSWebServices/ShippingOrderDispatcherServices?wsdl",
                   "test": "https://testwebservices.yurticikargo.com/"
                           "KOPSWebServices/ShippingOrderDispatcherServices?wsdl"}


class YurticiRequest:
    """Interface between Yurtiçi Kargo REST API and Odoo recordset
       Abstract Aras Kargo API Operations to connect them with Odoo

       Not all the features are implemented, but could be easily extended with
       the provided API. We leave the operations empty for future.
    """

    def __init__(
        self, username=None, password=None, user_language=None, prod=False
    ):
        self.username = username or ""
        self.password = password or ""
        self.user_language = user_language or ""
        api_env = "prod" if prod else "test"
        self.history = HistoryPlugin(maxlen=10)
        settings = Settings(strict=False, xml_huge_tree=True)
        self.client = Client(
            wsdl=YURTICI_API_URL[api_env],
            settings=settings,
            plugins=[self.history],
        )

    def _shipping_api_credentials(self):
        """ API credentials for Yurtici Kargo Web Services
        """
        return {
            'wsUserName': self.username,
            'wsPassword': self.password,
            'userLanguage': self.user_language,
        }

    def _process_reply(self, service, vals=None, send_as_kw=False):
        """Yurtiçi API returns error petitions as server exceptions wich makes zeep to
        raise a Fault exception as well. To catch the error info we need to make a
        raw_response request and the extract the error codes from the response."""
        try:
            if not send_as_kw:
                response = service(vals)
            else:
                response = service(**vals)
        except Fault as e:
            with self.client.settings(raw_response=True):
                if not send_as_kw:
                    response = service(vals)
                else:
                    response = service(**vals)
                try:
                    root = ET.fromstring(response.text)
                    error_text = next(root.iter("faultstring")).text
                    error_message = next(root.iter("message")).text
                    error_code = next(root.iter("code")).text
                    raise ValidationError(
                        _(
                            "Error in the request to the Yurtiçi API. This is the "
                            "thrown message:\n\n"
                            "[%s]\n"
                            "%s - %s" % (error_text, error_code, error_message)
                        )
                    )
                except ValidationError:
                    raise
                # If we can't get the proper exception, fallback to the first
                # exception error traceback
                except Exception:
                    raise Fault(e)

        if response.outFlag != '0':
            raise ValidationError("%s %s" % (response.errCode, response.outResult))

        return response

    def _fill_empty_fields(self, vals, method):
        """
        Fill empty fields with xsd.SkipValue (pass)
        :param vals: dict
        :param method: web service function
        :return: dict
        """
        func = self.client.get_type(method)
        for field in func.elements:
            if field[0] not in vals:
                vals[field[0]] = xsd.SkipValue

        return vals

    def _send_shipping(self, picking_vals, method=False):
        """Create new shipment
        :params vals dict of needed values
        :returns dict with Yurtici response containing the shipping code and label
        """
        vals = self._shipping_api_credentials()
        filled_fields = self._fill_empty_fields(picking_vals, 'ns0:ShippingOrderVO')
        vals.update({'ShippingOrderVO': filled_fields})
        response = self._process_reply(self.client.service.createShipment, vals, send_as_kw=True)
        return response.shippingOrderDetailVO[0]

    def _cancel_shipment(self, cargo_keys):
        """Cancel the expedition for the given ref
        :param str picking_name -- reference (picking name)
        :param int query_type -- yurtici_query_type field
        :returns: bool True if success
        """
        vals = self._shipping_api_credentials()
        vals.update({'cargoKeys': cargo_keys})
        response = self._process_reply(self.client.service.cancelShipment, vals, send_as_kw=True)
        return response

    def _query_shipment(self, picking, query_type=False):
        """Get tracking status of the given ref
        :param str picking_name -- reference (picking name)
        :param int query_type -- yurtici_query_type field
        :returns: Yurtiçi queryShipment object
        """
        vals = self._shipping_api_credentials()
        keys_val = picking.name if query_type == 1 else picking.client_tracking_ref
        vals['wsLanguage'] = vals.pop('userLanguage')  # this method requires the language field in wsLanguage
        vals.update({'keys': keys_val,
                     'keyType': query_type,  # 0 = picking_name, 1 = tracking_number
                     'addHistoricalData': True,
                     'onlyTracking': False})
        response = self._process_reply(self.client.service.queryShipment, vals, send_as_kw=True)
        return response.shippingDeliveryDetailVO[0]
