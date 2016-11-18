# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _


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
                    required=True,
                    readonly=True,
                    states={
                        'new': [('readonly', False)],
                        'draft': [('readonly', False)]},
                    default=_default_manager1_get,
                    copy=False)
    manager_id2 = fields.Many2one(
                    'hr.employee',
                    string='Second Approval',
                    readonly=True,
                    states={
                        'new': [('readonly', False)],
                        'draft': [('readonly', False)]},
                    default=_default_manager2_get,
                    copy=False)
    can_approve = fields.Boolean(
                    string='Can approve',
                    compute='_compute_can_approve')

    @api.multi
    def action_timesheet_confirm(self):
        if self.filtered(lambda sheet: sheet.state != 'x_validate'):
            raise UserError(_("Cannot approve a non-submitted timesheet."))
        for sheet in self:
            if not sheet.can_approve:
                raise UserError(_(
                    'Only an HR Manager or First Approval \
                    can validate timesheet.'))
        return super(HrTimesheetSheet, self).action_timesheet_confirm()

    @api.multi
    def action_timesheet_done(self):
        if self.filtered(lambda sheet: sheet.state != 'confirm'):
            raise UserError(_("Cannot approve a non-validated timesheet."))
        for sheet in self:
            if not sheet.can_approve:
                raise UserError(_(
                    'Only an HR Manager or Second Approval can approve \
                    timesheet.'))
        return super(HrTimesheetSheet, self).action_timesheet_done()

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
                raise UserError(_(
                    'You cannot modify an entry in a confirmed timesheet.'))
        return True

    @api.onchange('manager_id1')
    def _onchange_manager_id1(self):
            self.manager_id2 = self.manager_id1.parent_id

    @api.multi
    def _compute_can_approve(self):
        """ User can approve a timesheet if it is its own first approve
            or if he is an Hr Manager.
        """
        user = self.env.user
        group_timesheet_manager = self.env.ref(
                    'hr_timesheet.group_hr_timesheet_user')
        for timesheet in self:
            timesheet.can_approve = False
            if (timesheet.manager_id1 and timesheet.state == 'x_validate' and
                    timesheet.manager_id1.user_id == user):
                timesheet.can_approve = True
            if (timesheet.manager_id2 and timesheet.state == 'confirm' and
                    timesheet.manager_id2.user_id == user):
                timesheet.can_approve = True
