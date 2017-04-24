# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

import odoo.addons.decimal_precision as dp


class XFaultManagement(models.Model):
    _name = "x.fault.management"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Fault Management"
    _order = "id desc"

    name = fields.Char(
        string='Sequence',
        required=True,
        readonly=True,
        index=True,
        copy=False,
        default=lambda self: _('New'))
    customer_reference = fields.Char(string="Customer Reference/ID")
    partner_id1 = fields.Many2one(
        'res.partner',
        string='Customer A')
    partner_id2 = fields.Many2one(
        'res.partner',
        string='Customer B')
    start_datetime = fields.Datetime(
        string="Start DateTime")
    end_datetime = fields.Datetime(
        string="End DateTime")
    cause_of_fault = fields.Text('Cause of Fault')
    troubleshooting = fields.Text('Troubleshooting')

    @api.model
    def create(self, vals):
        if not vals.get('name', False) or vals['name'] == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'x.fault.management') or _('New')
        result = super(XFaultManagement, self).create(vals)
        return result
