# Copyright 2022 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Delivery Integration Base Module',
    'summary': 'Provides fields to be able to use integration modules.',
    'author': 'Yiğit Budak, Odoo Turkey Localization Group',
    'website': 'https://github.com/odoo-turkey/integration',
    'license': 'AGPL-3',
    'category': 'Delivery',
    'version': '12.0.1.1.0',
    'depends': [
        "delivery", "l10n_tr_address", "delivery_state", "product_dimension",
        "queue_job", "sms_verimor_http", "short_url_yourls"
    ],
    'data': [
        'views/stock_picking_views.xml',
        'views/delivery_carrier_views.xml',
        'views/delivery_price_rule_views.xml',
        'wizards/sale_get_rates_wizard_views.xml',
        'views/sale_order_views.xml',
        'views/delivery_region_views.xml',
    ],
    'installable': True,
}
