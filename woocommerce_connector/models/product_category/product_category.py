# Copyright 2022 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, api, _
from odoo.exceptions import UserError
from .woo_product_category import WooProductCategory

ONCHANGE_FIELDS = ['name',
                   'parent_id']


class ProductCategory(models.Model):
    _name = "product.category"
    _inherit = ["product.category", "woocommerce.mapping"]

    @api.multi
    def create(self, vals):
        res = super(ProductCategory, self).create(vals)
        backend = self.env.user.company_id.default_woocommerce_backend_id
        for rec in res:
            if rec.sync_to_woocommerce:
                connector = WooProductCategory(backend)
                resp = connector.create(rec)
                rec.woocommerce_id = resp['id']
        return res

    @api.multi
    def write(self, vals):
        res = super(ProductCategory, self).write(vals)
        backend = self.env.user.company_id.default_woocommerce_backend_id
        connector = WooProductCategory(backend)
        for rec in self.filtered(lambda i: i.woocommerce_id):
            if rec.sync_to_woocommerce and any(
                    x in vals for x in ONCHANGE_FIELDS):  # If category name or parent category changed
                connector.write(rec, vals)
            # if not rec.sync_to_woocommerce:
            #     raise UserError(_("This category is synced with WooCommerce: %s."
            #                       " Contact with your administrator.") % rec.name)
        return res

    def action_sync_to_woocommerce(self):

        unsynced_categs = self.search([('sync_to_woocommerce', '=', True),
                                       ('woocommerce_id', '=', False)])
        for categ in self.web_progress_iter(unsynced_categs.sorted(lambda i: i.child_id, reverse=True),
                                            msg='Kategoriler eşleştiriliyor.'):  # Create parent categories first
            categ.action_single_sync_to_woocommerce()

    def action_single_sync_to_woocommerce(self):
        if self.parent_id and not (self.parent_id.woocommerce_id and self.parent_id.sync_to_woocommerce):
            raise UserError(_("Parent category must be synced first: %s") % self.parent_id.name)

        if self.woocommerce_id:
            raise UserError(_("Category is already synced: %s") % self.name)

        connector = WooProductCategory(self.env.user.company_id.default_woocommerce_backend_id)
        resp = connector.create(self)
        self.write({'woocommerce_id': resp['id']})
        self.env.cr.commit()

    def _check_before_woo_unlink(self):
        exception_msg = ''
        for child_categ in self.child_id:
            if child_categ.sync_to_woocommerce:
                exception_msg += "%s\n" % child_categ.name
        if exception_msg:
            raise UserError(_("You can't delete a category which has synced child categories:\n%s") % exception_msg)

        product_tmpls = self.env['product.template'].search([('categ_id', '=', self.id),
                                                             ('sync_to_woocommerce', '=', True)])
        for product_tmpl in product_tmpls:
            exception_msg += "%s\n" % product_tmpl.name

        if exception_msg:
            raise UserError(_("You can't delete a category which has synced products:\n%s") % exception_msg)

    def woocommerce_unlink(self):
        self._check_before_woo_unlink()
        backend = self.env.user.company_id.default_woocommerce_backend_id
        connector = WooProductCategory(backend)
        connector.delete(self)
        self.write({'woocommerce_id': False})
        self.env.cr.commit()
