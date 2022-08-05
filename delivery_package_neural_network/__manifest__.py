# Copyright 2022 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Delivery Package Neural Network",
    "summary": "Package dimension and weight prediction with neural network.",
    "version": "12.0.1.0.0",
    "category": "Stock",
    "website": "https://github.com/odoo-turkey",
    "author": "Yiğit Budak, Mustafa Kağan Çuhadar",
    "maintainers": ["yibudak", "Mkaganc"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {"python": [
        "tensorflow", "keras", "numpy", "pandas", "matplotlib"
    ], "bin": []},
    "depends": ["delivery_integration_base"],
    "data": ["views/delivery_nn_view.xml"],
}
