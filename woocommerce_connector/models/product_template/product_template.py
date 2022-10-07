# Copyright 2022 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from .woo_product_template import WooProductTemplate

ONCHANGE_FIELDS = ['name',
                   'description',
                   'list_price',
                   'categ_id',
                   'description',
                   'default_code',
                   'attribute_line_ids',
                   'manage_woo_stock',
                   'image_ids']


class ProductTemplate(models.Model):
    _name = "product.template"
    _inherit = ["product.template", "woocommerce.mapping"]

    manage_woo_stock = fields.Boolean(string='Manage WooCommerce Stock', default=True)

    @api.multi
    def create(self, vals):
        res = super(ProductTemplate, self).create(vals)
        backend = self.env.user.company_id.default_woocommerce_backend_id
        for rec in res:
            if rec.sync_to_woocommerce:
                connector = WooProductTemplate(backend)
                resp = connector.create(rec)
                rec.woocommerce_id = resp['id']
        return res

    @api.multi
    def write(self, vals):
        res = super(ProductTemplate, self).write(vals)
        backend = self.env.user.company_id.default_woocommerce_backend_id
        for rec in self:
            if rec.sync_to_woocommerce and rec.woocommerce_id:
                if any(x in vals for x in ONCHANGE_FIELDS):  # If product name or parent category changed
                    connector = WooProductTemplate(backend)
                    connector.write(rec, vals)
        return res

    def action_sync_to_woocommerce(self):

        unsynced_product_tmpls = self.search([('sync_to_woocommerce', '=', True),
                                              ('woocommerce_id', '=', False)])
        for attr in self.web_progress_iter(unsynced_product_tmpls.sorted(lambda i: i.product_variant_ids, reverse=True),
                                           msg='Ürün şablonları eşleştiriliyor.'):
            attr.action_single_sync_to_woocommerce()

    def action_single_sync_to_woocommerce(self):

        if False in self.attribute_line_ids.mapped('attribute_id.sync_to_woocommerce'):
            raise UserError(_('Please sync all attributes to WooCommerce before syncing this product template.'))

        if self.woocommerce_id:
            raise UserError(_("Product template is already synced: %s") % self.name)

        connector = WooProductTemplate(self.env.user.company_id.default_woocommerce_backend_id)
        resp = connector.create(self)
        self.write({'woocommerce_id': resp['id']})
        self.env.cr.commit()
        self.product_variant_ids.woocommerce_product_variation_sync()
