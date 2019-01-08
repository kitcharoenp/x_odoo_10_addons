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

    # Description in Apps page
    'description': """
    * A new accounting date, payment_mode, Vendor field
    * Change the analytic_account onchange the employee field
    """,

    'depends': ['hr_expense', 'project', 'telco_hr_employee',],
    'data': [
        # Actions
        # Views
        'views/telco_expense_form_view.xml',
        'views/telco_expense_tree_view.xml',
        'views/telco_expense_sheet_form_view.xml',
        # Reports and Templates
    ],
    'installable': True,
    'auto_install': False,
}
