# Copyright 2022 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Garanti Payment Acquirer",
    "version": "12.0.0.1.0",
    "category": "Accounting",
    "license": "LGPL-3",
    "website": "https://github.com/odoo-turkey",
    "author": "Yigit Budak",
    "sequence": 350,
    "summary": "Garanti BBVA Sanal POS, internet üzerinden yapılan satışlarda"
    " kredi kartı ile ödeme alınabilmesi için oluşturulan güvenli"
    " bir ödeme çözümüdür.",
    "depends": ["sale", "payment"],
    "external_dependencies": {"python": ["lxml", "bs4"]},
    "data": [
        "views/payment_transaction_views.xml",
        "views/assets.xml",
        "views/payment_garanti_templates.xml",
        "views/payment_views.xml",
        "templates/result_page.xml",
        "data/payment_acquirer_data.xml",
    ],
    "application": True,
    "post_init_hook": "create_missing_journal_for_acquirers",
    "uninstall_hook": "uninstall_hook",
}
