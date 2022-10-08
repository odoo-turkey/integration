# Copyright 2022 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class WooCommerceMapping(models.AbstractModel):
    _name = "woocommerce.mapping"
    _description = 'Base model for WooCommerce - Odoo integration'

    sync_to_woocommerce = fields.Boolean('Sync to Woocommerce', default=False)
    woocommerce_id = fields.Integer('WooCommerce ID', readonly=True)

    _sql_constraints = [
        (
            'woocommerce_id_uniq',
            'UNIQUE(woocommerce_id)',
            'Only one WooCommerce ID for a record!'
        )
    ]

    # TODO UNLINK ????
    @api.multi
    def unlink(self):
        for rec in self:
            if rec.woocommerce_id:
                raise UserError(_("You can't delete a record which is synced to WooCommerce."))
        return super(WooCommerceMapping, self).unlink()
