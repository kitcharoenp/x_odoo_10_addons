# -*- coding: utf-8 -*-
# @author Kitcharoen Poolperm <kitcharoenp@gmail.com>
# @copyright Copyright (C) 2017
# @license http://opensource.org/licenses/gpl-3.0.html GNU Public License
{
    'name': 'Telco Expense',
    'version': '0.01',
    'category': 'Expense',
    "author": "kicharoenp@gmail.com",
    'summary': 'Telco Expense',
    'description': """
    * A new accounting date field
    """,
    'depends': ['hr_expense', 'project', ],
    'data': [
        # Actions
        # Views
        'views/telco_expense_form_view.xml',
        # Reports and Templates
    ],
    'installable': True,
    'auto_install': False,
}
