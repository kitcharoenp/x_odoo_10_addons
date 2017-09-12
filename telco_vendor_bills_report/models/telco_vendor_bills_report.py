# -*- coding: utf-8 -*-
# @author Kitcharoen Poolperm <kitcharoenp@gmail.com>
# @copyright Copyright (C) 2017
# @license http://opensource.org/licenses/gpl-3.0.html GNU Public License
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class TelcoVendorBillsReport(models.TransientModel):

    _name = 'telco.vendor.bills.report'
    _description = 'Telco Vendor Bills Report'

    def _default_due_date(self):
        r = 'month'
        if r == 'month':
            return time.strftime('%Y-%m-01')
        elif r == 'week':
            return (datetime.today() + relativedelta(
                    weekday=0, days=-6)).strftime('%Y-%m-%d')
        elif r == 'year':
            return time.strftime('%Y-01-01')
        return fields.date.context_today(self)

    def _default_issue_date(self):
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

    due_date = fields.Date(
        string='Due Date',
        required=True,
        default=_default_due_date)
    issue_date = fields.Date(
        string='Issue Date',
        required=True,
        default=_default_issue_date)
    project_ids = fields.Many2many(
        'project.project',
        string='Project',
        domain=[('active', '=', True)])

    @api.multi
    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        """
        if not data.get('project_ids'):
            raise UserError(_(
                'You have to select at least one Project. \
                And try again.'))
        """
        projects = self.env['project.project'].browse(
                            data['project_ids'])
        datas = {
            'ids': [],
            'model': 'project.project',
            'form': data
        }
        return self.env['report'].get_action(
            projects,
            'telco_vendor_bills_report.bills_report_template',
            data=datas)
