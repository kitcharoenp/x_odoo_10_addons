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

from odoo import models, api, _


class odoo_workflow_update_wizard(models.TransientModel):
    _name = 'odoo.workflow.update.wizard'

    @api.multi
    def btn_update(self):
        from odoo.addons import odoo_dynamic_workflow
        return odoo_dynamic_workflow.update_workflow(self)