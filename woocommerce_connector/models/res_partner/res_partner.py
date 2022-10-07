# Copyright 2022 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models, api
from odoo.osv import expression
from .woo_res_partner import WooResPartner
import hashlib


# ONCHANGE_FIELDS = ['name',
#                    'parent_id',
#                    'manage_woo_stock']


class ResPartner(models.Model):
    _name = "res.partner"
    _inherit = ["res.partner", "woocommerce.mapping"]

    woo_address_unique_hash = fields.Char('Address Unique Hash', readonly=True)

    # @api.multi
    # def create(self, vals):
    #     res = super(ProductTemplate, self).create(vals)
    #     for rec in res:
    #         if rec.sync_to_woocommerce and rec.woocommerce_backend_id:
    #             connector = WooProductTemplate(rec.woocommerce_backend_id)
    #             resp = connector.create(rec)
    #             rec.woocommerce_id = resp['id']
    #     return res
    #
    # @api.multi
    # def write(self, vals):
    #     res = super(ProductTemplate, self).write(vals)
    #     for rec in self:
    #         if rec.woocommerce_backend_id and rec.sync_to_woocommerce and rec.woocommerce_id:
    #             if any(x in vals for x in ONCHANGE_FIELDS):  # If category name or parent category changed
    #                 connector = WooProductTemplate(rec.woocommerce_backend_id)
    #                 connector.write(rec, vals)
    #     return res

    def _get_vat_field(self, meta):
        meta_dict = {}
        for field in meta:
            meta_dict.update({field.get('key'): field.get('value')})

        return meta_dict.get('billing_vergi_no') or meta_dict.get('billing_tc') or False

    def _get_partner_name(self, vals):
        first_name = vals.get('first_name')
        last_name = vals.get('last_name')
        company_name = vals.get('company')

        if company_name:
            return company_name
        elif first_name != '' and last_name != '':  # Check if the partner has defined first and last name
            return vals.get('first_name') + ' ' + vals.get('last_name')
        else:
            return ''

    def _get_partner_region(self, city):
        region = self.env['address.region'].search([('name', '=', city)], limit=1)
        return region.id

    def _get_partner_country(self, country_code):
        country = self.env['res.country'].search([('code', '=', country_code)], limit=1)
        return country.id

    def _get_partner_state(self, vals):
        country_code = vals.get('country')
        state_code = vals.get('state').lstrip(country_code)
        state = self.env['res.country.state'].search([('code', '=', state_code)], limit=1)
        return state.id

    def _compute_woo_address_unique_hash(self, res):
        long_string = ",".join(val for val in res.values())
        return hashlib.md5(long_string.encode()).hexdigest()

    def _create_woo_partner(self, vals, meta_fields):
        res = {'woocommerce_id': vals.get('id'),
               'sync_to_woocommerce': True,
               'email': vals.get('email', ),
               'name': self._get_partner_name(vals)}

        res.update(self._create_woo_address(address_dict=vals.get('billing'),
                                            parent_id=False,
                                            meta_fields=meta_fields))

        return self.create(res)

    def _create_woo_address(self, address_dict, parent_id=None, meta_fields=None, address_type=None):
        res = {'street': address_dict.get('address_1'),
               'street2': address_dict.get('address_2'),
               'zip': address_dict.get('postcode'),
               'country_id': self._get_partner_country(address_dict.get('country')),
               'state_id': self._get_partner_state(address_dict),
               'region_id': self._get_partner_region(address_dict.get('city')),
               'phone': address_dict.get('phone'),
               'woo_address_unique_hash': self._compute_woo_address_unique_hash(address_dict),
               'name': self._get_partner_name(address_dict)}

        if meta_fields:
            res.update({'vat': self._get_vat_field(meta_fields)})

        if parent_id:
            name = "%s - %s" % (self._get_partner_name(address_dict),
                                'Fatura Adresi' if address_type == 'billing' else 'Teslimat Adresi')
            res.update({'parent_id': parent_id,
                        'name': name})

        return res

    def _check_woo_parent_exist(self, vals):
        domain = [('woocommerce_id', '=', vals.get('id')), ('parent_id', '=', False),
                  ('email', '=', vals.get('email'))]
        meta_fields = vals.get('meta_data')
        vat = self._get_vat_field(meta_fields)
        if vat:
            domain = expression.OR([domain, [('vat', '=', vat)]])
        partner = self.search(domain, limit=1)
        return partner

    def _match_hashed_address(self, address_dict, parent):
        address_hash = self._compute_woo_address_unique_hash(address_dict)
        partner = False
        if address_hash == parent.woo_address_unique_hash:
            partner = parent
        else:
            for child in parent.child_ids:
                if address_hash == child.woo_address_unique_hash:
                    partner = child
                    break
        return partner

    def _search_woo_partner(self, woo_id, backend):
        connector = WooResPartner(backend)
        woo_partner = connector.get_customer(woo_id)
        parent = self._check_woo_parent_exist(woo_partner)
        meta_fields = woo_partner.get('meta_data')
        billing_fields = woo_partner.get('billing')
        shipping_fields = woo_partner.get('shipping')

        # BILLING ADDRESS
        if parent:
            hash_matched_partner = self._match_hashed_address(billing_fields, parent)
            billing_partner = hash_matched_partner
            if not billing_partner:
                vals = self._create_woo_address(address_dict=billing_fields,
                                                parent_id=parent.id,
                                                meta_fields=meta_fields,
                                                address_type='billing')
                billing_partner = self.create(vals)
        else:
            billing_partner = parent = self._create_woo_partner(woo_partner, meta_fields)

        # SHIPPING ADDRESS
        if shipping_fields:
            hash_matched_partner = self._match_hashed_address(shipping_fields, parent)
            shipping_partner = hash_matched_partner
            if not shipping_partner:
                vals = self._create_woo_address(address_dict=shipping_fields,
                                                parent_id=parent.id,
                                                meta_fields=meta_fields,
                                                address_type='shipping')
                shipping_partner = self.create(vals)
        else:
            shipping_partner = billing_partner

        return billing_partner, shipping_partner
