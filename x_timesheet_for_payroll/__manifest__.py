# -*- coding: utf-8 -*-

{
    'name': 'Timesheet Report for Payroll',
    'version': '1.0',
    'license': 'AGPL-3',
    'category': 'Human Resource',
    'description': """
        Timesheet Report for the external Payroll""",
    'depends': ['x_hr_timesheet_sheet', 'report'],
    'summary': 'Timesheet Report for the external Payroll',
    'data': [
        # Views
        'views/x_timesheet_for_payroll_form_view.xml',
        # Menu and Action
        'actions/x_timesheet_for_payroll_act_window.xml',
        'views/x_timesheet_for_payroll_menu_view.xml',
        # Report
        'report/x_timesheet_for_payroll_report.xml',
        'report/templates/x_ts_for_payroll_template.xml',
        # Security
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto-install': False,
}
