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
        user = self.env['res.users'].browse(self.env.uid)
        r = user.company_id and user.company_id.timesheet_range or 'month'
        if r == 'month':
            return time.strftime('%Y-%m-01')
        elif r == 'week':
            return (datetime.today() + relativedelta(
                    weekday=0, days=-6)).strftime('%Y-%m-%d')
        elif r == 'year':
            return time.strftime('%Y-01-01')
        return fields.date.context_today(self)

    def _default_date_to(self):
        user = self.env['res.users'].browse(self.env.uid)
        r = user.company_id and user.company_id.timesheet_range or 'month'
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
    analytic_account_ids = fields.Many2many(
        'account.analytic.account',
        string='Analytic Account')

    @api.multi
    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        if not data.get('analytic_account_ids'):
            raise UserError(_(
                'You have to select at least one Analytic Account. \
                And try again.'))
        analytic_accounts = self.env['account.analytic.account'].browse(
                            data['analytic_account_ids'])
        datas = {
            'ids': [],
            'model': 'account.analytic.account',
            'form': data
        }
        return self.env['report'].get_action(
            analytic_accounts,
            'telco_expense_qweb.telco_expense_qweb_by_date_template',
            data=datas)
