# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    x_vehicle_id = fields.Many2one(
        'fleet.vehicle',
        string='Vehicle')
    x_asset_number = fields.Char('Asset Number', copy=False)
