# -*- coding: utf-8 -*-

{
    'name': 'Air Conditioner - Maintenance',
    'version': '1.0',
    'sequence': 125,
    'description': """
        Air Conditioner - Maintenance.""",
    'depends': ['x_maintenance'],
    'summary': 'Air Conditioner Maintenance',
    'data': [
        # Menus and Actions
        'actions/x_air_conditioner_equipment_act_window.xml',
        'actions/x_air_conditioner_maintenance_act_window.xml',
        'views/x_air_conditioner_menu_view.xml',
        # Resource data
        'data/x_air_conditioner_data.xml',
    ],
    'demo': [],
    'installable': True,
    'auto-install': True,
}
