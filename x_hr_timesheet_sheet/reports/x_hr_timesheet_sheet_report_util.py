# -*- coding: utf-8 -*-

from datetime import timedelta, datetime
from odoo import api, fields, models, _


class HrTimesheetSheetReportUtil(models.AbstractModel):
    # _name = 'report.module.report_name'
    # module : directory name of your module.
    # report_name : report id.
    _name = 'report.x_hr_timesheet_sheet.x_timesheet_weekly_report_template'

    @api.model
    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name(
            'x_hr_timesheet_sheet.x_timesheet_weekly_report_template')
        records = self.env['hr_timesheet_sheet.sheet'].browse(docids)
        docargs = {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': records,
            'datetime': datetime,
            'timedelta': timedelta,
        }
        return report_obj.render(
            'x_hr_timesheet_sheet.x_timesheet_weekly_report_template', docargs)
