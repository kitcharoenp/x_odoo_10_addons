# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError

from datetime import datetime, time
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
import pytz


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"
    _order = 'date desc, x_start_date asc'

    x_vehicle_id = fields.Many2one(
        'fleet.vehicle',
        string='Vehicle')
# fix me change default date format
    x_start_date = fields.Datetime(
        string='Start',
        default=fields.Datetime.from_string(
            fields.Datetime.now()).strftime('%Y-%m-%d 01:00:00'))
    x_end_date = fields.Datetime(
        string='End',
        default=fields.Datetime.from_string(
            fields.Datetime.now()).strftime('%Y-%m-%d 10:00:00'))
    x_notes = fields.Text(
        string='Note',)
    is_overtime = fields.Boolean(
        string='Overtime')
    x_odometer_id = fields.Many2one(
        'fleet.vehicle.odometer',
        string='Odometer',
        help='Odometer measure of the vehicle at the moment \
            of this activity')
    x_odometer = fields.Float(
        string='Odometer Start',
        compute="_get_odometer",
        inverse='_set_odometer',
        help='Odometer measure of the vehicle at the moment \
            of this activity start')
    y_odometer = fields.Float(
        string='Odometer End',
        help='Odometer measure of the vehicle at the moment \
            of this activity end')
    employee_ids = fields.Many2many(
        'hr.employee',
        string='Collaborators')
    x_overtime_pay = fields.Float(
        string='Overtime Pay')
    x_is_leave = fields.Boolean(
        string='Leave')
    x_is_holiday = fields.Boolean(
        string='Holiday')
    x_is_per_diem = fields.Boolean(
        string='Per Diem')
    x_state_id = fields.Many2one(
        "res.country.state",
        string='State')

    @api.onchange('x_start_date')
    def _compute_date_from_x_start_date(self):
        """ auto change 'date' onchange of 'x_start_date """
        for ts_line in self:
            if ts_line.x_start_date:
                start_datetime = ts_line.x_start_date
                timezone = pytz.timezone(self._context.get('tz') or 'UTC')

                attendance_dt = datetime.strptime(
                    start_datetime, DEFAULT_SERVER_DATETIME_FORMAT)
                att_tz_dt = pytz.utc.localize(attendance_dt)
                att_tz_dt = att_tz_dt.astimezone(timezone)
                att_tz_date_str = datetime.strftime(
                    att_tz_dt, DEFAULT_SERVER_DATE_FORMAT)
                ts_line.date = att_tz_date_str

    @api.constrains('x_start_date', 'x_end_date')
    def _check_validity_x_start_date_x_end_date(self):
        for ts_line in self:
            if ts_line.x_start_date and ts_line.x_end_date:
                """ Verifies if x_start_date is earlier than x_end_date."""
                if ts_line.x_end_date < ts_line.x_start_date:
                    raise ValidationError(_(
                        '"Start" time cannot be earlier than "End" time.'))

                domain = [
                    ('x_start_date', '<', ts_line.x_end_date),
                    ('x_end_date', '>', ts_line.x_start_date),
                    ('user_id', '=', ts_line.user_id.id),
                    ('id', '!=', ts_line.id),
                ]
                n_timesheet_lines = self.search_count(domain)
                if n_timesheet_lines:
                    raise ValidationError(_('You can not have 2 timesheet line that \
                        overlaps on same day!'))

    @api.onchange('x_notes')
    def _onchange_x_notes(self):
        for ts_line in self:
            if ts_line.x_notes:
                ts_line.name = ts_line.user_id.name + '/' + ts_line.x_start_date

    @api.onchange('unit_amount')
    def _onchange_unit_amount(self):
        for ts_line in self:
            if ts_line.unit_amount and ts_line.is_overtime:
                ts_line.x_overtime_pay = ts_line.unit_amount

    @api.onchange('x_start_date', 'x_end_date')
    def _compute_duration(self):
        """ auto calculate 'hours' onchange of 'x_start_date or x_end_date """
        diff_float = 0
        for ts_line in self:
            if ts_line.x_start_date:
                st_datetime = fields.Datetime.from_string(
                    ts_line.x_start_date)
                en_datetime = fields.Datetime.from_string(
                    ts_line.x_end_date)
                diff = en_datetime - st_datetime
                if(time(1, 00) <= st_datetime.time() <= time(5, 00)):
                    if(time(6, 00) <= en_datetime.time() <= time(10, 00)):
                        # del 1 hour for breaking lunch
                        diff_float = round(diff.total_seconds() / 3600.0, 2)-1
                else:
                    diff_float = round(diff.total_seconds() / 3600.0, 2)
                ts_line.unit_amount = diff_float

    @api.onchange('is_overtime')
    def _compute_duration_overtime(self):
        """ auto calculate 'hours' onchange of 'is_overtime """
        diff_float = 0
        for ts_line in self:
            if ts_line.x_start_date:
                st_datetime = fields.Datetime.from_string(
                    ts_line.x_start_date)
                en_datetime = fields.Datetime.from_string(
                    ts_line.x_end_date)
                diff = en_datetime - st_datetime
                if not ts_line.is_overtime:
                    if(time(1, 00) <= st_datetime.time() <= time(5, 00)):
                        if(time(6, 00) <= en_datetime.time() <= time(10, 00)):
                            # del 1 hour for breaking lunch
                            diff_float = round(
                                diff.total_seconds() / 3600.0, 2)-1
                else:
                    diff_float = round(diff.total_seconds() / 3600.0, 2)
                ts_line.unit_amount = diff_float

    @api.multi
    def write(self, values):
        # to do fix validate user to edit line by _check_owner methods
        # self._check_owner()
        return super(AccountAnalyticLine, self).write(values)

    def _check_owner(self):
        for line in self:
            user = self.env.user
            group_timesheet_manager = self.env.ref(
                        'x_hr_timesheet_sheet.x_group_hr_timesheet_manager')
            if (user != line.user_id):
                    if (group_timesheet_manager not in user.groups_id):
                        if (user != line.sheet_id.reviewer_id.user_id
                                or user != line.sheet_id.manager_id1.user_id
                                or user != line.sheet_id.manager_id2.user_id):
                            raise UserError(_('You cannot modify this entry \
                                because you is not Manager/Coach \
                                of this employee.'))
        return True

    # overide _check_state() method.
    def _check_state(self):
        for line in self:
            user = self.env.user
            group_hr_timesheet_officer = self.env.ref(
                        'hr_timesheet.group_hr_timesheet_user')
            if group_hr_timesheet_officer not in user.groups_id:
                if (line.sheet_id and
                        line.sheet_id.state not in ('draft', 'new')):
                    raise UserError(_('You cannot modify an entry in a \
                        confirmed timesheet'))
        return True

    def _get_odometer(self):
        for record in self:
            if record.x_odometer_id:
                record.x_odometer = record.x_odometer_id.value
                record.y_odometer = record.x_odometer_id.y_odometer

    def _check_start_end_odometer(self):
        for record in self:
            if record.x_vehicle_id:
                if record.x_odometer > record.y_odometer:
                    raise ValidationError(_(
                        "the Odometer Start value must been less \
                        than Odometer End value (%s).") % record.x_notes)

    def _check_overlap_odometer(self):
        odometer_obj = self.env['fleet.vehicle.odometer']
        for record in self:
            domain_overlap = [
                ('value', '<', record.y_odometer),
                ('y_odometer', '>', record.x_odometer),
                ('vehicle_id', '=', record.x_vehicle_id.id),
                ('id', '!=', record.x_odometer_id.id)]
            n_odometer_overlaps = odometer_obj.search_count(domain_overlap)
            if n_odometer_overlaps > 0:
                raise ValidationError(_("You can not have 2 odometer line that \
                    overlaps (%s).") % record.x_notes)

    @api.depends('x_vehicle_id')
    def _set_odometer(self):
        odometer_obj = self.env['fleet.vehicle.odometer']
        for record in self:
            self._check_start_end_odometer()
            # domain for search duplicate odometer
            domain = [
                    ('value', '=', record.x_odometer),
                    ('y_odometer', '=', record.y_odometer),
                    ('vehicle_id', '=', record.x_vehicle_id.id),
                    ('id', '!=', record.x_odometer_id.id)]
            vehicle_odometer = odometer_obj.search(
                        domain, limit=1, order='value desc')
            # Search employee_id from user_id
            employee = self.env['hr.employee'].search(
                    [('user_id', '=', record.user_id.id)], limit=1)
            if employee:
                employee_id = employee and employee[0].id

            # if not duplicate odometer then create the new one with validate
            # overlap else update exist
            if vehicle_odometer:
                self.x_odometer_id = vehicle_odometer
            else:
                # self._check_overlap_odometer()
                if not self.x_odometer_id and record.x_vehicle_id.id:
                    odometer = odometer_obj.create({
                        'value': record.x_odometer,
                        'y_odometer': record.y_odometer,
                        'date': record.date or fields.Date.context_today(record),
                        'vehicle_id': record.x_vehicle_id.id,
                        'x_description': record.x_notes,
                        'x_driver_id': employee_id or False,
                        })
                    self.x_odometer_id = odometer
