# -*- coding: utf-8 -*-
{
    'name': 'Enhancement Timesheets',
    'version': '1.0',
    'license': 'AGPL-3',
    'category': 'Human Resources',
    'sequence': 135,
    'description': """
Enhancement Timesheet with following :
-------------
    * Added vehicle in activity timesheet
    * Auto record vehicle odometer log when created activity
    * Double validate timesheet by choosed manager
    * Set default search activities to own
    * Only edit own activities
    * Added start/end time, note and overtime field in the activity
    * Changed activity line to popup edit
    * Added odometer start/end and collaborators field in the activity
        """,
    'depends': [
        'hr_timesheet_sheet',
        'hr_attendance',
        'fleet',
        'report',
        'x_vehicle_odometer'],
    'summary': 'Enhancement Timesheets',
    'data': [
        'views/x_hr_timesheet_view.xml',
        'views/x_hr_timesheet_filter_view.xml',
        # Activities
        'views/x_hr_timesheet_activities_filter_view.xml',
        'views/x_hr_timesheet_activities_form_view.xml',
        'views/x_hr_timesheet_activities_list_view.xml',
        # Reports
        'reports/x_hr_timesheet_sheet_report.xml',
        'reports/x_hr_timesheet_weekly_th_report.xml',
        # report templates
        #
        # new - Weekly Timesheet pdf templates
        'reports/templates/x_hr_timesheet_sheet_weekly_report_template.xml',
        'reports/templates/x_timesheet_weekly_th_report_template.xml',
        # inherit - Timesheet Entries pdf templates
        'reports/templates/x_report_timesheet_templates.xml',
        # Security
        'security/ir.model.access.csv',
        'security/x_hr_timesheet_sheet_security.xml',
    ],

    'demo': [],
    'installable': True,
    'auto_install': False,
}
