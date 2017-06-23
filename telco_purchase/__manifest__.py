# -*- coding: utf-8 -*-
# @author Kitcharoen Poolperm <kitcharoenp@gmail.com>
# @copyright Copyright (C) 2017
# @license http://opensource.org/licenses/gpl-3.0.html GNU Public License

{
    'name': 'Telco Purchase Order',
    'version': '0.01',
    'category': 'Purchases',
    "author": "kicharoenp@gmail.com",
    'summary': 'Purchase Orders for Telecommunications Company',
    'description': """
        1. Payment report per a purchase Order
        2. New Managing , Accounting Director fields in ResCompany Model
        3. New Project, Requestor, Manager, Other ref fields in PurchaseOrder Model
    """,
    'depends': ['purchase'],
    'data': [
        'data/telco_purchase_sequence_data.xml',
        # Views
        'views/telco_purchase_order_tree_view.xml',
        'views/telco_purchase_order_form_view.xml',
        'views/telco_purchase_rescompany_form_view.xml',
        # Reports and Templates
        'reports/telco_purchase_report.xml',
        'reports/templates/payment_report_by_po_templates.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
