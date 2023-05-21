# Copyright 2023 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import logging
from zeep import Client, Settings
from zeep.exceptions import Fault
from zeep.plugins import HistoryPlugin
from zeep import xsd
from xml.etree import ElementTree as ET
from odoo import _
from odoo.exceptions import ValidationError

PARAM_TEST_API = (
    "https://test-dmz.param.com.tr:4443/turkpos.ws/service_turkpos_test.asmx?wsdl"
)


class ParamConnector:
    def __init__(self, **kwargs):
        self.client_code = kwargs.get("client_code")
        self.username = kwargs.get("username")
        self.password = kwargs.get("password")
        self.guid = kwargs.get("guid")
        api_env = kwargs.get("param_endpoint")
        self.history = HistoryPlugin(maxlen=10)
        settings = Settings(strict=False, xml_huge_tree=True)
        self.client = Client(
            wsdl=api_env,
            settings=settings,
            plugins=[self.history],
        )

    def _pos_odeme(self, transaction_data):
        """
        Bu metot, Nonsecure / 3D ödeme işleminin başlatılacağı metottur.
        (SanalPOS_ID parametresi kaldırılmıştır.) İşlem sonucu dönen 3D
        URL sine yönlendirme yapılır ve kredi kartı ile ödeme işlemi başlar.
        https://dev.param.com.tr/tr/api/oedeme-v2
        """
        return self.client.service.Pos_Odeme(**transaction_data)

    def _calculate_sha2b64(self, transcation_data):
        """
        Calculate SHA2B64 with transcation data
        Formula:
        Dim Islem_Guvenlik_Str$ = CLIENT_CODE & GUID & Taksit &
        Islem_Tutar & Toplam_Tutar & Siparis_ID & Hata_URL & Basarili_URL
        Dim Islem_Hash$ = SHA2B64(Islem_Guvenlik_Str)
        https://dev.param.com.tr/tr/api/sha2b64
        """
        concat_str = (
            self.client_code
            + self.guid
            + str(1)  # we are not using installments for now
            + transcation_data["amount"]
            + transcation_data["total_amount"]
            + transcation_data["order_id"]
            + transcation_data["error_url"]
            + transcation_data["success_url"]
        )
        return self.client.service.SHA2B64(concat_str)
