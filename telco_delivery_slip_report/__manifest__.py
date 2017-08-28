# -*- coding: utf-8 -*-
# @author Kitcharoen Poolperm <kitcharoenp@gmail.com>
# @copyright Copyright (C) 2017
# @license http://opensource.org/licenses/gpl-3.0.html GNU Public License
{
    'name': 'Telco Delivery Slip Report',
    'version': '0.01',
    'category': 'Warehouse',
    "author": "kicharoenp@gmail.com",
    'summary': 'Telco Delivery Slip Report',
    'description': """
    """,
    'depends': ['stock', ],
    'data': [
        # Views
        # Reports and Templates
        'report/telco_delivery_slip_report.xml',
        'report/templates/telco_report_delivery_slip_template.xml',
    ],
    'installable': True,
    'auto_install': False,
}
