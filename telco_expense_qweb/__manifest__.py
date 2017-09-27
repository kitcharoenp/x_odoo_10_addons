# -*- coding: utf-8 -*-
# @author Kitcharoen Poolperm <kitcharoenp@gmail.com>
# @copyright Copyright (C) 2017
# @license http://opensource.org/licenses/gpl-3.0.html GNU Public License
{
    'name': 'Telco Expense QWeb Report',
    'version': '0.01',
    'category': 'Expense',
    "author": "kicharoenp@gmail.com",
    'summary': 'Telco Expense QWeb Report',
    'description': """
    * Expense QWeb Report by Date
    """,
    'depends': ['hr_expense', 'project', 'telco_expense', ],
    'data': [
        # Actions
        'views/telco_expense_qweb_by_date_form_view.xml',
        'actions/telco_expense_qweb_by_date_act_window.xml',
        # Views
        'views/telco_expense_qweb_menu_view.xml',
        'views/hr_expense_form_view.xml',
        'views/product_product_form_view.xml',
        # Reports and Templates
        'report/telco_expense_qweb_by_date_report.xml',
        'report/templates/telco_expense_qweb_by_date_template.xml',

    ],
    'installable': True,
    'auto_install': False,
}
