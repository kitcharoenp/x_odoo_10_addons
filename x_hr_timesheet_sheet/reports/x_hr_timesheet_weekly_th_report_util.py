# -*- coding: utf-8 -*-

from datetime import timedelta
from odoo import api, fields, models


class HrTimesheetWeeklyThReportUtil(models.AbstractModel):
    # _name = 'report.module.report_name'
    # module : directory name of your module.
    # report_name : report id.
    _name = 'report.x_hr_timesheet_sheet.x_weekly_th_report_template'

    def get_day(self, obj):
        start_date = fields.Date.from_string(obj.date_from)
        end_date = fields.Date.from_string(obj.date_to)
        res = start_date
        while res <= end_date:
            yield res
            res += timedelta(days=1)

    @api.model
    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name(
            'x_hr_timesheet_sheet.x_weekly_th_report_template')
        records = self.env['hr_timesheet_sheet.sheet'].browse(docids)
        docargs = {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': records,
            'get_day': self.get_day,
        }
        return report_obj.render(
            'x_hr_timesheet_sheet.x_weekly_th_report_template',
            docargs)
