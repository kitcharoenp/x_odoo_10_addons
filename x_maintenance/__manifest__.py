# -*- coding: utf-8 -*-

{
    'name': 'Enhancement - Maintenance',
    'version': '1.0',
    'license': 'AGPL-3',
    'sequence': 125,
    'category': 'Equipments',
    'description': """
        Extend Maintenance.""",
    'depends': ['hr_maintenance', 'fleet'],
    'summary': 'Enhancement Equipments',
    'data': [
        'views/x_equipment_form_view.xml',
        'views/x_equipment_kanban_view.xml',
        'views/x_equipment_tree_view.xml',
    ],
    'demo': [],
    'installable': True,
    'auto-install': True,
}
