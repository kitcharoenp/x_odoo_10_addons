# -*- coding: utf-8 -*-
{
    'name': 'Leave Employee Image',
    'version': '1.0',
    'license': 'AGPL-3',
    'category': 'Human Resources',
    "author": "kicharoenp@gmail.com",
    'description': """
Show a Employee image on Leave
        """,
    'depends': [
        'hr_holidays',
        'x_hr_holidays'
        ],
    'summary': 'Show a Employee image on Leave',
    'data': [
        # Views
        'views/x_hr_holidays_emp_image_form_view.xml',
    ],

    'installable': True,
    'auto_install': False,
}
