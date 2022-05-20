# Copyright 2022 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Delivery Yurtici",
    "summary": "Delivery Carrier implementation for Yurtiçi Kargo API",
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
        "views/delivery_yurtici_view.xml",
        'report/yurtici_carrier_label.xml',
        'report/reports.xml',
    ],
}
