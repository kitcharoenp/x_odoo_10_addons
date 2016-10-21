# -*- coding: utf-8 -*-

{
    'name': 'Extended Timesheets',
    'version': '1.0',
    'license': 'AGPL-3',
    'author': "Kitcharoen Poolperm",
    'category': 'Human Resources',
    'sequence': 135,
    'description': """
Extended Timesheet with following :
-------------
    * Set the employee_id field to readonly
    * Double Validate define in a department
    * Set default search activities to own
    *
    * only edit own activities
    * Added a vehicle to the activities form
        """,
    'depends': ['hr_timesheet_sheet', 'fleet'],
    'summary': 'Timesheets',
    'data': [
        'views/x_hr_timesheet_view.xml',
        'views/x_hr_timesheet_filter_view.xml',
        # hr_timesheet my activities filter
        'views/x_hr_timesheet_activities_filter_view.xml',
        'views/x_hr_timesheet_activities_form_view.xml'
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
