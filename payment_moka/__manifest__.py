# Copyright 2022 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Payment Provider: Moka',
    'version': '16.0.0.1.0',
    'category': 'Accounting/Payment Providers',
    'license': 'LGPL-3',
    'website': 'https://github.com/odoo-turkey',
    'author': 'Yigit Budak',
    'sequence': 350,
    'summary': "MOKA offers payment solutions approved by all"
               " global card payment companies such as Visa and"
               " MasterCard and developed in accordance with the"
               " highest security standards.",
    'depends': ['payment'],
    'data': [
        'views/payment_moka_templates.xml',
        'views/payment_provider_views.xml',
        'data/payment_provider_data.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'payment_moka/static/src/js/payment_form.js',
        ],
    },
    'application': True,
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
}
