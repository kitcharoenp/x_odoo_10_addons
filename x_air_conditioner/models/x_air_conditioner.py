# -*- coding: utf-8 -*-

from odoo import api, fields, models


class MaintenanceEquipment(models.Model):
    _inherit = ['maintenance.equipment']

    is_airconditioner_component = fields.Boolean()

class MaintenanceRequest(models.Model):
    _inherit = ['maintenance.request']

    is_airconditioner_maintenance = fields.Boolean()
