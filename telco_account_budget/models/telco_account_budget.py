# -*- coding: utf-8 -*-
# @author Kitcharoen Poolperm <kitcharoenp@gmail.com>
# @copyright Copyright (C) 2018
# @license http://opensource.org/licenses/gpl-3.0.html GNU Public License

from odoo import api, fields, models, tools


class CrossoveredBudgetLines(models.Model):
    _inherit = 'crossovered.budget.lines'

    x_internal_reference = fields.Char('Internal Reference',)
    percentage = fields.Float(
        compute='_compute_percentage',
        string='Achievement',
        group_operator="avg",)
    available_amount = fields.Float(
        compute='_compute_available_amount',
        string='Available Amount',
        group_operator="sum",
        store="True")
    x_practical_amount = fields.Float(
        compute='_compute_practical_amount',
        group_operator="sum",
        store="True",
        string='Practical Amount', digits=0)
    x_percentage = fields.Float(
        compute='_compute_x_percentage',
        group_operator="avg",
        store="True",
        string='Achievement')


    @api.multi
    def _compute_available_amount(self):
        for line in self:
            if line.planned_amount != 0.00:
                line.available_amount = float((line.planned_amount or 0.0) - line.practical_amount)
            else:
                line.available_amount = 0.00

    @api.multi
    #@api.depends('general_budget_id', 'analytic_account_id', 'date_from', 'date_to')
    @api.depends('practical_amount',)
    def _compute_practical_amount(self):
        super(CrossoveredBudgetLines, self)._compute_practical_amount()
        for line in self:
            if line.practical_amount:
                line.x_practical_amount = line.practical_amount

    @api.multi
    @api.depends('practical_amount', 'theoritical_amount')
    def _compute_x_percentage(self):
        for line in self:
            if line.theoritical_amount != 0.00:
                line.x_percentage = float((line.practical_amount or 0.0) / line.theoritical_amount) * 100
            else:
                line.x_percentage = 0.00
