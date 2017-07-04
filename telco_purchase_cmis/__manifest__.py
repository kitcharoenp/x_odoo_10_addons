# -*- coding: utf-8 -*-
# @author Kitcharoen Poolperm <kitcharoenp@gmail.com>
# @copyright Copyright (C) 2017
# @license http://opensource.org/licenses/gpl-3.0.html GNU Public License
{
    'name': 'Telco Purchase CMIS',
    'version': '0.01',
    'category': 'Purchases',
    "author": "kicharoenp@gmail.com",
    'summary': 'Linked a purchase order to Alfresco cmis',
    'description': """
    """,
    'depends': ['purchase', 'cmis_web_alf',],
    'data': [
        # Views
        'views/telco_purchase_cmis_form_view.xml',
        # Reports and Templates
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
