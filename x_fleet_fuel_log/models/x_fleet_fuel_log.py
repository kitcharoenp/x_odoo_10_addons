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
    x_fuel_type = fields.Selection([
        ('gasoline', 'Gasoline'),
        ('diesel', 'Diesel'),
        ('ngv', 'NGV'),
        ('lpg', 'LPG')],
        string='Fuel Type',
        help='Fuel Used by the vehicle')
    x_payment_type = fields.Selection([
        ('fleet_card', 'Fleet Card'),
        ('cash', 'Cash')],
        string='Payment Type',
        help='Payment Type (Cash or Fleet Card)')
    x_distance = fields.Float(
        compute="_compute_fuel_consumption",
        string="Distance",
        group_operator="sum",
        store="True")

    @api.multi
    @api.depends('liter', 'odometer', 'x_last_refuel_odometer')
    def _compute_fuel_consumption(self):
        for fuel_log in self:
            distance = abs(fuel_log.odometer - fuel_log.x_last_refuel_odometer)
            if fuel_log.liter > 0:
                fuel_log.x_distance = distance
                fuel_log.x_fuel_consumption = distance / fuel_log.liter

    @api.onchange('vehicle_id')
    def _onchange_vehicle(self):
        super(FleetVehicleLogFuel, self)._onchange_vehicle()
        for record in self:
            if record.vehicle_id:
                vehicle_cost = self.env['fleet.vehicle.cost'].search([
                    ('vehicle_id', '=', record.vehicle_id.id),
                    ('cost_type', '=', 'fuel')],
                    order="id desc",
                    limit=1)
                record.x_last_refuel_odometer = vehicle_cost.odometer_id.value
