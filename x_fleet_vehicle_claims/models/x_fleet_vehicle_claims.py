# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class FleetVehicleClaims(models.Model):
    _name = "fleet.vehicle.claims"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Fleet Vehicle Claims"
    _order = "date desc, id desc"

    name = fields.Char(
        string='Sequence',
        required=True,
        readonly=True,
        index=True,
        copy=False,
        default=lambda self: _('New'))
    date = fields.Date(
        string="Date",
        required=True,
        default=fields.Date.context_today)
    vehicle_id = fields.Many2one(
        'fleet.vehicle',
        string='Vehicle',
        required=True,
        help='Vehicle concerned by this claims')
    driver_id = fields.Many2one(
        'hr.employee',
        string='Driver',
        required=True,
        help='Driver of the vehicle')
    third_party_id = fields.Many2one(
        'res.partner',
        string='Third Party',
        help=' Third Party ์Name')
    third_party_plate = fields.Char(
        string='Third party plate',
        help='License plate number of the third party vehicle')
    description = fields.Text('Description')
    claimed = fields.Boolean(default=False)

    @api.model
    def create(self, vals):
        if not vals.get('name', False) or vals['name'] == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'fleet.vehicle.claims') or _('New')
        result = super(FleetVehicleClaims, self).create(vals)
        return result
