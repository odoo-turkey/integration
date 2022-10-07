from unicode_tr.extras import slugify
from odoo.exceptions import UserError
from odoo import _


class WooProductAttributeValue:
    def __init__(self, connector):
        self.connector = connector

    # CREATE

    def _prepare_data_for_create(self, model):
        data = {'name': model.name,
                'slug': slugify(model.name),
                }
        return data

    def create(self, model):
        wcapi = self.connector._build_api()
        data = self._prepare_data_for_create(model)
        response = wcapi.post("products/attributes/%s/terms" % model.attribute_id.woocommerce_id, data)
        if response.status_code == 201:
            return response.json()
        else:
            raise UserError(_("Error while creating product attribute value. %s" % response.text))

    # WRITE

    def _prepare_data_for_write(self, vals):
        data = {}
        if 'name' in vals:
            data.update({'name': vals['name'],
                         'slug': slugify(vals['name'])})

        return data

    def write(self, model, vals):
        data = self._prepare_data_for_write(vals)
        wcapi = self.connector._build_api()
        response = wcapi.put("products/attributes/%s/terms/%s" % (model.attribute_id.woocommerce_id,
                                                                  model.woocommerce_id), data)
        if response.status_code == 200:
            return response.json()
        else:
            raise UserError(_("Error while updating product attribute value. %s" % response.text))
