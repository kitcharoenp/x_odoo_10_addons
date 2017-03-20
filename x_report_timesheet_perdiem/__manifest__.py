# -*- coding: utf-8 -*-

{
    'name': 'Timesheet Per Diem Report',
    'version': '1.0',
    'license': 'AGPL-3',
    'category': 'Human Resource',
    'description': """
        Timesheet Per Diem Report""",
    'depends': ['x_hr_timesheet_sheet', 'report'],
    'summary': 'Timesheet Per Diem Report',
    'data': [
        # Views
        'views/x_report_timesheet_perdiem_form_view.xml',
        # Menu and Action
        'actions/x_report_timesheet_perdiem_act_window.xml',        
        'views/x_report_timesheet_perdiem_menu_view.xml',
        # Report
        'report/templates/x_report_ts_perdiem_template.xml',
        # Security
    ],
    'installable': True,
    'auto-install': False,
}
