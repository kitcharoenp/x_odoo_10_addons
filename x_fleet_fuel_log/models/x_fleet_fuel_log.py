# -*- coding: utf-8 -*-

from odoo import api, fields, models


class FleetVehicleLogFuel(models.Model):
    _inherit = 'fleet.vehicle.log.fuel'

    x_fuel_consumption = fields.Float(
        compute="_compute_fuel_consumption",
        group_operator="avg",
        string="Fuel Consumption",
        store="True")
    x_last_refill_odometer = fields.Float(string="Last Refill Odometer")

    @api.multi
    @api.depends('liter', 'odometer', 'x_last_refill_odometer')
    def _compute_fuel_consumption(self):
        for fuel_log in self:
            distance = fuel_log.odometer - fuel_log.x_last_refill_odometer
            if fuel_log.liter > 0:
                fuel_log.x_fuel_consumption = distance / fuel_log.liter
