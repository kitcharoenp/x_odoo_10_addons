# -*- coding: utf-8 -*-

from odoo import api, fields, models


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    x_driver_id1 = fields.Many2one(
        'hr.employee',
        string='First Driver',
        help='Driver of the vehicle')
    x_driver_id2 = fields.Many2one(
        'hr.employee',
        string='Second Driver')
    x_administrator_id = fields.Many2one(
        'hr.employee',
        string='Administrator')
    x_fleet_card_no = fields.Char('Fleet Card No.', copy=False)
    x_fleet_card_password = fields.Char('Fleet Card Password', copy=False)

    @api.onchange('x_driver_id1')
    def _onchange_x_driver(self):
        if self.x_driver_id1:
            self.driver_id = self.x_driver_id1.user_id.partner_id

    def _get_odometer(self):
        super(FleetVehicle, self)._get_odometer()
        FleetVehicalOdometer = self.env['fleet.vehicle.odometer']
        for record in self:
            vehicle_odometer = FleetVehicalOdometer.search([('vehicle_id', '=', record.id)], limit=1, order='value desc')
            if vehicle_odometer:
                record.odometer = vehicle_odometer.y_odometer
            else:
                record.odometer = 0
