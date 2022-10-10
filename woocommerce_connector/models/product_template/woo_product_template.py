from unicode_tr.extras import slugify
from odoo.exceptions import UserError
from odoo import _


class WooProductTemplate:
    def __init__(self, connector):
        self.connector = connector

    # HELPERS

    def _get_attributes(self, model):
        attributes = []
        for idx, attr_val in enumerate(model.attribute_line_ids.filtered(lambda x: x.attribute_id.sync_to_woocommerce)):
            options = attr_val.value_ids.mapped('name')
            attributes.append({
                'id': attr_val.attribute_id.woocommerce_id,
                'name': attr_val.attribute_id.name,
                'position': idx,
                'visible': True if len(options) < 10 else False,
                'variation': True,
                'options': options
            })
        return attributes

    def _get_default_attributes(self, model):
        attributes = []
        for attr_val in model.product_variant_id.attribute_value_ids.filtered(lambda x:
                                                                              x.attribute_id.sync_to_woocommerce):
            attributes.append({
                'id': attr_val.attribute_id.woocommerce_id,
                # 'name': attr_val.attribute_id.name,
                'option': attr_val.name
                # attr_val.filtered(lambda a: a.attribute_id.id == attr_val.attribute_id.id).mapped('woocommerce_id')
            })
        return attributes

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

    def _get_product_categ(self, model):
        if not model.categ_id.woocommerce_id:
            raise UserError(_('Category %s is not synced to WooCommerce' % model.categ_id.name))
        return model.categ_id.woocommerce_id

    # CREATE

    def _prepare_data_for_create(self, model):
        data = {'name': model.name,
                'slug': slugify(model.name),
                'type': 'variable',
                'status': 'publish',
                'short_description': model.description or '',
                # 'sku': self._get_sku(model),
                'regular_price': model.list_price or '',
                'virtual': True,
                'tax_status': 'taxable',
                'manage_stock': model.manage_woo_stock,
                'stock_quantity': model.qty_available_not_res or 0,
                'categories': [{'id': self._get_product_categ(model)}],
                'attributes': self._get_attributes(model),
                'default_attributes': self._get_default_attributes(model),
                'images': self._get_images(model)
                }
        return data

    def create(self, model):
        wcapi = self.connector._build_api()
        data = self._prepare_data_for_create(model)
        response = wcapi.post("products", data)
        if response.status_code == 201:
            return response.json()
        else:
            raise UserError(_("Error while creating product template. %s" % response.text))

    # WRITE

    def _prepare_data_for_write(self, model, vals):
        data = {}
        if 'name' in vals:
            data.update({'name': vals['name'],
                         'slug': slugify(vals['name'])})

        if 'description' in vals:
            data.update({'short_description': vals['description']})

        if 'default_code' in vals:
            data.update({'sku': vals['default_code']})

        if 'list_price' in vals:
            data.update({'regular_price': vals['list_price']})

        if 'categ_id' in vals:
            data.update({'categories': [{'id': model.categ_id.woocommerce_id}]})

        if 'attribute_line_ids' in vals:
            data.update({'attributes': self._get_attributes(model),
                         'default_attributes': self._get_default_attributes(model)})

        if 'manage_woo_stock' in vals:
            data.update({'manage_stock': vals['manage_woo_stock'],
                         'stock_quantity': model.qty_available_not_res or 0})

        if 'image_ids' in vals:
            data.update({'images': self._get_images(model)})

        return data

    def write(self, model, vals):
        data = self._prepare_data_for_write(model, vals)
        wcapi = self.connector._build_api()
        response = wcapi.put("products/%s" % model.woocommerce_id, data)
        if response.status_code == 200:
            return response.json()
        else:
            raise UserError(_("Error while updating product category. %s" % response.text))
