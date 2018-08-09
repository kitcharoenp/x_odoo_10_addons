# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
# @author Kitcharoen Poolperm <kitcharoenp@gmail.com>
# @copyright Copyright (C) 2017
# @license http://opensource.org/licenses/gpl-3.0.html GNU Public License

from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models

"""
for fuel_log in LogFuels.search_read(
                [['&', ['date', '>=', '01-01-2018'], ['date', '<=', '01-31-2018'],]],
                ['date', 'vehicle_id',  'purchaser_id', 'liter',
                    'amount', 'price_per_liter', 'odometer',
                    'x_last_refuel_odometer', 'x_fuel_consumption',
                    'x_distance'],
                order="vehicle_id asc, date asc"):
"""

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
            amount = 0
            x_distance = 0
            liter = 0
            for fuel_log in LogFuels.search(
                #[('date', '<=', end_date), ('date', '>=', start_date),('vehicle_id', '=', vehicle.id)], limit=1):
                [('date', '<=', '2018-05-10'), ('date', '>=', '2018-05-01'),('vehicle_id', '=', vehicle.id)]):
                amount = fuel_log.amount
                x_distance = fuel_log.x_distance
                liter = fuel_log.liter
            res.append({
                'vehicle_name': vehicle.name,
                'amount': amount,
                'x_distance': x_distance,
                'liter': liter,
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
