# -*- coding: utf-8 -*-

{
    'name': 'Enhancement - Maintenance',
    'version': '1.0',
    'license': 'AGPL-3',
    'sequence': 125,
    'category': 'Equipments',
    'description': """
Extend Maintenance Request & Equipment:
    Images fields for Equipment
    Asset Number for Equipment
    related a vehicle to equipment
    Linked a Product Template to a Equipment
        """,
    'depends': ['hr_maintenance', 'fleet'],
    'summary': 'Enhancement Equipments',
    'data': [
        # Actions
        'actions/x_equipment_act_window.xml',
        'actions/x_equipment_product_act_window.xml',
        # View
        'views/x_equipment_form_view.xml',
        'views/x_equipment_kanban_view.xml',
        'views/x_equipment_tree_view.xml',
        'views/x_equipment_search_view.xml',
        'views/x_equipment_product_form_view.xml',
        'views/x_equipment_product_menu.xml',
        # Sequence
        'data/x_maintenance_request_sequence_data.xml',
    ],
    'demo': [],
    'installable': True,
    'auto-install': True,
}
