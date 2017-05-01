# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime


class TelcoWorkOrder(models.Model):
    _name = "telco.work.order"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Telco Work Order"
    _order = "id desc"

    name = fields.Char(
        string='Sequence',
        required=True,
        readonly=True,
        index=True,
        copy=False,
        default=lambda self: _('New'))
    fault_id = fields.Many2one(
        'telco.fault.management',
        string='Reference Fault')
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer')
    start_date = fields.Date(
        string="Start Date")
    end_date = fields.Date(
        string="End Date")
    duration = fields.Float(
        string='Duration',
        compute='_compute_duration',
        store=True,
        readonly=True)
    state_id = fields.Many2one(
        "res.country.state",
        string='State')
    description = fields.Text('Cause of Fault')
    latitude = fields.Float(string='Geo Latitude', digits=(16, 5))
    longitude = fields.Float(string='Geo Longitude', digits=(16, 5))
    process_time = fields.Float(string='Process Time')
    employee_id = fields.Many2one(
        'hr.employee',
        string="Payer",
        required=True,
        default=lambda self: self.env['hr.employee'].search([
            ('user_id', '=', self.env.uid)], limit=1))

    @api.depends('start_datetime', 'end_datetime')
    def _compute_duration(self):
        for work_order in self:
            if work_order.end_datetime:
                end_dt = datetime.strptime(
                    work_order.end_datetime,
                    DEFAULT_SERVER_DATETIME_FORMAT)
                start_dt = datetime.strptime(
                    work_order.start_datetime,
                    DEFAULT_SERVER_DATETIME_FORMAT)
                delta = end_dt - start_dt
                work_order.duration = delta.total_seconds() / 60.0

    @api.model
    def create(self, vals):
        if not vals.get('name', False) or vals['name'] == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'telco.work.order') or _('New')
        result = super(TelcoWorkOrder, self).create(vals)
        return result
