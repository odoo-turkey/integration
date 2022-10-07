# Copyright 2022 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import re
from woocommerce import API
from base64 import b64encode, b64decode
import magic
import requests

http_regex = re.compile(
    r'^(?:http|ftp)s?://'  # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)


class WooCommerceBackend(models.Model):
    _name = 'woocommerce.backend'
    _description = 'Connector model for WooCommerce'

    name = fields.Char(string='Name')
    hostname = fields.Char(string='Hostname', required=True, help="Example: https://www.altinkaya.com.tr")
    consumer_key = fields.Char(string='Consumer Key', required=True)
    consumer_secret = fields.Char(string='Consumer Secret', required=True)
    wp_app_user = fields.Char(string='App User', required=True)
    wp_app_key = fields.Char(string='App Key', required=True, help='Wordpress application password')
    version = fields.Selection(selection=[('wc/v3', 'wc/v3')], string='Version', default='wc/v3')
    request_timeout = fields.Integer(string='Request Timeout', default=60,
                                     help="Timeout in seconds for requests to WooCommerce.")
    # Product Fields
    product_price_type_id = fields.Many2one('product.price.type', string='Product Price Type', required=True,
                                            help="Product price field.")
    location_ids = fields.Many2many(comodel_name='stock.location', string='Stock Locations', required=True,
                                    help="Stock locations to be used for WooCommerce stock managing.")
    # Sale Fields
    sale_pricelist_id = fields.Many2one('product.pricelist', string='Sale Pricelist', required=True,
                                        help="Pricelist to be used for WooCommerce sales.")
    sale_warehouse_id = fields.Many2one('stock.warehouse', string='Sale Warehouse', required=True,
                                        help="Warehouse to be used for WooCommerce sales.")
    sale_utm_source_id = fields.Many2one('utm.source', string='Sale UTM Source',
                                         help="UTM Source to be used for WooCommerce sales.")
    last_sale_import_date = fields.Datetime(string='Last Sale Import Date', default=fields.Datetime.now)

    sale_mail_sending = fields.Boolean(string='Send Sale Mail', default=True,
                                       help="Send sale mail to customer.")

    def _build_api(self):
        return API(url=self.hostname,
                   consumer_key=self.consumer_key,
                   consumer_secret=self.consumer_secret,
                   wp_api=True,
                   version=self.version,
                   timeout=self.request_timeout)

    @api.model
    def create(self, vals):
        res = super(WooCommerceBackend, self).create(vals)
        if re.match(http_regex, res.hostname) is None:
            raise ValidationError(_('Hostname must be a valid URL. Example: https://www.altinkaya.com.tr'))
        if not res.name:
            res.name = res.hostname.split('://')[-1]
        return res

    def test_woo_connection(self):
        wcapi = self._build_api()
        r = wcapi.get("system_status")
        if r.status_code == 404:
            raise UserError(_("Enter Valid url"))
        val = r.json()
        if "errors" in r.json():
            msg = val["errors"][0]["message"] + "\n" + val["errors"][0]["code"]
            raise UserError(_(msg))
        else:
            raise UserError(_("Test Success"))

    def wp_upload_media(self, payload):
        url = '%s/wp-json/wp/v2/media' % self.hostname
        auth_token = b64encode(('%s:%s' % (self.wp_app_user, self.wp_app_key)).encode('utf-8')).decode('utf-8')
        data = b64decode(payload['data'])
        mimetype = magic.from_buffer(data, mime=True)
        res = requests.post(url=url,
                            data=data,
                            headers={'Authorization': 'Basic %s' % auth_token,
                                     'Content-Type': mimetype,
                                     'Content-Disposition': 'attachment; filename=%s' % payload['filename']})
        if res.status_code == 201:
            return res.json()
        else:
            raise UserError(_('Error: %s' % res.text))

    def wp_read_media(self, media_id):
        url = '%s/wp-json/wp/v2/media/%s' % (self.hostname, media_id)
        auth_token = b64encode(('%s:%s' % (self.wp_app_user, self.wp_app_key)).encode('utf-8')).decode('utf-8')
        res = requests.get(url=url,
                           headers={'Authorization': 'Basic %s' % auth_token})
        if res.status_code == 200:
            return res.json()
        elif res.status_code == 404:
            return {}
        else:
            raise UserError(_('Error: %s' % res.text))

    def wp_update_media(self, media_id):
        pass
        # Todo: implement this

    def wp_delete_media(self, media_id):
        pass
        # Todo: implement this

    def sync_all_categories(self):
        self.env['product.category'].action_sync_to_woocommerce()

    def sync_all_attributes(self):
        self.env['product.attribute'].action_sync_to_woocommerce()

    def sync_all_attribute_values(self):
        self.env['product.attribute.value'].action_sync_to_woocommerce()

    def sync_all_products(self):
        self.env['product.template'].action_sync_to_woocommerce()
