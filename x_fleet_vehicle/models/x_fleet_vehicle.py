# -*- coding: utf-8 -*-

from odoo import api, fields, models


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    def _default_driver(self):
        emp_ids = self.env[
            'hr.employee'].search([('user_id', '=', self.env.uid)])
        return emp_ids and emp_ids[0] or False

    x1_driver_id = fields.Many2one(
        'hr.employee',
        string='First Driver',
        default=_default_driver,
        help='Driver of the vehicle')

    x2_driver_id = fields.Many2one(
        'hr.employee',
        string='Second Driver')
