# -*- coding: utf-8 -*-
{
    'name': 'Enhancement - HR Holidays',
    'license': 'AGPL-3',
    'category': 'Human Resources',
    "author": "kicharoenp@gmail.com",
    'version': '1.0',
    'sequence': 125,
    'description': """
Enhancement HR Holidays :
-------------
    * created a related timesheet line when leave is confirm
    * deleted a related timesheet line when refuse or reset to draft
    * computed can approve leave base on first/second approval
    * action mass approve in tree view
        """,
    'depends': ['hr_holidays', 'x_hr_timesheet_sheet'],
    'summary': 'HR Holidays',
    'data': [
        'views/x_hr_holidays_menu_views.xml',
        'views/x_hr_holidays_tree_views.xml',
        'views/x_hr_holidays_form_views.xml',
        'views/x_hr_holidays_filter_view.xml',
        # 'views/x_web_calendar_templates.xml',
        # Actions
        'actions/x_leave_request_to_approve_act_window.xml',
        'actions/x_hr_holidays_mass_approve_act_server.xml',
    ],
    'demo': [],
    'installable': True,
    'auto-install': False,
}
