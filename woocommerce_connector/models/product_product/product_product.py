# Copyright 2022 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models, api
from .woo_product_product import WooProductProduct

ONCHANGE_FIELDS = [
    'active',
    'attr_price',
    'length',
    'width',
    'height',
    'weight',
    'image_ids',
    # 'woo_stock_rel' # No need. We are syncing stock separately.
    'woo_stock_qty',
]


class ProductProduct(models.Model):
    _name = "product.product"
    _inherit = ["product.product", "woocommerce.mapping"]

    woo_stock_rel = fields.Boolean(string='Manage Stock',
                                   readonly=True, store=True,
                                   compute='_compute_woo_stock_rel')

    woo_stock_qty = fields.Float(string='WooCommerce Stock Quantity',
                                 store=True, readonly=True)

    @api.multi
    def _compute_quantities(self):
        res = super(ProductProduct, self)._compute_quantities()
        backend = self.env['res.company'].browse(1).default_woocommerce_backend_id  # Todo: fix this
        for rec in self:
            if rec.sync_to_woocommerce and rec.woo_stock_rel:
                loc_ids = backend.location_ids.ids
                unreserved_qty = rec.with_context({'location': loc_ids}).qty_available_not_res
                if unreserved_qty != rec.woo_stock_qty:
                    rec.write({'woo_stock_qty': unreserved_qty})
        return res

    @api.multi
    @api.depends('product_tmpl_id.manage_woo_stock')
    def _compute_woo_stock_rel(self):
        backend = self.env.user.company_id.default_woocommerce_backend_id
        for rec in self:
            rec.woo_stock_rel = rec.product_tmpl_id.manage_woo_stock
            if rec.sync_to_woocommerce:
                connector = WooProductProduct(backend)
                connector.write(rec, {'woo_stock_rel': rec.woo_stock_rel})

        return True

    @api.multi
    def create(self, vals):
        res = super(ProductProduct, self).create(vals)
        backend = self.env.user.company_id.default_woocommerce_backend_id
        for rec in res:
            if rec.product_tmpl_id.sync_to_woocommerce:
                connector = WooProductProduct(backend)
                resp = connector.create(rec)
                rec.write({'woocommerce_id': resp['id'],
                           'sync_to_woocommerce': bool(resp['id'])})
        return res

    @api.multi
    def write(self, vals):
        res = super(ProductProduct, self).write(vals)
        backend = self.env.user.company_id.default_woocommerce_backend_id
        checking_fields = ONCHANGE_FIELDS + backend.mapped('product_price_type_id.field')
        for rec in self:
            if rec.sync_to_woocommerce and rec.woocommerce_id:
                if any(x in vals for x in checking_fields):  # If category name or parent category changed
                    connector = WooProductProduct(backend)
                    connector.write(rec, vals)
        return res

    def woocommerce_product_variation_sync(self):
        backend = self.env.user.company_id.default_woocommerce_backend_id
        connector = WooProductProduct(backend)
        products = self.filtered(lambda p: not p.woocommerce_id)
        for product in self.web_progress_iter(
                products.sorted(lambda i: i.sale_qty360days, reverse=True)):  # Sort by last 360 days sale
            if not any(product.attribute_value_ids.filtered(
                    lambda x: not x.attribute_id.sync_to_woocommerce)):  # If all attributes are synced

                resp = connector.create(product)
                product.write({'woocommerce_id': resp['id'],
                               'sync_to_woocommerce': bool(resp['id'])})
                self.env.cr.commit()

    def update_woo_product_price(self):
        backend = self.env.user.company_id.default_woocommerce_backend_id
        connector = WooProductProduct(backend)
        products = self.search([('sync_to_woocommerce', '=', True),
                                ('woocommerce_id', '!=', False)])
        price_field = backend.product_price_type_id.field
        for product in self.web_progress_iter(products):
            connector.write(product, {price_field: 'update'})  # Not a real value. Just to trigger the update.
