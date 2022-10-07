# Copyright 2022 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'WooCommerce Connector',
    'summary': 'Export and sync your products, customers, sales, invoices with WooCommerce.',
    'version': '12.0.1.0.1',
    'development_status': 'Beta',
    'category': 'Connector',
    'website': 'https://github.com/yibudak',
    'author': 'Yiğit Budak',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'base', 'queue_job', 'sale', 'stock', 'account', 'product', 'delivery',
    ],
    "external_dependencies": {
        "python": ["woocommerce", "unicode_tr"],
    },
    'data': [
        'wizards/woo_match_payment_shipment_methods_view.xml',
        'view/woocommerce_backend_view.xml',
        'view/product_category_view.xml',
        'view/product_attribute_view.xml',
        # 'view/product_attribute_value_view.xml',
        'view/product_template_view.xml',
        'view/product_product_view.xml',
        'view/res_partner_view.xml',
        'view/sale_order_view.xml',
        'view/res_company_view.xml',
        'security/ir.model.access.csv',
    ],
}
