# Copyright 2022 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, api, _
from odoo.exceptions import UserError
from .woo_product_attribute import WooProductAttribute


class ProductAttribute(models.Model):
    _name = "product.attribute"
    _inherit = ["product.attribute", "woocommerce.mapping"]

    @api.model
    def create(self, vals):
        res = super(ProductAttribute, self).create(vals)
        backend = self.env.user.company_id.default_woocommerce_backend_id
        for rec in res:
            if rec.sync_to_woocommerce:
                connector = WooProductAttribute(backend)
                resp = connector.create(rec)
                rec.woocommerce_id = resp['id']
        return res

    @api.multi
    def write(self, vals):
        res = super(ProductAttribute, self).write(vals)
        backend = self.env.user.company_id.default_woocommerce_backend_id
        for rec in self:
            if rec.sync_to_woocommerce and rec.woocommerce_id:
                if 'name' in vals:  # If attribute name changed
                    connector = WooProductAttribute(backend)
                    connector.write(rec, vals)
        return res

    def action_sync_to_woocommerce(self):
        unsynced_attrs = self.search([('sync_to_woocommerce', '=', True),
                                      ('woocommerce_id', '=', False)])
        for attr in self.web_progress_iter(unsynced_attrs, msg='Nitelikler eşleştiriliyor.'):
            attr.action_single_sync_to_woocommerce()

    def action_single_sync_to_woocommerce(self):
        if self.woocommerce_id:
            raise UserError(_("Attribute is already synced: %s") % self.name)

        connector = WooProductAttribute(self.env.user.company_id.default_woocommerce_backend_id)
        resp = connector.create(self)
        self.write({'woocommerce_id': resp['id']})
        self.env.cr.commit()

    def _check_before_woo_unlink(self):
        exception_msg = ''
        for product in self.attribute_line_ids.mapped('product_tmpl_id'):
            if product.sync_to_woocommerce:
                exception_msg += '%s\n' % product.name
        if exception_msg:
            raise UserError(_("You cannot delete synced attributes."
                              " Following products are synced:\n%s") % exception_msg)

    def woocommerce_unlink(self):
        self._check_before_woo_unlink()
        backend = self.env.user.company_id.default_woocommerce_backend_id
        connector = WooProductAttribute(backend)
        connector.delete(self)
        self.write({'woocommerce_id': False})
        self.env.cr.commit()
