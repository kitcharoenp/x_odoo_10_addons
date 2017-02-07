# -*- coding: utf-8 -*-
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class xTimesheetSummaryDepartment(models.TransientModel):

    _name = 'x_timesheet.summary.department'
    _description = 'Timesheet Summary Report By Department'

    def _default_date_from(self):
        user = self.env['res.users'].browse(self.env.uid)
        r = user.company_id and user.company_id.timesheet_range or 'month'
        if r == 'month':
            return time.strftime('%Y-%m-01')
        elif r == 'week':
            return (datetime.today() + relativedelta(weekday=0, days=-6)).strftime('%Y-%m-%d')
        elif r == 'year':
            return time.strftime('%Y-01-01')
        return fields.date.context_today(self)

    def _default_date_to(self):
        user = self.env['res.users'].browse(self.env.uid)
        r = user.company_id and user.company_id.timesheet_range or 'month'
        if r == 'month':
            return (datetime.today() + relativedelta(months=+1, day=1, days=-1)).strftime('%Y-%m-%d')
        elif r == 'week':
            return (datetime.today() + relativedelta(weekday=6)).strftime('%Y-%m-%d')
        elif r == 'year':
            return time.strftime('%Y-12-31')
        return fields.date.context_today(self)

    date_from = fields.Date(
        string='From',
        required=True,
        default=_default_date_from)
    date_to = fields.Date(
        string='To',
        required=True,
        default=_default_date_to)
    depts = fields.Many2many(
        'hr.department',
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
            'x_timesheet_summary_department.x_ts_dept_report_template',
            data=datas)
