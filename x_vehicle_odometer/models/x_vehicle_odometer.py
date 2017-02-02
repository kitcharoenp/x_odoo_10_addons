# -*- coding: utf-8 -*-

from odoo import api, fields, models


class FleetVehicleOdometer(models.Model):
    _inherit = 'fleet.vehicle.odometer'

    x_description = fields.Text(
        string='Description')
    x_driver_id = fields.Many2one(
        'res.users',
        string='Driver',
        default=lambda self: self.env.user,
        help='Driver of the vehicle')
    y_odometer = fields.Float(
        string='Odometer End',
        group_operator="max")
