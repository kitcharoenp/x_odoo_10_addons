# -*- coding: utf-8 -*-

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp


class MaintenanceEquipment(models.Model):
    _inherit = ['maintenance.equipment']

    is_airconditioner_component = fields.Boolean()


class MaintenanceRequest(models.Model):
    _inherit = ['maintenance.request']

    is_airconditioner_maintenance = fields.Boolean()
    vendor_id = fields.Many2one(
        'res.partner',
        string='Vendor',
        domain="[('supplier','=',True)]")
    total_amount = fields.Float(
        string='Total',
        digits=dp.get_precision('Account'))
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        readonly=True,
        default=lambda self: self.env.user.company_id.currency_id)
