# -*- coding: utf-8 -*-

{
    'name': 'Fleet Vehicle Claims',
    'version': '1.0',
    'license': 'AGPL-3',
    'category': 'Fleet',
    'description': """
        Fleet Vehicle Claims""",
    'depends': ['fleet'],
    'summary': 'Fleet Vehicle Claims',
    'data': [
        # Menu and Action
        'actions/x_fleet_vehicle_claims_act_window.xml',
        'views/x_fleet_vehicle_claims_menu_view.xml',
        # Views
        'views/x_fleet_vehicle_claims_form_view.xml',
        'views/x_fleet_vehicle_claims_tree_view.xml',

        # Sequence
        'data/x_fleet_vehicle_claims_sequence_data.xml',
    ],
    'installable': True,
    'auto-install': True,
}
