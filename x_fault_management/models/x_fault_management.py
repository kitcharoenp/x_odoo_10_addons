# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

import odoo.addons.decimal_precision as dp
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime


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
    customer_reference = fields.Char(string="Reference/ID")
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
    duration = fields.Float(
        string='Duration',
        compute='_compute_duration',
        store=True,
        readonly=True)
    state_id = fields.Many2one(
        "res.country.state",
        string='State')
    latitude = fields.Float(string='Geo Latitude', digits=(16, 5))
    longitude = fields.Float(string='Geo Longitude', digits=(16, 5))
    distance = fields.Float(string='Distance')
    permanant = fields.Boolean(default=False)
    temporarily = fields.Boolean(default=False)
    process_time = fields.Float(string='Process Time')

    @api.depends('start_datetime', 'end_datetime')
    def _compute_duration(self):
        for fault_management in self:
            if fault_management.end_datetime:
                end_dt = datetime.strptime(
                    fault_management.end_datetime,
                    DEFAULT_SERVER_DATETIME_FORMAT)
                start_dt = datetime.strptime(
                    fault_management.start_datetime,
                    DEFAULT_SERVER_DATETIME_FORMAT)
                delta = end_dt - start_dt
                fault_management.duration = delta.total_seconds() / 60.0

    @api.model
    def create(self, vals):
        if not vals.get('name', False) or vals['name'] == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'x.fault.management') or _('New')
        result = super(XFaultManagement, self).create(vals)
        return result
