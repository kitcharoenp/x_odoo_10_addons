# -*- coding: utf-8 -*-
# @author Kitcharoen Poolperm <kitcharoenp@gmail.com>
# @copyright Copyright (C) 2018
# @license http://opensource.org/licenses/gpl-3.0.html GNU Public License

{
    'name': 'Account Budgets',
    'version': '0.1',
    'license': 'AGPL-3',
    'category': 'Accounting',

    'description':"""
Enhancement the `account_budget` module  :
-------------
    * New a Internal Reference Field
    * New a Available Amount Field
    * Pivot View
    """,

    'depends': ['account_budget',],
    'summary': 'Enhancement the `account_budget` module',
    'data': [
        # Views
        'views/telco_account_budget_form_view.xml',
        'views/telco_account_budget_pivot_view.xml',
        'views/telco_account_budget_tree_view.xml',
        # Action
        'views/telco_account_budget_act_crossovered_budget_lines_view.xml',
    ],
    'installable': True,
    'auto-install': False,
}
