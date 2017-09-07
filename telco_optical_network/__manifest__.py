# -*- coding: utf-8 -*-
# @author Kitcharoen Poolperm <kitcharoenp@gmail.com>
# @copyright Copyright (C) 2017
# @license http://opensource.org/licenses/gpl-3.0.html GNU Public License

{
    'name': 'Telco Optical Network',
    'version': '0.01',
    'category': 'Telecommunication',
    "author": "kicharoenp@gmail.com",
    'summary': 'Optical Network',
    'description': """

    """,
    'depends': ['base_setup', 'cmis_web_alf', ],
    'data': [
        # Security
        'security/telco_optical_network_groups.xml',
        'security/ir_rule.xml',
        'security/ir.model.access.csv',
        # Menu and Action
        'actions/telco_optical_network_act_window.xml',
        'views/telco_optical_network_menu_view.xml',
        # Views
        'views/telco_optical_network_form_view.xml',
        'views/telco_optical_network_tree_view.xml',
        'views/telco_optical_network_cmis_form_view.xml',
        # Reports and Templates
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
