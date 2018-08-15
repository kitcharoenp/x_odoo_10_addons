# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
# @author Kitcharoen Poolperm <kitcharoenp@gmail.com>
# @copyright Copyright (C) 2017
# @license http://opensource.org/licenses/gpl-3.0.html GNU Public License

from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
import io

import pandas as pd
import numpy as np
#https://stackoverflow.com/questions/37604289/tkinter-tclerror-no-display-name-and-no-display-environment-variable
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import seaborn as sns

class TelcoVehiclesFuelLogReportUtil(models.AbstractModel):
    # _name is format:
    # report.module_name.template_id
    _name = 'report.telco_vehicles_fuel_log.fuel_log_report_template'

    def _make_pandas_data_frame(self, logs_fuel):
        param = {
            'date':      [],
            'license_plate':  [],
            'location':  [],
            'amount':     []
        }
        for log in logs_fuel:
            param['date'] +=  [log.date]
            param['license_plate'] +=  [log.vehicle_id.license_plate]
            param['location'] +=  [log.vehicle_id.location]
            param['amount'] +=  [log.amount]

        # make pandas dataframe
        df = pd.DataFrame(param)
        # convert date field to datetime
        df['date'] = pd.to_datetime(df['date'])
        # set the index
        df.set_index('date', inplace=True)
        return df

    def _make_boxplot_group_by_month(self, df):
        # group data by vehicle and index mounth
        grouper = df.groupby([pd.Grouper(freq="M"), 'license_plate'])
        # re-index
        grouper_reindex = grouper.sum().reset_index()
        # Convert pandas datetime month to string representation
        grouper_reindex['month'] = grouper_reindex['date'].dt.strftime('%b')
        p = sns.stripplot(
            data=grouper_reindex,
            x='month',
            y='amount',
            size=16,
            jitter=0.15,
            palette="hls",
            linewidth=1,
            alpha=.2)
        p_box = sns.boxplot(x='month', y='amount', data=grouper_reindex, palette="hls", linewidth=3)
        ax = plt.gca()
        ax.set_title("Fuel Log : Group by Month")
        # output file name
        plot_file_name="/opt/x_odoo_10_addons/telco_vehicles_fuel_log/static/img/all_groupby_month.png"
        # save as jpeg
        p_box.figure.savefig(plot_file_name,
                    format='png',
                    dpi=100)

    def _make_box_plot(self, logs_fuel):
        df = self._make_pandas_data_frame(logs_fuel)
        self._make_boxplot_group_by_month(df)

    def _get_data_for_report(self, data):
        res = []
        start_date = fields.Date.from_string(data['start_date'])
        end_date = fields.Date.from_string(data['end_date'])
        LogFuels = self.env['fleet.vehicle.log.fuel']
        data = {
            'date':      [],
            'license_plate':  [],
            'location':  [],
            'value':     []}

        i = 0
        for vehicle in self.env['fleet.vehicle'].search([('active', '=', True)]):
            amount = []
            # Find fuel log where date and between end_date and start_date vehicle id
            fuel_logs =  LogFuels.search([('date', '<=', end_date),
                                ('date', '>=', start_date),
                                ('vehicle_id', '=', vehicle.id)])

            for fuel_log in fuel_logs:
                amount +=  [fuel_log.amount]
                data['date'] +=  [fuel_log.date]
                data['license_plate'] +=  [fuel_log.vehicle_id.license_plate]
                data['location'] +=  [fuel_log.vehicle_id.location]
                data['value'] +=  [fuel_log.amount]

            df = pd.Series(amount)
            stat = df.describe()

            res.append({
                'license_plate': vehicle.license_plate,
                'amount': '',
                'count':  stat['count'],
                'mean':   stat['mean'],
                'std':    stat['std'],
                'min':    stat['min'],
                '25%':    stat['25%'],
                '50%':    stat['50%'],
                '75%':    stat['75%'],
                'max':    stat['max'],
            })
        # create the boxplot images
        logs_fuel =  LogFuels.search([
            ('date', '<=', end_date),
            ('date', '>=', start_date),
        ])
        self._make_box_plot(logs_fuel)
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
