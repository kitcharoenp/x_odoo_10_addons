# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
# @author Kitcharoen Poolperm <kitcharoenp@gmail.com>
# @copyright Copyright (C) 2017
# @license http://opensource.org/licenses/gpl-3.0.html GNU Public License

from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models


class TelcoExpenseQwebByDateReportUtil(models.AbstractModel):
    # _name is format:
    # report.module_name.template_id
    _name = 'report.telco_expense_qweb.telco_expense_qweb_by_date_template'

    def _get_header_info(self, start_date, end_date):
        st_date = fields.Date.from_string(start_date)
        en_date = fields.Date.from_string(end_date)
        return {
            'start_date': fields.Date.to_string(st_date),
            'end_date': fields.Date.to_string(en_date),
            }

    def _get_day(self, start_date, end_date):
        res = []
        start_date = fields.Date.from_string(start_date)
        end_date = fields.Date.from_string(end_date)
        delta = end_date - start_date
        for x in range(delta.days + 1):
            color = '#ababab' if start_date.strftime('%a') == 'Sat' or start_date.strftime('%a') == 'Sun' else ''
            res.append({'day_str': start_date.strftime('%a'), 'day': start_date.day , 'color': color})
            start_date = start_date + relativedelta(days=1)
        return res

    def _get_data_for_report(self, data):
        res = []
        Expense = self.env['hr.expense']
        if 'project_ids' in data:
            for project in self.env['project.project'].browse(
                    data['project_ids']):
                res.append({
                    'project_name': project.name,
                    'data': [],
                    'color': self._get_day(
                        data['date_from'], data['date_to'])})
                for exp in Expense.search(
                        [('analytic_account_id', '=', project.analytic_account_id.id)],
                        order="id asc"):
                    res[len(res)-1]['data'].append({
                        'exp_name': exp.name,
                        'exp_date': exp.date,
                        'exp_reference': exp.reference,
                    })
        return res

    @api.model
    def render_html(self, docids, data=None):
        Report = self.env['report']
        # get report template from template id
        expense_report = Report._get_report_from_name(
            'telco_expense_qweb.telco_expense_qweb_by_date_template')
        hr_expenses = self.env['hr.expense'].browse(docids)
        docargs = {
            'doc_ids': docids,
            'doc_model': expense_report.model,
            'docs': hr_expenses,
            'get_header_info': self._get_header_info(
                data['form']['date_from'],
                data['form']['date_to']),
            'get_data_for_report': self._get_data_for_report(data['form']),
        }
        return Report.render(
            'telco_expense_qweb.telco_expense_qweb_by_date_template', docargs)
