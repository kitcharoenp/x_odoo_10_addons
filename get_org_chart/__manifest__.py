# -*- coding: utf-8 -*-
{
    'name': 'Organization Chart',
    'version': '1.0',
    'category': 'OdooBro Apps',
    'author': 'OdooBro - odoobro.contact@gmail.com',
    'website': 'odoobro.com',
    'license': 'AGPL-3',
    'depends': [
        'hr',
        'web',
        'website',
    ],
    'data': [
        # ============================================================
        # SECURITY SETTING - GROUP - PROFILE
        # ============================================================
        # 'security/',

        # ============================================================
        # DATA
        # ============================================================
        # 'data/',

        # ============================================================
        # VIEWS
        # ============================================================
        # 'views/',
        'views/hr_employee_view.xml',
        'views/webclient_templates.xml',

        # ============================================================
        # MENU
        # ============================================================
        # 'menu/',

        # ============================================================
        # FUNCTION USED TO UPDATE DATA LIKE POST OBJECT
        # ============================================================
    ],

    'test': [],
    'demo': [],

    'installable': True,
    'active': False,
    'application': True,
}
