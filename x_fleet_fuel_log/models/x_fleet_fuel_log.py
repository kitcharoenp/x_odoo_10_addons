# -*- coding: utf-8 -*-

from odoo import api, fields, models


class FleetVehicleLogFuel(models.Model):
    _inherit = 'fleet.vehicle.log.fuel'

    x_fuel_consumption = fields.Float(
        compute="_compute_fuel_consumption",
        group_operator="avg",
        string="Fuel Consumption",
        store="True")
    x_last_refuel_odometer = fields.Float(string="Last Refuel Odometer")

    @api.multi
    @api.depends('liter', 'odometer', 'x_last_refuel_odometer')
    def _compute_fuel_consumption(self):
        for fuel_log in self:
            distance = fuel_log.odometer - fuel_log.x_last_refuel_odometer
            if fuel_log.liter > 0:
                fuel_log.x_fuel_consumption = distance / fuel_log.liter

    def _get_last_refuel_odometer(self):
        vehicle_log_fuel = self.env['fleet.vehicle.log.fuel'].search([
                ('vehicle_id', '=', self.vehicle_id.id)],
                order="odometer desc",
                limit=1)
        return vehicle_log_fuel.odometer

    @api.onchange('vehicle_id')
    def _onchange_vehicle(self):
        super(FleetVehicleLogFuel, self)._onchange_vehicle()
        if self.vehicle_id:
            x_last_refuel_odometer = self._get_last_refuel_odometer()
            self.x_last_refuel_odometer = x_last_refuel_odometer
