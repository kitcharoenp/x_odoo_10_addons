# -*- coding: utf-8 -*-

{
    'name': 'Extend - Maintenance',
    'version': '1.0',
    'sequence': 125,
    'category': 'Human Resources',
    'description': """
        Extend Maintenance.""",
    'depends': ['hr_maintenance', 'fleet'],
    'summary': 'Equipments',
    'data': [
        'views/x_equipment_form_views.xml'
    ],
    'demo': [],
    'installable': True,
    'auto-install': True,
}
