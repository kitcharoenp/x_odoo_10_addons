# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
# @author Kitcharoen Poolperm <kitcharoenp@gmail.com>
# @copyright Copyright (C) 2017
# @license http://opensource.org/licenses/gpl-3.0.html GNU Public License

from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
import io
import base64
import cStringIO

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
            'amount':     [],
            'liter':     [],
            'x_distance':     [],
            'x_fuel_consumption':     []
        }
        for log in logs_fuel:
            param['date'] +=  [log.date]
            param['license_plate'] +=  [log.vehicle_id.license_plate]
            param['location'] +=  [log.vehicle_id.location]
            param['amount'] +=  [log.amount]
            param['liter'] +=  [log.liter]
            param['x_distance'] +=  [log.x_distance]
            param['x_fuel_consumption'] +=  [log.x_fuel_consumption]

        # make pandas dataframe
        df = pd.DataFrame(param)
        # convert date field to datetime
        df['date'] = pd.to_datetime(df['date'])
        # set the index
        df.set_index('date', inplace=True)
        return df

    def _make_boxplot_group_by_month(self, df, y_column):
        # group data by vehicle and index mounth
        grouper = df.groupby([pd.Grouper(freq="M"), 'license_plate'])
        # re-index
        grouper_reindex = grouper.sum().reset_index()
        # Convert pandas datetime month to string representation
        grouper_reindex['month'] = grouper_reindex['date'].dt.strftime('%b')
        p = sns.stripplot(
            data=grouper_reindex,
            x='month',
            y=str(y_column),
            #size=16,
            jitter=True,
            palette="hls",
            linewidth=1,
            alpha=.2)
        p_box = sns.boxplot(x='month', y=str(y_column), data=grouper_reindex, palette="hls", linewidth=3)
        ax = plt.gca()
        ax.set_title(str(y_column).upper())
        return p_box.figure

    def _make_boxplot_group_by_zone(self, df, y_column):
        # group data by vehicle and index mounth
        grouper = df.groupby([pd.Grouper(freq="M"), 'license_plate'])
        # re-index
        grouper_reindex = grouper.sum().reset_index()
        # Convert pandas datetime month to string representation
        grouper_reindex['month'] = grouper_reindex['date'].dt.strftime('%b')
        p = sns.stripplot(
            data=grouper_reindex,
            x='month',
            y=str(y_column),
            jitter=0.05,
            size=11,
            palette="hls",
            hue="license_plate",
            linewidth=1,
            alpha=.7)
        p_box = sns.boxplot(x='month', y=str(y_column), data=grouper_reindex, palette="hls", linewidth=1)
        ax = plt.gca()
        ax.set_title(str(y_column).upper())
        return p_box.figure

    def _make_box_plot(self, df, y_column):
        figure = self._make_boxplot_group_by_month(df, y_column)
        out = cStringIO.StringIO()
        figure.savefig(out, format='png')
        figure.clear()
        figure_out = out.getvalue().encode('base64')
        out.truncate(0)
        return figure_out

    def _make_box_plot_zone(self, df, y_column):
        figure = self._make_boxplot_group_by_zone(df, y_column)
        out = cStringIO.StringIO()
        figure.savefig(out, format='png')
        figure.clear()
        figure_out = out.getvalue().encode('base64')
        out.truncate(0)
        return figure_out

    def _get_figure_for_report(self, data):
        result = []
        res = {}
        start_date = fields.Date.from_string(data['start_date'])
        end_date = fields.Date.from_string(data['end_date'])
        LogFuels = self.env['fleet.vehicle.log.fuel']
        # create the boxplot images
        logs_fuel =  LogFuels.search([
            ('date', '<=', end_date),
            ('date', '>=', start_date),
        ])
        df = self._make_pandas_data_frame(logs_fuel)
        column_list = ['amount', 'liter', 'x_distance', 'x_fuel_consumption']
        for column in column_list:
            res = {}
            figure_out = self._make_box_plot(df, column)
            res['figure_out'] = figure_out
            res['test_text'] = str(column).upper()
            result.append(res)

        return result

    def _get_figure_by_location(self, data):
        result = []
        start_date = fields.Date.from_string(data['start_date'])
        end_date = fields.Date.from_string(data['end_date'])
        LogFuels = self.env['fleet.vehicle.log.fuel']

        # create the boxplot images
        logs_fuel =  LogFuels.search([
            ('date', '<=', end_date),
            ('date', '>=', start_date),
        ])
        df = self._make_pandas_data_frame(logs_fuel)
        location_list = df.location.unique()

        for loc in location_list:
            result.append({
                'zone_name': loc,
                'data': []
            })
            # make the dataframe
            df_loc = df.loc[df['location'] == loc]
            column_list = ['amount', 'liter', 'x_distance', 'x_fuel_consumption']
            zone_data = {}
            for column in column_list:
                figure_out = self._make_box_plot_zone(df_loc, column)
                zone_data['FIG_'+column] = figure_out
            result[len(result)-1]['data'].append(zone_data)
        return result

    def _get_data_for_report(self, data):
        res = []
        start_date = fields.Date.from_string(data['start_date'])
        end_date = fields.Date.from_string(data['end_date'])
        LogFuels = self.env['fleet.vehicle.log.fuel']

        i = 0
        data = {
            'date':      [],
            'license_plate':  [],
            'location':  [],
            'value':     []}
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
            'get_data': self._get_data(data['form']),
            'get_figure': self._get_figure_for_report(data['form']),
            'get_figure_by_location': self._get_figure_by_location(data['form']),
        }
        return Report.render(
            'telco_vehicles_fuel_log.fuel_log_report_template',
            docargs)
