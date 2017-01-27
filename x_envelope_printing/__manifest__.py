# -*- coding: utf-8 -*-

{
    'name': 'Envelope Printing',
    'version': '1.0',
    'license': 'AGPL-3',
    'category': 'Tools',
    'description': """
        This module gives you a quick printing of
        your contacts Envelope""",
    'depends': ['base',
                'report'],
    'summary': 'Customers, Vendors, Partners,... Envelope Printing',
    'data': [
        'reports/x_envelope_printing_report.xml',
        'reports/templates/x_envelope_printing_template.xml',
    ],
    'installable': True,
}
