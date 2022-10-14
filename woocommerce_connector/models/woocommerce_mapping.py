# Copyright 2022 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class WooCommerceMapping(models.AbstractModel):
    _name = "woocommerce.mapping"
    _description = 'Base model for WooCommerce - Odoo integration'

    sync_to_woocommerce = fields.Boolean('Sync to Woocommerce', default=False, copy=False)
    woocommerce_id = fields.Integer('WooCommerce ID', readonly=True, copy=False)

    @api.multi
    @api.constrains('woocommerce_id')
    def _check_woocommerce_id(self):
        for rec in self:
            model = self.env[rec._name].search([('woocommerce_id', '=', rec.woocommerce_id),
                                                ('id', '!=', rec.id)])
            if model:
                raise UserError(_("Only one WooCommerce ID for a record!"))
        return True

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.woocommerce_id and rec.sync_to_woocommerce:
                raise UserError(_("You can't delete a record which is synced to WooCommerce."))
        return super(WooCommerceMapping, self).unlink()

    @api.multi
    def write(self, vals):
        """
        This method is used to delete WooCommerce record when Odoo
        record is unchecked from sync_to_woocommerce field.
        Universal method for all models.
        :param vals:
        :return:
        """
        for rec in self:
            if 'sync_to_woocommerce' in vals and not vals['sync_to_woocommerce'] and rec.woocommerce_id:
                rec.woocommerce_unlink()
        return super(WooCommerceMapping, self).write(vals)
