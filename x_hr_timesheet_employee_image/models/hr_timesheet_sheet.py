# -*- coding: utf-8 -*-

from odoo import api, fields, models


class HrTimesheetSheet(models.Model):
    _inherit = 'hr_timesheet_sheet.sheet'

    image = fields.Binary(
        related='employee_id.image',
        string="Employee Image")
    image_small = fields.Binary(
        related='employee_id.image_small',
        string="Employee Image (small)")
    image_medium = fields.Binary(
        related='employee_id.image_medium',
        string="Employee Image (medium)")
    x_state_id = fields.Many2one(
        "res.country.state",
        related='employee_id.x_state_id',
        string='State')

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        super(HrTimesheetSheet, self).onchange_employee_id()
        if self.employee_id:
            self.image_medium = self.employee_id.image
        else:
            self.image_medium = False
