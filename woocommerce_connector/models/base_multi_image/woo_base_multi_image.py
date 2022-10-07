from unicode_tr.extras import slugify
from odoo.exceptions import UserError
from odoo import _


class WooBaseMultiImage:
    def __init__(self, connector):
        self.connector = connector

    # CREATE

    def _prepare_data_for_create(self, model):
        upload_dict = {
            'data': model.file_db_store,
            'filename': "%s.%s" % (slugify(model.name), model.filename.split('.')[1])
        }
        return upload_dict

    def create(self, model):
        data = self._prepare_data_for_create(model)
        return self.connector.wp_upload_media(data)

    # WRITE

    # def _prepare_data_for_write(self, vals):
    #     data = {}
    #     if 'name' in vals:
    #         data.update({'name': vals['name'],
    #                      'slug': slugify(vals['name'])})
    #
    #     return data
    #
    # def write(self, model, vals):
    #     data = self._prepare_data_for_write(vals)
    #     wcapi = self.connector._build_api()
    #     response = wcapi.put("products/attributes/%s" % model.woocommerce_id, data)
    #     if response.status_code == 200:
    #         return response.json()
    #     else:
    #         raise UserError(_("Error while updating product attribute. %s" % response.text))

    # READ

    def read(self, model):
        res = self.connector.wp_read_media(model.woocommerce_id)

        if not res:  # if not found, create a new one. This is for the case when the image is deleted from woocommerce.
            return self.create(model)

        return res or {}
