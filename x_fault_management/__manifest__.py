# -*- coding: utf-8 -*-

{
    'name': 'Fault Management (Telco)',
    'version': '1.0',
    'license': 'AGPL-3',
    'category': 'Telecommunication',
    'description': """
        Fault Management for Telecommunication""",
    'depends': [],
    'summary': """
        Fault Management is the set of functions that detect, isolate,
        and correct malfunctions in a telecommunications network
        """,
    'data': [
        # Security
        # Menu and Action
        'actions/x_fault_management_act_window.xml',
        'views/x_fault_management_menu_view.xml',
        # Views
        'views/x_fault_management_form_view.xml',
        'views/x_fault_management_tree_view.xml',
        # Sequence
        'data/x_fault_management_sequence_data.xml',
        # Reports
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'auto-install': False,
}
