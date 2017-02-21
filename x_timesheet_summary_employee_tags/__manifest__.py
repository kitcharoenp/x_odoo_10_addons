# -*- coding: utf-8 -*-

{
    'name': 'Timesheet Summary by Employee Tags',
    'version': '1.0',
    'license': 'AGPL-3',
    'category': 'Human Resource',
    'description': """
        Timesheet Summary by Employee Tags""",
    'depends': ['x_hr_timesheet_sheet', 'report'],
    'summary': 'Timesheet Summary by Employee Tags',
    'data': [
        # Views
        'views/x_timesheet_summary_employee_tags_form_view.xml',
        # Menu and Action
        'actions/x_timesheet_summary_employee_tags_act_window.xml',
        'views/x_timesheet_summary_employee_tags_menu_view.xml',
        # Report
        'report/x_timesheet_summary_employee_tags_report.xml',
        'report/templates/x_ts_emp_tags_template.xml',
        # Security
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto-install': False,
}
