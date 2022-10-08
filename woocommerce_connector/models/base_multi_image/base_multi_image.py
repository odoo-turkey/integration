# Copyright 2022 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from .woo_base_multi_image import WooBaseMultiImage

ALLOWED_FIELDS = ['woocommerce_id', 'sync_to_woocommerce']


class BaseMultiImageImage(models.Model):
    woocommerce_id: fields.Integer
    _name = "base_multi_image.image"
    _inherit = ["base_multi_image.image", "woocommerce.mapping"]

    @api.multi
    def create(self, vals):
        res = super(BaseMultiImageImage, self).create(vals)
        backend = self.env['res.company'].browse(1).default_woocommerce_backend_id
        for rec in res:
            if rec.owner_ref_id.sync_to_woocommerce:
                connector = WooBaseMultiImage(backend)
                resp = connector.create(rec)
                rec.write({'woocommerce_id': resp['id'],
                           'sync_to_woocommerce': True})
        return res

    @api.multi
    def write(self, vals):
        if len(vals) == 2 and ALLOWED_FIELDS == list(vals.keys()):
            return super(BaseMultiImageImage, self).write(vals)
        else:
            raise UserError(_("You can't update image for synced products!"
                              " Instead, you can delete and create new one."))
        # Todo: Implement this
        # res = super(BaseMultiImageImage, self).write(vals)
        # for rec in self:
        #     if rec.woocommerce_backend_id and rec.sync_to_woocommerce and rec.woocommerce_id:
        #         if any(x in vals for x in ONCHANGE_FIELDS):  # If attribute name changed
        #             connector = WooBaseMultiImage(rec.woocommerce_backend_id)
        #             connector.write(rec, vals)
        # return res

    def action_single_sync_to_woocommerce(self):
        backend = self.env['res.company'].browse(1).default_woocommerce_backend_id
        connector = WooBaseMultiImage(backend)
        if self.woocommerce_id:
            resp = connector.read(self)
        else:
            resp = connector.create(self)
            self.write({'woocommerce_id': resp['id'],
                        'sync_to_woocommerce': True})
        self.env.cr.commit()
        return resp.get('source_url', '')  # Return image url, maybe we can return other fields too
