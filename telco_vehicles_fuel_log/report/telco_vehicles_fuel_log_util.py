# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
# @author Kitcharoen Poolperm <kitcharoenp@gmail.com>
# @copyright Copyright (C) 2017
# @license http://opensource.org/licenses/gpl-3.0.html GNU Public License

from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
"""
import numpy as np
import matplotlib as mpl

## agg backend is used to create plot as a .png file
mpl.use('agg')

import matplotlib.pyplot as plt
"""
import pandas as pd

class TelcoVehiclesFuelLogReportUtil(models.AbstractModel):
    # _name is format:
    # report.module_name.template_id
    _name = 'report.telco_vehicles_fuel_log.fuel_log_report_template'

    def _get_data_for_report(self, data):
        res = []
        start_date = fields.Date.from_string(data['start_date'])
        end_date = fields.Date.from_string(data['end_date'])
        LogFuels = self.env['fleet.vehicle.log.fuel']

        for vehicle in self.env['fleet.vehicle'].search([('active', '=', True)]):
            amount = []
            x_distance = 0
            liter = 0
            # Find fuel log where date and between end_date and start_date vehicle id
            fuel_logs =  LogFuels.search([('date', '<=', end_date),
                                ('date', '>=', start_date),
                                ('vehicle_id', '=', vehicle.id)])

            for fuel_log in fuel_logs:
                amount +=  [fuel_log.amount]

            df = pd.Series(amount)
            stat = df.describe()

            res.append({
                'vehicle_name': vehicle.name,
                'amount': amount,
                'count':  stat['count'],
                'mean':   stat['mean'],
                'std':    stat['std'],
                'min':    stat['min'],
                '25%':    stat['25%'],
                '50%':    stat['50%'],
                '75%':    stat['75%'],
                'max':    stat['max'],
            })

        return res

    def _get_data(self, data):
        res = self._get_data_for_report(data)
        return res

    @api.model
    def render_html(self, docids, data=None):
        Report = self.env['report']
        # get report template from template id
        vehicles_fuel_log_report = Report._get_report_from_name(
            'telco_vehicles_fuel_log.fuel_log_report_template')
        LogFuel = self.env['fleet.vehicle.log.fuel'].browse(docids)
        docargs = {
            'doc_ids': docids,
            'doc_model': vehicles_fuel_log_report.model,
            'docs': LogFuel,
            '_get_data': self._get_data(data['form']),
        }
        return Report.render(
            'telco_vehicles_fuel_log.fuel_log_report_template',
            docargs)
