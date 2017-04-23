# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _


class HrTimesheetSheet(models.Model):
    _inherit = 'hr_timesheet_sheet.sheet'

    # get a default Reviewer from current user coach
    def _default_reviewer_get(self):
        employee = self.env['hr.employee'].search(
                [('user_id', '=', self.env.uid)], limit=1)
        return employee.x_administrator_id

    def _default_reviewer2_get(self):
        employee = self.env['hr.employee'].search(
                [('user_id', '=', self.env.uid)], limit=1)
        return employee.coach_id

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
                ('x_under_review', 'Under Review'),
                ('x_second_review', 'Second Review'),
                ('x_validate', 'Waiting Validation'),
                ('confirm', 'Waiting Approval'),
                ('done', 'Approved')],
                string='Status',
                select=True,
                required=True,
                readonly=True,
                index=True,
                track_visibility='onchange',
                help=' * The \'Draft\' status is used when a user is encoding a new \
                    and unconfirmed timesheet. \
            \n* The \'Validated\' status is used for to validate the \
                    timesheet by user. \
            \n* The \'Confirmed\' status is used for to confirm the timesheet \
                    by user. \
            \n* The \'Done\' status is used when users timesheet is accepted \
                    by his/her senior.')
    reviewer_id = fields.Many2one(
                    'hr.employee',
                    string='Reviewer',
                    readonly=True,
                    states={
                        'new': [('readonly', False)],
                        'draft': [('readonly', False)]},
                    default=_default_reviewer_get)
    reviewer_id2 = fields.Many2one(
                    'hr.employee',
                    string='Second Reviewer',
                    readonly=True,
                    states={
                        'new': [('readonly', False)],
                        'draft': [('readonly', False)]},
                    default=_default_reviewer2_get)
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
    summit_date = fields.Datetime(string='Summit Date')
    review_date = fields.Datetime(string='Review Date')
    second_review_date = fields.Datetime(string='Second Review Date')
    validated_date = fields.Datetime(string='Validated Date')
    approved_date = fields.Datetime(string='Approved Date')
    timesheet_ids = fields.One2many(
        'account.analytic.line',
        'sheet_id',
        string='Timesheet lines',
        readonly=False, states={
            'draft': [('readonly', False)],
            'new': [('readonly', False)]})

    @api.multi
    def action_timesheet_confirm(self):
        if self.filtered(lambda sheet: sheet.state != 'x_validate'):
            raise UserError(_("Cannot approve a non-submitted timesheet."))
        for sheet in self:
            if not sheet.can_approve:
                raise UserError(_(
                    'Only an Timesheet Manager or First Approval \
                    can validate timesheet.'))
        self.write({'validated_date': fields.Datetime.now()})
        super(HrTimesheetSheet, self).action_timesheet_confirm()
        if self.manager_id2 == self.manager_id1:
            self.write({
                'state': 'done',
                'approved_date': fields.Datetime.now()})
        return True

    @api.multi
    def action_timesheet_done(self):
        if self.filtered(lambda sheet: sheet.state != 'confirm'):
            raise UserError(_("Cannot approve a non-validated timesheet."))
        for sheet in self:
            if not sheet.can_approve:
                raise UserError(_(
                    'Only an Timesheet Manager or Second Approval can approve \
                    timesheet.'))
        self.write({'approved_date': fields.Datetime.now()})
        return super(HrTimesheetSheet, self).action_timesheet_done()

    @api.multi
    def action_timesheet_draft(self):
        for sheet in self:
            if not sheet.can_approve:
                raise UserError(_(
                    'Only an Timesheet Manager or Reviewer / Manager can Refuse timesheets \
                    or reset them to draft.'))
        return super(HrTimesheetSheet, self).action_timesheet_draft()

    @api.multi
    def action_timesheet_x_validate(self):
        for sheet in self:
            if not sheet.can_approve:
                raise UserError(_(
                    'Only an Timesheet Manager or Authority can Summit \
                    timesheet.'))
            if (sheet.employee_id and sheet.manager_id1 and
                    sheet.manager_id1.user_id):
                self.message_subscribe_users(
                    user_ids=[sheet.manager_id1.user_id.id])
        self.write({
            'state': 'x_validate',
            'second_review_date': fields.Datetime.now()})
        if self.reviewer_id2 == self.manager_id1:
            self.write({
                'state': 'confirm',
                'validated_date': fields.Datetime.now()})
        if (self.reviewer_id2 == self.manager_id1) and (
                self.manager_id1 == self.manager_id2):
            self.write({
                'state': 'done',
                'approved_date': fields.Datetime.now()})
        return True

    @api.multi
    def action_timesheet_x_second_review(self):
        for sheet in self:
            if not sheet.can_approve:
                raise UserError(_(
                    'Only an Timesheet Manager or Reviewer can Summit \
                    timesheet.'))
            if (sheet.employee_id and sheet.reviewer_id2 and
                    sheet.reviewer_id2.user_id):
                self.message_subscribe_users(
                    user_ids=[sheet.reviewer_id2.user_id.id])
        self.write({
            'state': 'x_second_review',
            'review_date': fields.Datetime.now()})
        if self.reviewer_id == self.reviewer_id2:
            self.write({
                'state': 'x_validate',
                'second_review_date': fields.Datetime.now()})
        if (self.reviewer_id == self.reviewer_id2) and (
                self.reviewer_id2 == self.manager_id1):
            self.write({
                'state': 'confirm',
                'validated_date': fields.Datetime.now()})
        if (self.reviewer_id == self.reviewer_id2) and (
                self.reviewer_id2 == self.manager_id1) and (
                        self.manager_id1 == self.manager_id2):
            self.write({
                'state': 'done',
                'approved_date': fields.Datetime.now()})
        return True

    @api.multi
    def action_timesheet_x_under_review(self):
        for sheet in self:
            if (sheet.employee_id and sheet.reviewer_id and
                    sheet.reviewer_id.user_id):
                self.message_subscribe_users(
                    user_ids=[sheet.reviewer_id.user_id.id])
        self.write({
            'state': 'x_under_review',
            'summit_date': fields.Datetime.now()})
        return True

    def _check_state(self):
        for line in self:
            if line.sheet_id and line.sheet_id.state not in ('draft', 'new'):
                raise UserError(_(
                    'You cannot modify an entry in a confirmed timesheet.'))
        return True

    @api.onchange('manager_id1')
    def _onchange_manager_id1(self):
        if self.manager_id1:
            self.manager_id2 = self.manager_id1.parent_id

    @api.multi
    def _compute_can_approve(self):
        """ User can approve a timesheet if it is its own first approval
            or if he is an Timesheet Manager.
        """
        user = self.env.user
        group_timesheet_manager = self.env.ref(
                    'x_hr_timesheet_sheet.x_group_hr_timesheet_manager')
        for timesheet in self:
            timesheet.can_approve = False
            if (timesheet.reviewer_id and timesheet.state == 'x_under_review'
                    and timesheet.reviewer_id.user_id == user):
                timesheet.can_approve = True
            if (timesheet.reviewer_id2 and timesheet.state == 'x_second_review'
                    and timesheet.reviewer_id2.user_id == user):
                timesheet.can_approve = True
            if (timesheet.manager_id1 and timesheet.state == 'x_validate'
                    and timesheet.manager_id1.user_id == user):
                timesheet.can_approve = True
            if (timesheet.manager_id2 and timesheet.state == 'confirm'
                    and timesheet.manager_id2.user_id == user):
                timesheet.can_approve = True
            if group_timesheet_manager in user.groups_id:
                timesheet.can_approve = True

    # validate user who can write the record
    @api.multi
    def write(self, vals):
        for sheet in self:
            if not sheet.can_approve and sheet.state not in ('draft', 'new'):
                raise UserError(_(
                    'In this status only the Reviewer/Manager can write \
                    this timesheet'))
        return super(HrTimesheetSheet, self).write(vals)
