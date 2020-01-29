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
    x_location = fields.Char(
        string="Location",
        help='Location of the vehicle (garage, ...)')
    x_vin_sn = fields.Char(
        string='Label Sticker',
        help='Unique number written on the vehicle motor (VIN/SN number)',)
    x_project_id = fields.Many2one(
        'project.project',
        'Project',
        domain=[('active', '=', True)])       

    # Overide original method
    @api.onchange('liter', 'price_per_liter', 'amount')
    def _onchange_liter_price_amount(self):
        liter = float(self.liter)
        price_per_liter = float(self.price_per_liter)
        amount = float(self.amount)
        if amount > 0 and price_per_liter > 0 and round(amount / price_per_liter, 2) != liter:
            self.liter = round(amount / price_per_liter, 2)

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
                record.x_location = record.vehicle_id.location
                record.x_vin_sn = record.vehicle_id.vin_sn

    @api.multi
    def write(self, vals):
        if vals.get('vehicle_id'):
            vehicle = self.env['fleet.vehicle'].browse(vals.get('vehicle_id'))
            vals['x_location'] =vehicle.location
            vals['x_vin_sn'] = vehicle.vin_sn
        res = super(FleetVehicleLogFuel, self).write(vals)
        return res

    @api.model
    def create(self, vals):
         if vals.get('vehicle_id'):
             vehicle = self.env['fleet.vehicle'].browse(vals.get('vehicle_id'))
             vals['x_location'] = vehicle.location
             vals['x_vin_sn'] = vehicle.vin_sn
         res = super(FleetVehicleLogFuel, self).create(vals)
         return res
