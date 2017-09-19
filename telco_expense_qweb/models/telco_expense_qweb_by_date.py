# -*- coding: utf-8 -*-
# @author Kitcharoen Poolperm <kitcharoenp@gmail.com>
# @copyright Copyright (C) 2017
# @license http://opensource.org/licenses/gpl-3.0.html GNU Public License
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class TelcoExpenseReportByDate(models.TransientModel):

    _name = 'telco.expense.qweb.by.date'
    _description = 'Telco Expense Qweb Report by Date'

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
    project_ids = fields.Many2many(
        'project.project',
        string='Project',
        domain=[('active', '=', True)])
    description = fields.Text()
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('reported', 'Reported'),
        ('done', 'Posted'),
        ('refused', 'Refused')],
        string='Status',
        help="Status of the expense.")

    @api.multi
    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        if not data.get('project_ids'):
            raise UserError(_(
                'You have to select at least one Project. \
                And try again.'))
        projects = self.env['project.project'].browse(
                            data['project_ids'])
        datas = {
            'ids': [],
            'model': 'project.project',
            'form': data
        }
        return self.env['report'].get_action(
            projects,
            'telco_expense_qweb.telco_expense_qweb_by_date_template',
            data=datas)
