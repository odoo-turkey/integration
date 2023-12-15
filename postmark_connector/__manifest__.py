# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Postmark Connector",
    "version": "16.0.0.1.0",
    # "category": "Accounting",
    "license": "LGPL-3",
    "website": "https://github.com/odoo-turkey",
    "author": "Samet Altuntaş",
    "sequence": -100,
    "summary": "",
    "depends": ["mail", "sale"],
    "external_dependencies": {"python": ["postmarker"]},
    "data": ["views/assets.xml", "views/ir_mail_server_view.xml"],
    # "assets": {
    #     "web.assets_backend": ["/postmark_connector/static/src/js/postmark_chatter.js",
    #                            "/postmark_connector/static/src/xml/postmark_mail_state.xml"],
    # },
}
