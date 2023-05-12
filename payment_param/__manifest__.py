# Copyright 2022 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Payment Provider: Param",
    "version": "16.0.0.1.0",
    "category": "Accounting/Payment Providers",
    "license": "LGPL-3",
    "website": "https://github.com/odoo-turkey",
    "author": "Yigit Budak",
    "sequence": 350,
    "summary": "ParamPOS is an online collection system that"
               " enables payments to be received through"
               " Virtual POS without the need to make"
               " individual agreements with banks.",
    "depends": ["payment"],
    "external_dependencies": {"python": ["phonenumbers", "zeep"]},
    "data": [
        "views/payment_param_templates.xml",
        "views/payment_provider_views.xml",
        "data/payment_provider_data.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "payment_param/static/src/js/payment_form.js",
        ],
    },
    "application": True,
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "uninstall_hook",
}
