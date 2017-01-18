# -*- coding: utf-8 -*-

{
    'name': 'Receipt/Send for Bulk Posting',
    'version': '1.0',
    'license': 'AGPL-3',
    'category': 'Report, Tools',
    'description': """
        This module gives you a quick printing of
        your vendors Receipt/Send bulk Posting""",
    'depends': ['base',
                'report'],
    'summary': 'Customers, Vendors, Partners,... Receipt/Send bulk Posting Printing',
    'data': [
        'reports/x_receipt_bulk_posting_report.xml',
        'reports/templates/x_receipt_bulk_posting_template.xml',
    ],
    'installable': True,
}
