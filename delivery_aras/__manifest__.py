# Copyright 2024 Ahmet Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Delivery Aras",
    "summary": "Delivery Carrier implementation for Aras Kargo API",
    "version": "12.0.1.1.0",
    "category": "Stock",
    "website": "https://github.com/odoo-turkey",
    "author": "Yiğit Budak, Odoo Turkey Localization Group",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["delivery_integration_base"],
    "external_dependencies": {"python": ["phonenumbers", "zeep"]},
    "data": [
        "views/delivery_aras_view.xml",
        'report/aras_carrier_label.xml',
        'report/aras_sms_template.xml',
        'report/reports.xml',

    ],
}
