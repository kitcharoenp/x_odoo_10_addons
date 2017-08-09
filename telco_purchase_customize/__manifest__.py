# -*- coding: utf-8 -*-
# @author Kitcharoen Poolperm <kitcharoenp@gmail.com>
# @copyright Copyright (C) 2017
# @license http://opensource.org/licenses/gpl-3.0.html GNU Public License
{
    'name': 'Telco Purchase Customize Report',
    'version': '0.01',
    'category': 'Purchases',
    "author": "kicharoenp@gmail.com",
    'summary': 'Telco Purchase Customize Report',
    'description': """
    """,
    'depends': ['telco_purchase', ],
    'data': [
        # Views
        # Reports and Templates
        'reports/telco_purchase_customize_report.xml',
        'reports/templates/telco_purchase_customize_templates.xml',
    ],
    'installable': True,
    'auto_install': False,
}
