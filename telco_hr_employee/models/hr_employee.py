# -*- coding: utf-8 -*-
# @author Kitcharoen Poolperm <kitcharoenp@gmail.com>
# @copyright Copyright (C) 2017
# @license http://opensource.org/licenses/gpl-3.0.html GNU Public License

from odoo import api, fields, models, tools


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    x_analytic_account_id = fields.Many2one(
        'account.analytic.account',
        'Analytic Account')
