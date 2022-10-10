# Copyright 2022 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from unicode_tr.extras import slugify
from odoo.exceptions import UserError
from odoo import _


class WooResPartner:
    def __init__(self, connector):
        self.connector = connector

    # HELPERS

    def get_customer(self, woo_id):
        wcapi = self.connector._build_api()
        response = wcapi.get("customers/%s" % woo_id)
        if response.status_code == 200:
            return response.json()
        else:
            raise UserError(_("Error while updating product category. %s" % response.text))

    # def _get_attributes(self, model):
    #     attributes = []
    #     for idx, attr_val in enumerate(model.attribute_line_ids.filtered(lambda x: x.attribute_id.sync_to_woocommerce)):
    #         attributes.append({
    #             'id': attr_val.attribute_id.woocommerce_id,
    #             'name': attr_val.attribute_id.name,
    #             'position': idx,
    #             'visible': True,
    #             'variation': True,
    #             'options': attr_val.value_ids.mapped('name')
    #         })
    #     return attributes
    #
    # def _get_default_attributes(self, model):
    #     attributes = []
    #     for attr_val in model.product_variant_id.attribute_value_ids.filtered(lambda x:
    #                                                                           x.attribute_id.sync_to_woocommerce):
    #         attributes.append({
    #             'id': attr_val.attribute_id.woocommerce_id,
    #             # 'name': attr_val.attribute_id.name,
    #             'option': attr_val.name
    #             # attr_val.filtered(lambda a: a.attribute_id.id == attr_val.attribute_id.id).mapped('woocommerce_id')
    #         })
    #     return attributes
    #
    # # CREATE
    #
    # def _prepare_data_for_create(self, model):
    #     data = {'name': model.name,
    #             'slug': slugify(model.name),
    #             'type': 'variable',
    #             'status': 'publish',
    #             'short_description': model.description or '',
    #             'sku': model.default_code or '',
    #             'regular_price': model.list_price or '',
    #             'virtual': True,
    #             'tax_status': 'taxable',
    #             'manage_stock': model.manage_woo_stock,
    #             'stock_quantity': model.qty_available_not_res or 0,
    #             'categories': [{'id': model.categ_id.woocommerce_id}],
    #             'attributes': self._get_attributes(model),
    #             'default_attributes': self._get_default_attributes(model),
    #             }
    #     return data
    #
    # def create(self, model):
    #     wcapi = self.connector._build_api()
    #     data = self._prepare_data_for_create(model)
    #     response = wcapi.post("products", data)
    #     if response.status_code == 201:
    #         return response.json()
    #     else:
    #         raise UserError(_("Error while creating partner. %s" % response.text))
    #
    # # WRITE
    #
    # def _prepare_data_for_write(self, model, vals):
    #     data = {}
    #     if 'name' in vals:
    #         data.update({'name': vals['name'],
    #                      'slug': slugify(vals['name'])})
    #
    #     if 'description' in vals:
    #         data.update({'short_description': vals['description']})
    #
    #     if 'default_code' in vals:
    #         data.update({'sku': vals['default_code']})
    #
    #     if 'list_price' in vals:
    #         data.update({'regular_price': vals['list_price']})
    #
    #     if 'categ_id' in vals:
    #         data.update({'categories': [{'id': model.categ_id.woocommerce_id}]})
    #
    #     if 'attribute_line_ids' in vals:
    #         data.update({'attributes': self._get_attributes(model),
    #                      'default_attributes': self._get_default_attributes(model)})
    #
    #     if 'manage_woo_stock' in vals:
    #         data.update({'manage_stock': vals['manage_woo_stock'],
    #                      'stock_quantity': model.qty_available_not_res or 0})
    #
    #     return data
    #
    # def write(self, model, vals):
    #     data = self._prepare_data_for_write(model, vals)
    #     wcapi = self.connector._build_api()
    #     response = wcapi.put("products/%s" % model.woocommerce_id, data)
    #     if response.status_code == 200:
    #         return response.json()
    #     else:
    #         raise UserError(_("Error while updating product category. %s" % response.text))
