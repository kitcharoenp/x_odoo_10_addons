# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import time

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class xTimesheetSummaryDepartment(models.TransientModel):

    _name = 'x_timesheet.summary.department'
    _description = 'Timesheet Summary Report By Department'

    date_from = fields.Date(
        string='From',
        required=True,
        default=lambda *a: time.strftime('%Y-%m-01'))
    date_to = fields.Date(
        string='To',
        required=True)
    depts = fields.Many2many(
        'hr.department',
        'summary_dept_rel',
        'sum_id',
        'dept_id',
        string='Department(s)')

    @api.multi
    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        if not data.get('depts'):
            raise UserError(_(
                'You have to select at least one Department. And try again.'))
        departments = self.env['hr.department'].browse(data['depts'])
        datas = {
            'ids': [],
            'model': 'hr.department',
            'form': data
        }
        return self.env['report'].get_action(
            departments,
            'x_timesheet_summary_department.x_timesheet_summary_department_report_template',
            data=datas)
