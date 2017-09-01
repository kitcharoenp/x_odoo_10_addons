# -*- coding: utf-8 -*-

{
    'name': 'Telco Work Order',
    'version': '1.0',
    'license': 'AGPL-3',
    'category': 'Telecommunication',
    "author": "kicharoenp@gmail.com",
    'description': """
        Work Order for Telecommunication""",
    'depends': ['base_setup', 'cmis_web_alf', ],
    'summary': """
        Work Order for Telecommunication
        """,
    'data': [
        # Security
        'security/telco_work_order_groups.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        # Menu and Action
        'actions/telco_work_order_act_window.xml',
        'views/telco_work_order_menu_view.xml',
        # Views
        'views/telco_work_order_tree_view.xml',
        'views/telco_work_order_form_view.xml',
        'views/telco_work_order_cmis_form_view.xml',
        # Sequence
        'data/telco_work_order_sequence_data.xml',
        # Reports
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'auto-install': False,
}
