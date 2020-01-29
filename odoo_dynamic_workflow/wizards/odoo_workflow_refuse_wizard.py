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

from odoo import fields, models, api, _

class odoo_workflow_refuse_wizard(models.TransientModel):
    _name = 'odoo.workflow.refuse.wizard'
    _description = 'Workflow Refuse Wizard'

    reason = fields.Text(string='Reason')

    @api.multi
    def btn_submit(self):
        # Variables
        cx = self.env.context.copy() or {}
        # Write refuse message
        for wiz in self:
            if wiz.reason and cx.get('active_id', False) and cx.get('active_model', False):
                model_obj = self.env[cx.get('active_model')]
                rec_id = model_obj.browse(cx.get('active_id'))
                if hasattr(rec_id, 'message_post'):
                    rec_id.message_post(_("Reason of refusal is '%s'" % wiz.reason))