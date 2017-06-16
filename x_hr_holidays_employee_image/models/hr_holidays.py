# -*- coding: utf-8 -*-

from odoo import api, fields, models


class Holidays(models.Model):
    _inherit = 'hr.holidays'

    image = fields.Binary(
        related='employee_id.image',
        string="Employee Image")
    image_small = fields.Binary(
        related='employee_id.image_small',
        string="Employee Image (small)")
    image_medium = fields.Binary(
        related='employee_id.image_medium',
        string="Employee Image (medium)")

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        super(Holidays, self).onchange_employee_id()
        if self.employee_id:
            self.image_medium = self.employee_id.image
        else:
            self.image_medium = False
