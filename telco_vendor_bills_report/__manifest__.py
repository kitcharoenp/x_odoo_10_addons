# -*- coding: utf-8 -*-
# @author Kitcharoen Poolperm <kitcharoenp@gmail.com>
# @copyright Copyright (C) 2017
# @license http://opensource.org/licenses/gpl-3.0.html GNU Public License
{
    'name': 'Telco Vendor Bills Report',
    'version': '0.01',
    'category': 'Purchase',
    "author": "kicharoenp@gmail.com",
    'summary': 'Telco Vendor Bills Report',
    'description': """
    * Vendor Bills Report
    """,
    'depends': ['purchase', ],
    'data': [
        # Actions
        'views/telco_vendor_bills_report_form_view.xml',
        'actions/telco_vendor_bills_report_act_window.xml',
        # Views
        'views/telco_vendor_bills_report_menu_view.xml',
        # Reports and Templates
        'report/telco_vendor_bills_qweb_report.xml',
        'report/templates/bills_report_template.xml',
    ],
    'installable': True,
    'auto_install': False,
}
