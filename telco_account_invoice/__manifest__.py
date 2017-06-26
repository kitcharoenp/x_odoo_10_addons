# -*- coding: utf-8 -*-
# @author Kitcharoen Poolperm <kitcharoenp@gmail.com>
# @copyright Copyright (C) 2017
# @license http://opensource.org/licenses/gpl-3.0.html GNU Public License

{
    'name': 'Telco Account Invoice',
    'version': '0.01',
    'category': 'Accounting',
    "author": "kicharoenp@gmail.com",
    'summary': 'Account Invoice for Telecommunications Company',
    'description': """
    """,
    'depends': ['account', 'account_asset'],
    'data': [
        # Views
        'views/telco_account_invoice_form_view.xml',
        # Reports and Templates
    ],
    'installable': True,
    'auto_install': False,
}
