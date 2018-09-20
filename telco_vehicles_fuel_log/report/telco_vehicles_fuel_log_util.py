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

    def _make_boxplot_group_by_month(self, df):
        # group data by vehicle and index mounth
        grouper = df.groupby([pd.Grouper(freq="M"), 'license_plate'])
        # re-index
        grouper_reindex = grouper.sum().reset_index()
        # Convert pandas datetime month to string representation
        grouper_reindex['month'] = grouper_reindex['date'].dt.strftime('%b')
        # https://www.datacamp.com/community/tutorials/seaborn-python-tutorial
        plt.figure(figsize=(16.69,12.00))
        plt.subplot(221)
        p = sns.stripplot(
            data=grouper_reindex,
            x='month',
            y='amount',
            jitter=0.15,
            palette="hls",
            linewidth=1,
            alpha=.4)
        p_box = sns.boxplot(
            x='month',
            y='amount',
            data=grouper_reindex,
            palette="Set2",
            linewidth=3)

        plt.subplot(222)
        p = sns.stripplot(
            data=grouper_reindex,
            x='month',
            y='liter',
            jitter=0.15,
            palette="hls",
            linewidth=1,
            alpha=.4)
        p_box = sns.boxplot(
            x='month',
            y='liter',
            data=grouper_reindex,
            palette="Set2",
            linewidth=3)

        plt.subplot(223)
        p = sns.stripplot(
            data=grouper_reindex,
            x='month',
            y='x_distance',
            jitter=0.15,
            palette="hls",
            linewidth=1,
            alpha=.4)
        p_box = sns.boxplot(
            x='month',
            y='x_distance',
            data=grouper_reindex,
            palette="Set2",
            linewidth=3)

        plt.subplot(224)
        p = sns.stripplot(
            data=grouper_reindex,
            x='month',
            y='x_fuel_consumption',
            jitter=0.15,
            palette="hls",
            linewidth=1,
            alpha=.4)
        p_box = sns.boxplot(
            x='month',
            y='x_fuel_consumption',
            data=grouper_reindex,
            palette="Set2",
            linewidth=3)
        #ax = plt.gca()
        #ax.set_title(str(y_column).upper())
        return p_box.figure

    def _make_box_plot(self, df):
        figure = self._make_boxplot_group_by_month(df)
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
        figure_out = self._make_box_plot(df)
        res['figure_out'] = figure_out
        result.append(res)
        return result

    def _make_boxplot_group_by_zone(self, df):
        # group data by vehicle and index mounth
        grouper = df.groupby([pd.Grouper(freq="M"), 'license_plate'])
        # re-index
        grouper_reindex = grouper.sum().reset_index()
        # Convert pandas datetime month to string representation
        grouper_reindex['month'] = grouper_reindex['date'].dt.strftime('%b')
        plt.figure(figsize=(16.69,11.25))
        plt.subplot(221)
        pz = sns.stripplot(
            data=grouper_reindex,
            x='month',
            y='amount',
            hue="license_plate",
            jitter=0.15,
            size=14,
            palette="hls",
            linewidth=1,
            alpha=.8)
        pz_box = sns.boxplot(
            x='month',
            y='amount',
            data=grouper_reindex,
            palette="Set2",
            linewidth=3)

        plt.subplot(222)
        pz = sns.stripplot(
            data=grouper_reindex,
            x='month',
            y='liter',
            hue="license_plate",
            jitter=0.15,
            size=14,
            palette="hls",
            linewidth=1,
            alpha=.8)
        pz_box = sns.boxplot(
            x='month',
            y='liter',
            data=grouper_reindex,
            palette="Set2",
            linewidth=3)

        plt.subplot(223)
        pz = sns.stripplot(
            data=grouper_reindex,
            x='month',
            y='x_distance',
            hue="license_plate",
            jitter=0.1,
            palette="hls",
            linewidth=1,
            alpha=.8)
        pz_box = sns.boxplot(
            x='month',
            y='x_distance',
            data=grouper_reindex,
            palette="Set2",
            linewidth=3)

        plt.subplot(224)
        pz = sns.stripplot(
            data=grouper_reindex,
            x='month',
            y='x_fuel_consumption',
            hue="license_plate",
            jitter=0.1,
            palette="hls",
            linewidth=1,
            alpha=.8)
        pz_box = sns.boxplot(
            x='month',
            y='x_fuel_consumption',
            data=grouper_reindex,
            palette="Set2",
            linewidth=3)
        #ax = plt.gca()
        #ax.set_title(str(y_column).upper())
        return pz_box.figure

    def _make_box_plot_zone(self, df):
        figure = self._make_boxplot_group_by_zone(df)
        out = cStringIO.StringIO()
        figure.savefig(out, format='png')
        figure.clear()
        figure_out = out.getvalue().encode('base64')
        out.truncate(0)
        return figure_out

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
            # make the dataframe
            df_loc = df.loc[df['location'] == loc]
            figure_out = self._make_box_plot_zone(df_loc)

            result.append({
                'zone_name': loc,
                'figure_out': figure_out
            })
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
        docargs = {}
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
