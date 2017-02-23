# -*- coding: utf-8 -*-

{
    'name': 'Timesheet Entry Report',
    'version': '1.0',
    'license': 'AGPL-3',
    'category': 'Human Resource',
    'description': """
        Timesheet Entry Report""",
    'depends': ['x_hr_timesheet_sheet', 'report'],
    'summary': 'Timesheet Entry Report',
    'data': [
        # Views
        'views/x_report_timesheet_entry_form_view.xml',
        # Menu and Action
        'actions/x_report_timesheet_entry_act_window.xml',
        'views/x_report_timesheet_entry_menu_view.xml',
        # Report
        'report/x_report_timesheet_entry_report.xml',
        'report/templates/x_report_ts_entry_template.xml',
        # Security
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto-install': False,
}
