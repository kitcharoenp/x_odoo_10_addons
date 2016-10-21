# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError

from datetime import datetime
from dateutil.relativedelta import relativedelta


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    x_vehicle_id = fields.Many2one(
        'fleet.vehicle',
        string='Vehicle')
    x_start_date = fields.Datetime('Start')
    x_end_date = fields.Datetime('End')
