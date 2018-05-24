# -*- coding: utf-8 -*-

{
    'name': 'Timesheet Records/Fields Security',
    'version': '1.0',
    'license': 'AGPL-3',
    'category': 'Human Resources',
    "author": "kicharoenp@gmail.com",
    'description': """
Timesheet Records/Fields Security
-------------
    * Grant access create on model_hr_employee to base.group_user
    * Grant access write on model_resource_resource to base.group_user
    * Grant access write on employee holidays rule to base.group_user
        """,
    'depends': [
        'x_hr_timesheet_sheet',
        'hr_holidays',
    ],
    'summary': """
        Timesheet Records/Fields Security
        """,
    'data': [
        # Security
        'security/ir.model.access.csv',
        'security/x_hr_timesheet_security.xml',
        # Menu and Action
        # Views
    ],
    'installable': True,
    'auto-install': False,
}
