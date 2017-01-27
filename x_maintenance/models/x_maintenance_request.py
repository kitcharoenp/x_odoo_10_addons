# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'

    name = fields.Char(
        string='Sequence No.',
        required=True,
        readonly=True,
        index=True,
        copy=False,
        default=lambda self: _('New'))

    @api.model
    def create(self, vals):
        if not vals.get('name', False) or vals['name'] == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'x_maintenance.request') or _('New')
        result = super(MaintenanceRequest, self).create(vals)
        return result
