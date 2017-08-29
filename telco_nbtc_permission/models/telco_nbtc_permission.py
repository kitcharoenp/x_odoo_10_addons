# -*- coding: utf-8 -*-
# @author Kitcharoen Poolperm <kitcharoenp@gmail.com>
# @copyright Copyright (C) 2017
# @license http://opensource.org/licenses/gpl-3.0.html GNU Public License

from odoo import api, fields, models, _


class TelcoNbtcPermission(models.Model):
    _name = "telco.nbtc.permission"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Telco NBTC Permission"
    _order = "id desc"

    name = fields.Char(
        required=True,
        readonly=True,
        index=True,
        copy=False,
        default=lambda self: _('New'))
    date = fields.Date(
        default=fields.Date.context_today,
        string="Date")
    date_text = fields.Char(
        string='Date Text',
        copy=False, )
    description_attachment = fields.Text('Description Attachment')
    description_route = fields.Text('Description Route')
    description_other = fields.Text('Description Other')
    optical_route_lines = fields.One2many(
        'telco.optical.network',
        'nbtc_permission_id',
        string='Optical Route Lines', )
    employee_id = fields.Many2one(
        'hr.employee',
        string="Employee",
        required=True,
        default=lambda self: self.env['hr.employee'].search([
            ('user_id', '=', self.env.uid)], limit=1))
    manager_id = fields.Many2one(
        'hr.employee',
        string="Manager",
        required=True, )

    @api.model
    def create(self, vals):
        if not vals.get('name', False) or vals['name'] == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'telco.nbtc.permission') or _('New')
        result = super(TelcoNbtcPermission, self).create(vals)
        return result
