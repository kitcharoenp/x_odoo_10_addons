# -*- coding: utf-8 -*-

from odoo import api, fields, models


class HrTimesheetSheet(models.Model):
    _inherit = 'hr_timesheet_sheet.sheet'

    # get a default first Manager from current user Manager
    def _default_manager1_get(self):
        employee = self.env['hr.employee'].search(
                [('user_id', '=', self.env.uid)], limit=1)
        return employee.parent_id

    # get a Second Manager from Manager of present User
    def _default_manager2_get(self):
        employee = self.env['hr.employee'].search(
                [('user_id', '=', self.env.uid)], limit=1)
        return employee.parent_id.parent_id

    state = fields.Selection([
                ('new', 'New'),
                ('draft', 'Open'),
                ('x_validate', 'Waiting Validation'),
                ('confirm', 'Waiting Approval'),
                ('done', 'Approved')],
                string='Status',
                select=True,
                required=True,
                readonly=True,
                track_visibility='onchange',
                help=' * The \'Draft\' status is used when a user is encoding a new \
                    and unconfirmed timesheet. \
            \n* The \'Validated\' status is used for to validate the \
                    timesheet by user. \
            \n* The \'Confirmed\' status is used for to confirm the timesheet \
                    by user. \
            \n* The \'Done\' status is used when users timesheet is accepted \
                    by his/her senior.')
    manager_id1 = fields.Many2one(
                    'hr.employee',
                    string='First Approval',
                    default=_default_manager1_get,
                    copy=False)
    manager_id2 = fields.Many2one(
                    'hr.employee',
                    string='Second Approval',
                    default=_default_manager2_get,
                    copy=False)

    @api.multi
    def action_timesheet_confirm(self):
        return super(HrTimesheetSheet, self).action_timesheet_confirm()

    @api.multi
    def action_timesheet_x_validate(self):
        for sheet in self:
            if (sheet.employee_id and sheet.employee_id.parent_id and
                    sheet.employee_id.parent_id.user_id):
                self.message_subscribe_users(
                    user_ids=[sheet.employee_id.parent_id.user_id.id])
        self.write({'state': 'x_validate'})
        return True

    def _check_state(self):
        for line in self:
            if line.sheet_id and line.sheet_id.state not in ('draft', 'new'):
                raise UserError(_('You cannot modify an entry in a confirmed timesheet.'))
        return True
