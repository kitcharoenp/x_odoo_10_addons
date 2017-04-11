# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _


class Holidays(models.Model):
    _inherit = "hr.holidays"

    x_can_approve = fields.Boolean(
                    string='Can approve',
                    compute='_compute_can_approve')

    @api.onchange('employee_id')
    def _onchange_employee(self):
        super(Holidays, self)._onchange_employee()
        self.manager_id = self.employee_id.coach_id
        self.manager_id2 = self.employee_id.department_id.manager_id

    @api.multi
    def _compute_can_approve(self):
        """ User can approve a leave if it is its own first/second approval
            or if he is an Holidays Manager.
        """
        user = self.env.user
        group_holidays_manager = self.env.ref(
                    'hr_holidays.group_hr_holidays_manager')
        for holiday in self:
            holiday.x_can_approve = False
            if (holiday.manager_id and holiday.state == 'confirm'
                    and holiday.manager_id.user_id == user):
                holiday.x_can_approve = True
            if (holiday.manager_id2 and holiday.state == 'validate1'
                    and holiday.manager_id2.user_id == user):
                holiday.x_can_approve = True
            if group_holidays_manager in user.groups_id:
                holiday.x_can_approve = True

    def _get_project(self):
        project_obj = self.env['project.project']
        # find the analytic_account corresponding to the company name
        company_id = self.employee_id.company_id
        project = project_obj.search([
                ('name', '=', company_id.name),
                ('company_id', '=', company_id.id)],
                limit=1)
        if not project:
            project = project_obj.create({
                'name': company_id.name,
                'company_id': company_id.id,
                'allow_timesheets': True,
            })
        return project

    @api.multi
    def _create_ts_analytic_line(self):
        """ This method will create a analytic line in timesheet object
            at the time of holidays validated
        """
        project = self._get_project()
        for holiday in self:
            self.env['account.analytic.line'].create({
                'x_holiday_id': holiday.id,
                'name': holiday.display_name,
                'x_notes': holiday.display_name,
                'project_id': project.id,
                'account_id': project.analytic_account_id.id,
                'user_id': holiday.employee_id.user_id.id,
                'unit_amount': holiday.number_of_days_temp * 8,
                'x_start_date': holiday.date_from,
                'x_end_date': holiday.date_to,
                'x_is_leave': True,
            })
        return True

    @api.multi
    def _remove_ts_analytic_line(self):
        """ This method will remove a analytic line in timesheet object
            at the time of holidays cancel/removed
        """
        return self.env['account.analytic.line'].search(
                [('x_holiday_id', 'in', self.ids)]).unlink()

    @api.multi
    def action_approve(self):
        """ validate user before action_approve
        """
        for holiday in self:
            if not holiday.x_can_approve:
                raise UserError(_('Only an HR Officer or Manager can \
                    approve leave requests.'))
        res = super(Holidays, self).action_approve()
        return res

    @api.multi
    def action_validate(self):
        """ validate user before action_validate
        """
        for holiday in self:
            if not holiday.x_can_approve:
                raise UserError(_('Only an HR Officer or Manager can \
                    approve leave requests.'))
        res = super(Holidays, self).action_validate()
        self._create_ts_analytic_line()
        return res

    @api.multi
    def action_refuse(self):
        res = super(Holidays, self).action_refuse()
        self._remove_ts_analytic_line()
        return res

    @api.multi
    def name_get(self):
        res = super(Holidays, self).name_get()
        res = []
        for leave in self:
            res.append((leave.id, _("%s on %s : %.2f Hours") % (
                leave.employee_id.name or leave.category_id.name,
                leave.holiday_status_id.name,
                leave.number_of_days_temp * 8)))
        return res
