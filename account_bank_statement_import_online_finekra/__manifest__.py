# Copyright 2022 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Online Bank Statements: Finekra",
    "version": "12.0.1.1.0",
    "category": "Account",
    "website": "https://github.com/odoo-turkey/integration",
    "author": "Yiğit Budak, Odoo Turkey Localization Group",
    "license": "AGPL-3",
    "installable": True,
    "depends": ["account_bank_statement_import_online", "sale", "sale_confirm_payment"],
    "data": [
        "view/online_bank_statement_provider.xml",
        "view/account_journal.xml",
        "view/account_bank_statement_view.xml",
    ],
}
