# -*- coding: utf-8 -*-

{
    'name': 'Timesheet Summary by Department',
    'version': '1.0',
    'license': 'AGPL-3',
    'category': 'Human Resource',
    'description': """
        Timesheet Summary by Department""",
    'depends': ['x_hr_timesheet_sheet', 'report'],
    'summary': 'Timesheet Summary by Department',
    'data': [
        # Views
        'views/x_timesheet_summary_department_form_view.xml',
        # Menu and Action
        'actions/x_timesheet_summary_department_act_window.xml',
        'views/x_timesheet_summary_department_menu_view.xml',
        # Report
        'report/x_timesheet_summary_department_report.xml',
        'report/templates/x_ts_dept_report_template.xml',
    ],
    'installable': True,
    'auto-install': False,
}
