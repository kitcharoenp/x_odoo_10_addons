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
    * Only edit own activities
    * Added the start, end, vehicle, note and overtime field in the activities
    * Changed the timesheets line inline edit to popup
        """,
    'depends': ['hr_timesheet_sheet', 'fleet', 'report'],
    'summary': 'Timesheets',
    'data': [
        'views/x_hr_timesheet_view.xml',
        'views/x_hr_timesheet_filter_view.xml',
        # Activities
        'views/x_hr_timesheet_activities_filter_view.xml',
        'views/x_hr_timesheet_activities_form_view.xml',
        'views/x_hr_timesheet_activities_list_view.xml',
        # Reports
        'reports/x_hr_timesheet_sheet_report.xml',
        # report templates
        #
        # new - Weekly Timesheet pdf templates
        'reports/templates/x_hr_timesheet_sheet_weekly_report_template.xml',
        # inherit - Timesheet Entries pdf templates
        'reports/templates/x_report_timesheet_templates.xml',
        # Security
        'security/ir.model.access.csv',
    ],

    'demo': [],
    'installable': True,
    'auto_install': False,
}
