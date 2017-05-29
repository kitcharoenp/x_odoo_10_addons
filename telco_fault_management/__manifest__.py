# -*- coding: utf-8 -*-

{
    'name': 'Telco Fault Management',
    'version': '1.0',
    'license': 'AGPL-3',
    'category': 'Telecommunication',
    "author": "kicharoenp@gmail.com",
    'description': """
        Fault Management for Telecommunication""",
    'depends': [
        'base',
        'mail',
    ],
    'summary': """
        Fault Management is the set of functions that detect, isolate,
        and correct malfunctions in a telecommunications network
        """,
    'data': [
        # Security
        'security/telco_fault_management_groups.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        # Menu and Action
        'actions/telco_fault_management_act_window.xml',
        'views/telco_fault_management_menu_view.xml',
        # Views
        'views/telco_fault_management_form_view.xml',
        'views/telco_fault_management_tree_view.xml',
        'views/telco_fault_management_pivot_view.xml',
        'views/telco_fault_management_graph_view.xml',
        # Sequence
        'data/telco_fault_management_sequence_data.xml',
        # Reports
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'auto-install': False,
}
