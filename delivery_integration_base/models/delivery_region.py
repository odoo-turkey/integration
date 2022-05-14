# Copyright 2022 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import models, fields, api


class DeliveryRegion(models.Model):
    _name = 'delivery.region'
    _description = 'Delivery regions for price calculation'
    name = fields.Char(string='Region Name', required=True)
    country_ids = fields.Many2many('res.country', string='Country', required=True)
    state_ids = fields.Many2many('res.country.state', 'region_id', string='States')
    carrier_ids = fields.Many2many('delivery.carrier', string='Carrier')
