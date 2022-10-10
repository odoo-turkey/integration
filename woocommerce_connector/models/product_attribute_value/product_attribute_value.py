# Copyright 2022 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, api, _
from odoo.exceptions import UserError
from .woo_product_attribute_value import WooProductAttributeValue


class ProductAttributeValue(models.Model):
    _name = "product.attribute.value"
    _inherit = ["product.attribute.value", "woocommerce.mapping"]

    @api.multi
    def create(self, vals):
        res = super(ProductAttributeValue, self).create(vals)
        backend = self.env.user.company_id.default_woocommerce_backend_id
        for rec in res:
            if rec.attribute_id.sync_to_woocommerce:  # if attribute is synced
                connector = WooProductAttributeValue(backend)
                resp = connector.create(rec)
                rec.write({'woocommerce_id': resp['id'],
                           'sync_to_woocommerce': True})
        return res

    @api.multi
    def write(self, vals):
        res = super(ProductAttributeValue, self).write(vals)
        backend = self.env.user.company_id.default_woocommerce_backend_id
        for rec in self:
            if rec.sync_to_woocommerce and rec.woocommerce_id:
                if 'name' in vals:  # If attribute name changed
                    connector = WooProductAttributeValue(backend)
                    connector.write(rec, vals)
        return res

    def action_sync_to_woocommerce(self):

        unsynced_attribute_values = self.search([('attribute_id.sync_to_woocommerce', '=', True),
                                                 ('woocommerce_id', '=', False)])
        for attr_val in self.web_progress_iter(unsynced_attribute_values, msg='Nitelik değerleri eşleştiriliyor.'):
            attr_val.action_single_sync_to_woocommerce()

    def action_single_sync_to_woocommerce(self):

        if self.attribute_id and not (self.attribute_id.woocommerce_id and self.attribute_id.sync_to_woocommerce):
            raise UserError(_("Parent attribute must be synced first: %s") % self.attribute_id.name)

        if self.woocommerce_id:
            raise UserError(_("Attribute value is already synced: %s") % self.name)

        connector = WooProductAttributeValue(self.env.user.company_id.default_woocommerce_backend_id)
        resp = connector.create(self)
        self.write({'woocommerce_id': resp['id'],
                    'sync_to_woocommerce': True})
        self.env.cr.commit()
