# -*- coding: utf-8 -*-
# @author Kitcharoen Poolperm <kitcharoenp@gmail.com>
# @copyright Copyright (C) 2017
# @license http://opensource.org/licenses/gpl-3.0.html GNU Public License

{
    'name': 'Telco NBTC Permission',
    'version': '0.01',
    'category': 'Telecommunication',
    "author": "kicharoenp@gmail.com",
    'summary': 'Telco NBTC Permission',
    'description': """

    """,
    'depends': ['telco_optical_network', 'cmis_web_alf', ],
    'data': [
        # Sequence
        'data/telco_nbtc_permission_sequence_data.xml',
        # Security
        # Menu and Action
        'actions/telco_nbtc_permission_act_window.xml',
        'views/telco_nbtc_permission_menu_view.xml',
        # Views
        'views/telco_nbtc_permission_tree_view.xml',
        'views/telco_nbtc_permission_form_view.xml',
        # Reports and Templates
    ],
    'installable': True,
    'auto_install': False,
}
