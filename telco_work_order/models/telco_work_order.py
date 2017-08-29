# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


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
    description = fields.Text('Description')
    latitude = fields.Float(string='Geo Latitude', digits=(16, 5))
    longitude = fields.Float(string='Geo Longitude', digits=(16, 5))
    employee_id = fields.Many2one(
        'hr.employee',
        string="Employee",
        required=True,
        default=lambda self: self.env['hr.employee'].search([
            ('user_id', '=', self.env.uid)], limit=1))

    @api.depends('start_date', 'end_date')
    def _compute_duration(self):
        for work_order in self:
            if work_order.end_date:
                date_end = fields.Datetime.from_string(work_order.end_date)
                date_start = fields.Datetime.from_string(work_order.start_date)
                delta = date_end - date_start
                work_order.duration = delta.days
    submit_date = fields.Date(
        string="Submit Date")
    revised_drawing = fields.Boolean(default=False)

    @api.model
    def create(self, vals):
        if not vals.get('name', False) or vals['name'] == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'telco.work.order') or _('New')
        result = super(TelcoWorkOrder, self).create(vals)
        return result
