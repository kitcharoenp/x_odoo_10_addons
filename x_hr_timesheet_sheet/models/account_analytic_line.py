# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

from datetime import datetime
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

    @api.onchange('x_notes')
    def _onchange_x_notes(self):
        for ts_line in self:
            if ts_line.x_notes:
                ts_line.name = ts_line.x_notes
