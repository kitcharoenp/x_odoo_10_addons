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
        1. Payment Report per a purchase Order
        2. New managing , accounting director fields in ResCompany model
        3. New project, requestor, manager, other ref fields
        4. New receipt by, invoice receipt date fields
        5. Default purchase tax vendor 
    """,
    'depends': ['purchase',
                'telco_account_invoice',
                ],
    'data': [
        'data/telco_purchase_sequence_data.xml',
        # Views
        'views/telco_purchase_order_tree_view.xml',
        'views/telco_purchase_order_form_view.xml',
        'views/telco_purchase_rescompany_form_view.xml',
        'views/telco_purchase_res_partner_form_view.xml',
        # Search
        'views/telco_purchase_order_search_view.xml',
        # Reports and Templates
        'reports/telco_purchase_report.xml',
        'reports/templates/payment_report_by_po_templates.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
