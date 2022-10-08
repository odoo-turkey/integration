from unicode_tr.extras import slugify
from odoo.exceptions import UserError
from odoo import _


class WooProductCategory:
    def __init__(self, connector):
        self.connector = connector

    # CREATE

    def _prepare_data_for_create(self, categ):
        data = {'name': categ.name,
                'slug': slugify(categ.name),
                'display': 'default'
                }
        if categ.parent_id:
            data.update({
                'parent': categ.parent_id.woocommerce_id,
                'display': 'subcategories'
            })
        return data

    def create(self, model):
        wcapi = self.connector._build_api()
        data = self._prepare_data_for_create(model)
        response = wcapi.post("products/categories", data)
        if response.status_code == 201:
            return response.json()
        else:
            raise UserError(_("Error while creating product modelory. %s" % response.text))

    # WRITE

    def _prepare_data_for_write(self, model, vals):
        data = {}
        if 'name' in vals:
            data.update({'name': vals['name'],
                         'slug': slugify(vals['name'])})

        if 'parent_id' in vals:
            data.update({'parent': model.browse(vals['parent_id']).woocommerce_id})

        return data

    def write(self, model, vals):
        data = self._prepare_data_for_write(model, vals)
        wcapi = self.connector._build_api()
        response = wcapi.put("products/categories/%s" % model.woocommerce_id, data)
        if response.status_code == 200:
            return response.json()
        else:
            raise UserError(_("Error while updating product category. %s" % response.text))

    def disable(self, model):
        wcapi = self.connector._build_api()
        response = wcapi.delete("products/categories/%s" % model.woocommerce_id)
        if response.status_code == 200:
            return response.json()
        else:
            raise UserError(_("Error while deleting product category. %s" % response.text))
