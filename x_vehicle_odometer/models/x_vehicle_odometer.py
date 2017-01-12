# -*- coding: utf-8 -*-

from odoo import api, fields, models


class FleetVehicleOdometer(models.Model):
    _inherit = 'fleet.vehicle.odometer'

    def _default_driver(self):
        emp_ids = self.env[
            'hr.employee'].search([('user_id', '=', self.env.uid)])
        return emp_ids and emp_ids[0] or False

    x_description = fields.Text(string='Description')
    x_driver_id = fields.Many2one(
                    'hr.employee',
                    string='Driver',
                    default=_default_driver,
                    help='Driver of the vehicle')
