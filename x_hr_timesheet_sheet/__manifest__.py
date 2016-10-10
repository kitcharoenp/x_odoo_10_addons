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
    * Double Validate define in a department
    * Set readonly the employee_id except HR officer
    * Don't edit not own activities
    * Added the startime, stoptime, vehicle in a activities
        """,
    'depends': ['hr_timesheet_sheet'],
    'summary': 'Timesheets',
    'data': [
        'views/x_hr_timesheet_view.xml',
        'views/x_hr_timesheet_filter_view.xml',
        # hr_timesheet my activities filter
        'views/x_hr_timesheet_activities_filter_view.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
