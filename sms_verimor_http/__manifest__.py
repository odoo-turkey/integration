# Copyright 2022 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sms Verimor HTTP",
    "summary": "Send sms using Verimor http API",
    "version": "12.0.1.0.0",
    "category": "SMS",
    "website": "https://github.com/odoo-turkey",
    "author": "Yiğit Budak, Odoo Turkey Localization Group",
    "maintainers": ["yibudak"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {"python": [], "bin": []},
    "depends": ["base_phone", "sms", "iap_alternative_provider"],
    "data": ["views/iap_account_view.xml"],
}
