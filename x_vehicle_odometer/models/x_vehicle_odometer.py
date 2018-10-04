# -*- coding: utf-8 -*-

from odoo import api, fields, models


class FleetVehicleOdometer(models.Model):
    _inherit = 'fleet.vehicle.odometer'

    def _default_driver(self):
        emp_ids = self.env[
            'hr.employee'].search([('user_id', '=', self.env.uid)])
        return emp_ids and emp_ids[0] or False

    x_description = fields.Text(
        string='Description')
    x_driver_id = fields.Many2one(
        'hr.employee',
        string='Driver',
        default=_default_driver,
        help='Driver of the vehicle')
    y_odometer = fields.Float(
        string='Odometer End',
        group_operator="max")
    x_state_id = fields.Many2one(
        "res.country.state",
        string='State')
    x_project_id = fields.Many2one(
        'project.project',
        string='Project',
        domain=['|', ('active', '=', True), ('name', 'like', 'I0')])

    def _compute_vehicle_log_name(self):
        # super(FleetVehicleOdometer, self)._compute_vehicle_log_name()
        for record in self:
            name = record.vehicle_id.name
            if not name:
                name = record.date
            elif record.date:
                name += ' / ' + record.date
            record.name = name
