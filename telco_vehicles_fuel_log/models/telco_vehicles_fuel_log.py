# -*- coding: utf-8 -*-
# @author Kitcharoen Poolperm <kitcharoenp@gmail.com>
# @copyright Copyright (C) 2017
# @license http://opensource.org/licenses/gpl-3.0.html GNU Public License
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class TelcoVehiclesFuelLog(models.TransientModel):

    _name = 'telco.vehicles.fuel.log'
    _description = 'Telco Vehicles Fuel Log'

    def _default_start_date(self):
        r = 'month'
        if r == 'month':
            return (datetime.today() + relativedelta(
                    months=-6, day=1, days=-1)).strftime('%Y-%m-%d')
        return fields.date.context_today(self)

    def _default_end_date(self):
        r = 'month'
        if r == 'month':
            return (datetime.today() + relativedelta(
                    months=+1, day=1, days=-1)).strftime('%Y-%m-%d')

        return fields.date.context_today(self)

    start_date = fields.Date(
        string='Start Date',
        required=True,
        default=_default_start_date)
    end_date = fields.Date(
        string='End Date',
        default=_default_end_date)

    @api.multi
    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': [],
            'form': data
        }
        return self.env['report'].get_action(
                    self,
                    'telco_vehicles_fuel_log.fuel_log_report_template',
                    data=datas)
