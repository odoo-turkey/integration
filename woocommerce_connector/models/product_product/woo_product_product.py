from odoo.exceptions import UserError
from odoo.tools import float_is_zero
from odoo import fields, _


class WooProductProduct:
    def __init__(self, connector):
        self.connector = connector

    # HELPERS

    def _get_attributes(self, model):
        attributes = []
        for attr_val in model.attribute_value_ids.filtered(lambda x: x.attribute_id.sync_to_woocommerce):
            attributes.append({
                'id': attr_val.attribute_id.woocommerce_id,
                'option': attr_val.name
            })
        return attributes

    def _get_dimensions(self, model):
        return {
            'length': str(model.product_length) or '',
            'width': str(model.product_width) or '',
            'height': str(model.product_height) or '',
        }

    def _get_product_price(self, model):
        # price_field = self.connector.product_price_type_id.field
        # price = getattr(model, price_field)
        # return str(price) if not float_is_zero(price, 6) else ''
        price_field = getattr(model, self.connector.product_price_type_id.field)
        if not float_is_zero(price_field, 6):
            currency = self.connector.product_price_type_id.currency
            to_currency = model.company_id.currency_id
            price = currency._convert(price_field, to_currency, model.company_id, fields.Date.today(),
                                      round=False)
            return str(price)
        return ''

    def _get_product_weight(self, model):
        return str(model.weight) if not float_is_zero(model.weight, 6) else ''

    # CREATE

    def _get_images(self, model):
        images = []
        for image in model.image_ids:
            if not image.file_db_store:
                continue
            wp_img_path = image.action_single_sync_to_woocommerce()
            images.append({
                'src': wp_img_path,
                'name': image.name,
                'alt': image.name
            })

        return images

    def _prepare_data_for_create(self, model):
        data = {'short_description': model.description or '',
                'sku': model.default_code or '',
                'regular_price': self._get_product_price(model),
                'manage_stock': model.woo_stock_rel,
                'stock_quantity': model.qty_available_not_res or 0,
                'attributes': self._get_attributes(model),
                'weight': self._get_product_weight(model),
                'dimensions': self._get_dimensions(model),
                'images': self._get_images(model),
                }
        return data

    def create(self, model):
        wcapi = self.connector._build_api()
        data = self._prepare_data_for_create(model)
        response = wcapi.post("products/%s/variations" % model.product_tmpl_id.woocommerce_id, data)
        if response.status_code == 201:
            return response.json()
        else:
            raise UserError(_("Error while creating product modelory. %s" % response.text))

    # WRITE

    def _prepare_data_for_write(self, model, vals):
        data = {}
        if 'active' in vals:
            data.update({'status': 'publish' if vals['active'] else 'draft'})

        if self.connector.product_price_type_id.field in vals:
            data.update({'regular_price': self._get_product_price(model)})

        if any(attr in vals for attr in ['product_length', 'product_width', 'product_height']):
            data.update({'dimensions': self._get_dimensions(model)})

        if 'weight' in vals:
            data.update({'weight': self._get_product_weight(model)})

        if 'woo_stock_rel' in vals:
            data.update({'manage_stock': model.woo_stock_rel,
                         'stock_quantity': model.qty_available_not_res or 0})

        if 'woo_stock_qty' in vals:
            data.update({'stock_quantity': model.woo_stock_qty or 0})

        if 'image_ids' in vals:
            data.update({'images': self._get_images(model)})

        return data

    def write(self, model, vals):
        data = self._prepare_data_for_write(model, vals)
        wcapi = self.connector._build_api()
        response = wcapi.put("products/%s/variations/%s" % (model.product_tmpl_id.woocommerce_id,
                                                            model.woocommerce_id), data)
        if response.status_code == 200:
            return response.json()
        else:
            raise UserError(_("Error while updating product. %s" % response.text))
