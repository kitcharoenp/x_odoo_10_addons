# -*- coding: utf-8 -*-
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class xReportTimesheetPerDiem(models.TransientModel):

    _name = 'x_report.timesheet.perdiem'
    _description = 'Timesheet Per Diem Report'

    def _default_date_from(self):
        r = 'month'
        if r == 'month':
            return time.strftime('%Y-%m-01')
        elif r == 'week':
            return (datetime.today() + relativedelta(
                    weekday=0, days=-6)).strftime('%Y-%m-%d')
        elif r == 'year':
            return time.strftime('%Y-01-01')
        return fields.date.context_today(self)

    def _default_date_to(self):
        r = 'month'
        if r == 'month':
            return (datetime.today() + relativedelta(
                    months=+1, day=1, days=-1)).strftime('%Y-%m-%d')
        elif r == 'week':
            return (datetime.today() + relativedelta(
                    weekday=6)).strftime('%Y-%m-%d')
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
    employee_tag_ids = fields.Many2many(
        'hr.employee.category',
        string='Employee Tags')
    approved = fields.Boolean(
                    string='Approved')

    @api.multi
    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        if not data.get('employee_tag_ids'):
            raise UserError(_(
                'You have to select at least one Employee Tag. \
                And try again.'))
        employee_tags = self.env['hr.employee.category'].browse(
                            data['employee_tag_ids'])
        datas = {
            'ids': [],
            'model': 'hr.employee.category',
            'form': data
        }
        return self.env['report'].get_action(
            employee_tags,
            'x_report_timesheet_perdiem.x_report_ts_perdiem_template',
            data=datas)
