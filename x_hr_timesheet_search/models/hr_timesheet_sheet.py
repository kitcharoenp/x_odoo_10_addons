# -*- coding: utf-8 -*-

from odoo import api, fields, models


class HrTimesheetSheet(models.Model):
    _inherit = 'hr_timesheet_sheet.sheet'

    x_had_overtime = fields.Boolean(
                    string='Has Overtime',
                    store=True,
                    readonly=True,
                    compute='_compute_had_overtime')
    x_had_perdiem = fields.Boolean(
                    string='Has Per Diem',
                    store=True,
                    readonly=True,
                    compute='_compute_had_perdiem')

    @api.multi
    @api.depends('timesheet_ids')
    def _compute_had_overtime(self):
        for sheet in self:
            for line in sheet.timesheet_ids:
                if line.is_overtime:
                    sheet.x_had_overtime = True
                    break

    @api.multi
    @api.depends('timesheet_ids')
    def _compute_had_perdiem(self):
        for sheet in self:
            for line in sheet.timesheet_ids:
                if line.x_is_per_diem:
                    sheet.x_had_perdiem = True
                    break
