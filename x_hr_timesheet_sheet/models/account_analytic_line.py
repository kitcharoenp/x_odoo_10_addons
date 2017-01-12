# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError

from datetime import datetime, time
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

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
    date = fields.Date(
        compute='_compute_date_from_x_start_date',
        string='Date',
        index=True)
    x_notes = fields.Text(
        string='Note',)
    is_overtime = fields.Boolean(
        string='Overtime')
    x_odometer_id = fields.Many2one(
        'fleet.vehicle.odometer',
        string='Odometer',
        help='Odometer measure of the vehicle at the moment of this activity')
    x_odometer = fields.Float(
        string='Odometer Value',
        compute="_get_odometer",
        inverse='_set_odometer',
        help='Odometer measure of the vehicle at the moment of this activity')

    @api.onchange('x_start_date')
    def _compute_date_from_x_start_date(self):
        """ auto change 'date' onchange of 'x_start_date """
        for ts_line in self:
            if ts_line.x_start_date:
                ts_line.date = datetime.strptime(
                    ts_line.x_start_date,
                    DEFAULT_SERVER_DATETIME_FORMAT).date()

    @api.constrains('x_start_date', 'x_end_date')
    def _check_validity_x_start_date_x_end_date(self):
        """ verifies if x_start_date is earlier than x_end_date.
            verifies if x_start_date is not same date x_end_date.
        """
        for ts_line in self:
            if ts_line.x_start_date and ts_line.x_end_date:
                if ts_line.x_end_date < ts_line.x_start_date:
                    raise ValidationError(_(
                        '"Start" time cannot be earlier than "End" time.'))

                d1 = datetime.strptime(
                    ts_line.x_start_date,
                    DEFAULT_SERVER_DATETIME_FORMAT).date()
                d2 = datetime.strptime(
                    ts_line.x_end_date,
                    DEFAULT_SERVER_DATETIME_FORMAT).date()

                if d1 != d2:
                    raise ValidationError(_(
                        '"Start" time must be the same date "End" time.'))

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
                ts_line.name = ts_line.x_notes

    @api.onchange('x_start_date', 'x_end_date')
    def _compute_duration(self):
        """ auto calculate 'hours' onchange of 'x_start_date """
        diff_float = 0
        for ts_line in self:
            if ts_line.x_start_date:
                st_datetime = fields.Datetime.from_string(
                    self.x_start_date)
                en_datetime = fields.Datetime.from_string(
                    self.x_end_date)
                diff = en_datetime - st_datetime
                if(time(1, 00) <= st_datetime.time() <= time(5, 00)):
                    if(time(6, 00) <= en_datetime.time() <= time(10, 00)):
                        # del 1 hour for breaking lunch
                        diff_float = round(diff.total_seconds() / 3600.0, 2)-1
                else:
                    diff_float = round(diff.total_seconds() / 3600.0, 2)
                ts_line.unit_amount = diff_float

    @api.multi
    def write(self, values):
        self._check_owner()
        return super(AccountAnalyticLine, self).write(values)

    def _check_owner(self):
        for line in self:
            user = self.env.user
            group_timesheet_manager = self.env.ref(
                        'x_hr_timesheet_sheet.x_group_hr_timesheet_manager')
            if (line.user_id != user and
                    group_timesheet_manager not in user.groups_id):
                raise UserError(_('You cannot modify entry that do not \
                    belong to you.'))
        return True

    # overide _check_state() method.
    def _check_state(self):
        for line in self:
            user = self.env.user
            group_timesheet_manager = self.env.ref(
                        'x_hr_timesheet_sheet.x_group_hr_timesheet_manager')
            if group_timesheet_manager not in user.groups_id:
                if (line.sheet_id and
                        line.sheet_id.state not in ('draft', 'new')):
                    raise UserError(_('You cannot modify an entry in a \
                        confirmed timesheet.'))
        return True

    def _get_odometer(self):
        for record in self:
            if record.x_odometer_id:
                record.x_odometer = record.x_odometer_id.value

    def _set_odometer(self):
        for record in self:
            if record.x_vehicle_id:
                if not record.x_odometer:
                    raise UserError(_(
                        'Emptying the odometer value of a vehicle is not allowed.'))
            odometer = self.env['fleet.vehicle.odometer'].create({
                'value': record.x_odometer,
                'date': record.date or fields.Date.context_today(record),
                'vehicle_id': record.x_vehicle_id.id,
                'x_description': record.x_notes,
                'x_driver_id': record.user_id.id,
            })
            self.x_odometer_id = odometer
