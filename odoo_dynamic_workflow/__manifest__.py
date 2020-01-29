# -*- coding: utf-8 -*-
##########################################################
###                 Disclaimer                         ###
##########################################################
### Lately, I started to get very busy after I         ###
### started my new position and I couldn't keep up     ###
### with clients demands & requests for customizations ###
### & upgrades, so I decided to publish this module    ###
### for community free of charge. Building on that,    ###
### I expect respect from whoever gets his/her hands   ###
### on my code, not to copy nor rebrand the module &   ###
### sell it under their names.                         ###
##########################################################

{
    'name': 'Dynamic Workflow Builder',
    'version': '1.0',
    'sequence': '10',
    'category': 'Extra Tools',
    'author': 'Mohamed Youssef',
    'website': 'http://mohamedhammad.info',
    'summary': 'Dynamic Workflow Builder',
    'images': [
        'static/description/banner.png',
    ],
    'description': """
Dynamic Workflow Builder
========================
* You can build dynamic workflow for any model.
""",
    'data': [
        'templates/webclient_templates.xml',
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/menu.xml',
        'wizards/views/odoo_workflow_refuse_wizard_view.xml',
        'wizards/views/odoo_workflow_update_wizard_view.xml',
        'views/odoo_workflow_view.xml',
        'views/ir_actions_server_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
