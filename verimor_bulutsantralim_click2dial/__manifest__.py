# Copyright 2022 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Verimor Bulutsantralim Connector',
    'version': '12.0.1.0.2',
    'category': 'Phone',
    'license': 'AGPL-3',
    'summary': 'Verimor Bulutsantralim Odoo Connector',
    'description': """
Verimor connector
==========================

""",
    'author': "Yiğit Budak, Odoo Turkey Localization Group",
    'website': 'https://github.com/odoo-turkey',
    'depends': ['base', 'crm', 'base_phone'],
    'external_dependencies': {'python': ['phonenumbers']},
    'data': [
        'views/bulutsantralim_connector_view.xml',
        'views/res_users_view.xml',
        'views/web_bulutsantralim_click2dial.xml',
        'views/res_company_view.xml',
        ],
    'qweb': ['static/src/xml/bulutsantralim_click2dial.xml'],
    'application': True,
    'installable': True,
}
