# -*- coding: utf-8 -*-
# @author Kitcharoen Poolperm <kitcharoenp@gmail.com>
# @copyright Copyright (C) 2018
# @license http://opensource.org/licenses/gpl-3.0.html GNU Public License

{
    'name': 'Hr Employee',
    'version': '0.1',
    'license': 'AGPL-3',
    'category': 'Human Resources',
    
    'description':"""
Enhancement the `hr_employee` module  :
-------------
    * New Analytic Account Field
    """,

    'depends': ['hr'],
    'summary': 'Enhancement the `hr_employee` module',
    'data': [
        # Form
        'views/telco_hr_employee_form_view.xml',
    ],
    'installable': True,
    'auto-install': False,
}
