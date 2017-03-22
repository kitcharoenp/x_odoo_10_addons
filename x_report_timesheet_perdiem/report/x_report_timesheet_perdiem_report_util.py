# -*- coding: utf-8 -*-

from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models


class xTimesheetPerdiemReportUtil(models.AbstractModel):
    # _name is format:
    # report.module_name.template_id
    _name = 'report.x_report_timesheet_perdiem.x_report_ts_perdiem_template'

    def _get_header_info(self, start_date, end_date):
        st_date = fields.Date.from_string(start_date)
        en_date = fields.Date.from_string(end_date)
        return {
            'start_date': fields.Date.to_string(st_date),
            'end_date': fields.Date.to_string(en_date)}

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

    def _get_months(self, start_date, end_date):
        # it works for geting month name between two dates.
        res = []
        start_date = fields.Date.from_string(start_date)
        end_date = fields.Date.from_string(end_date)
        while start_date <= end_date:
            last_date = start_date + relativedelta(day=1, months=+1, days=-1)
            if last_date > end_date:
                last_date = end_date
            month_days = (last_date - start_date).days + 1
            res.append(
                {'month_name': start_date.strftime('%B'), 'days': month_days})
            start_date += relativedelta(day=1, months=+1)
        return res

    def _get_timesheet_summary(
            self, start_date, end_date, approved, user_id, user_barcode):
        res = []
        count = 0
        start_date = fields.Date.from_string(start_date)
        end_date = fields.Date.from_string(end_date)
        delta = end_date - start_date
        for index in range(delta.days + 1):
            current = start_date + timedelta(index)
            res.append({
                'day': current.day,
                'date': current,
                'color': '',
                'description': [],
                'province': [],
                'vehicle': []})
            if current.strftime('%a') == 'Sat' or \
                    current.strftime('%a') == 'Sun':
                res[index]['color'] = '#ababab'

        # get analytic line summary details.
        analytic_lines = self.env['account.analytic.line'].search([
                ('user_id', '=', user_id),
                ('x_start_date', '<=', str(end_date)),
                ('x_end_date', '>=', str(start_date)),
                ('x_is_per_diem', '=', True)])

        for line in analytic_lines:
            # Convert date to user timezone, otherwise the report will
            # not be consistent with the value displayed in the interface.
            x_start_date = fields.Datetime.from_string(line.x_start_date)
            date_from = fields.Datetime.context_timestamp(
                            line, x_start_date).date()

            x_end_date = fields.Datetime.from_string(line.x_end_date)
            date_to = fields.Datetime.context_timestamp(
                            line, x_end_date).date()

            for index in range(0, ((date_to - date_from).days + 1)):
                if date_from >= start_date and date_from <= end_date:
                    res[(date_from-start_date).days][
                            'description'] = line.x_notes
                    res[(date_from-start_date).days][
                            'province'] = line.x_state_id.name
                    res[(date_from-start_date).days][
                            'vehicle'] = line.x_vehicle_id.license_plate
                date_from += timedelta(1)
            # count line match condtion
            count += 1
        self.sum = round(count, 0)
        return res

    def _get_data_for_report(self, data):
        res = []
        Employee = self.env['hr.employee']
        if 'employee_tag_ids' in data:
            # loop by employee tags
            for employee_tag in self.env['hr.employee.category'].browse(
                    data['employee_tag_ids']):
                res.append({
                    'employee_tag': employee_tag.name,
                    'data': [],
                    'color': self._get_day(
                        data['date_from'], data['date_to'])})
                # loop by employee in each tags
                for emp in Employee.search(
                        [('category_ids', 'in', employee_tag.id)],
                        order="work_location asc, barcode asc"):
                    res[len(res)-1]['data'].append({
                        'emp': emp.name,
                        'emp_job': emp.job_id.name,
                        'emp_department': emp.department_id.name,
                        'emp_mobile_phone': emp.mobile_phone,
                        'emp_barcode': emp.barcode,
                        'emp_signature': emp.x_signature_img,
                        'work_location': emp.work_location,
                        'emp_bank_account_id': emp.bank_account_id.acc_number,
                        'emp_bank_account': emp.bank_account_id.bank_name,
                        'month': fields.Date.from_string(
                                    data['date_to']).strftime('%B'),
                        'year': fields.Date.from_string(
                                    data['date_to']).strftime('%Y'),
                        # call method to get the timesheet line
                        'display': self._get_timesheet_summary(
                            data['date_from'],
                            data['date_to'],
                            data['approved'],
                            emp.user_id.id,
                            emp.barcode),
                        'sum': self.sum
                    })
        return res

    @api.model
    def render_html(self, docids, data=None):
        Report = self.env['report']
        # get report template from template id
        timesheet_report = Report._get_report_from_name(
            'x_report_timesheet_perdiem.x_report_ts_perdiem_template')
        analytic_lines = self.env['account.analytic.line'].browse(self.ids)
        docargs = {
            'doc_ids': self.ids,
            'doc_model': timesheet_report.model,
            'docs': analytic_lines,
            'get_header_info': self._get_header_info(
                data['form']['date_from'],
                data['form']['date_to']),
            'get_day': self._get_day(
                data['form']['date_from'],
                data['form']['date_to']),
            'get_months': self._get_months(
                data['form']['date_from'],
                data['form']['date_to']),
            'get_data_for_report': self._get_data_for_report(data['form']),
        }
        return Report.render(
            'x_report_timesheet_perdiem.x_report_ts_perdiem_template', docargs)
