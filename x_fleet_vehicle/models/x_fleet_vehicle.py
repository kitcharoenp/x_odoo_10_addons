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
