# -*- coding: utf-8 -*-
{
    'name': 'Timesheets Employee Image',
    'version': '1.0',
    'license': 'AGPL-3',
    'category': 'Human Resources',
    "author": "kicharoenp@gmail.com",
    'description': """
Enhancement Timesheets with image and state field
        """,
    'depends': [
        'hr_timesheet_sheet',
        'x_hr_timesheet_sheet'
        ],
    'summary': 'New image and state field to Timesheets',
    'data': [
        # Views
        'views/x_hr_timesheet_emp_image_form_view.xml'
    ],

    'installable': True,
    'auto_install': False,
}
