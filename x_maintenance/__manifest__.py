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
        # Actions
        'actions/x_equipment_act_window.xml',
        # Search
        'views/x_equipment_form_view.xml',
        'views/x_equipment_kanban_view.xml',
        'views/x_equipment_tree_view.xml',
        'views/x_equipment_search_view.xml',
        # Sequence
        'data/x_maintenance_request_sequence_data.xml',
    ],
    'demo': [],
    'installable': True,
    'auto-install': True,
}
