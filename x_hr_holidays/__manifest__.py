# -*- coding: utf-8 -*-

{
    'name': 'Enhancement - HR Holidays',
    'license': 'AGPL-3',
    'category': 'Human Resources',
    'version': '1.0',
    'sequence': 125,
    'description': """
        Enhancement HR Holidays.""",
    'depends': ['hr_holidays'],
    'summary': 'HR Holidays',
    'data': [
        'views/x_hr_holidays_menu_views.xml',
        'views/x_hr_holidays_tree_views.xml',
        'views/x_hr_holidays_form_views.xml',
    ],
    'demo': [],
    'installable': True,
    'auto-install': True,
}
