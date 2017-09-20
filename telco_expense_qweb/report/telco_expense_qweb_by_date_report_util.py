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

    def _thai_unit_process(self, val):
        thai_number = (
            "ศูนย์", "หนึ่ง", "สอง", "สาม", "สี่", "ห้า", "หก", "เจ็ด",
            "แปด", "เก้า")
        unit = ("", "สิบ", "ร้อย", "พัน", "หมื่น", "แสน", "ล้าน")
        length = len(val) > 1
        result = ''
        for index, current in enumerate(map(int, val)):
            if current:
                if index:
                    result = unit[index] + result

                if length and current == 1 and index == 0:
                    result += 'เอ็ด'
                elif index == 1 and current == 2:
                    result = 'ยี่' + result
                elif index != 1 or current != 1:
                    result = thai_number[current] + result
        return result

    def _thai_num2text(self, num_val):
        inverse_num_val = str(num_val)[::-1]
        n_list = [inverse_num_val[i:i + 6].rstrip("0") for i in range(
                                                0, len(inverse_num_val), 6)]
        result = self._thai_unit_process(n_list.pop(0))

        for i in n_list:
            result = self._thai_unit_process(i) + 'ล้าน' + result
        return result

    def _compute_amount_in_letter(self, float_val):
        float_val = format(float_val, ".2f")
        float_val_split = str(float_val).split('.')
        result = self._thai_num2text(float_val_split[0]) + "บาท"
        if len(float_val_split) > 1 and int(float_val_split[1][0:2]) > 0:
            result += self._thai_num2text(float_val_split[1][0:2]) + "สตางค์"
        return result

    def _get_data_for_report(self, data):
        res = []
        st_date = fields.Date.from_string(data['date_from'])
        en_date = fields.Date.from_string(data['date_to'])
        state = str(data['state'])
        employee_id = data['employee_id']
        Expense = self.env['hr.expense']
        if 'project_ids' in data:
            for project in self.env['project.project'].browse(
                    data['project_ids']):
                res.append({
                    'project_name': project.name,
                    'data': []})
                criteria = [
                    ('date', '<=', str(en_date)),
                    ('date', '>=', str(st_date))]
                if int(project.id) > 0:
                    criteria += [(
                        'analytic_account_id',
                        '=',
                        project.analytic_account_id.id)]
                if state in ['draft', 'reported', 'done', 'refused']:
                    criteria += [('state', '=', state)]
                if employee_id:
                    criteria += [(
                        'employee_id',
                        '=',
                        employee_id.id)]
                for exp in Expense.search(criteria, order="employee_id asc, \
                            date asc, \
                            reference asc"):
                    res[len(res)-1]['data'].append({
                        'name': exp.name,
                        'date': fields.Date.from_string(exp.date),
                        'reference': exp.reference,
                        'description': exp.description,
                        'employee': exp.employee_id.name,
                        'total_amount': exp.total_amount,
                        'code': exp.product_id.default_code,
                        'job_task': exp.product_id.description_purchase,
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
            'compute_amount_in_letter': self._compute_amount_in_letter,
            'description': data['form']['description'],
            'get_header_info': self._get_header_info(
                data['form']['date_from'],
                data['form']['date_to']),
            'get_data_for_report': self._get_data_for_report(data['form']),
        }
        return Report.render(
            'telco_expense_qweb.telco_expense_qweb_by_date_template', docargs)
