# -*- coding: utf-8 -*-
# @author Kitcharoen Poolperm <kitcharoenp@gmail.com>
# @copyright Copyright (C) 2018
# @license http://opensource.org/licenses/gpl-3.0.html GNU Public License

from odoo import api, fields, models, tools


class CrossoveredBudgetLines(models.Model):
    _inherit = 'crossovered.budget.lines'

    x_internal_reference = fields.Char('Internal Reference',)
    practical_amount = fields.Float(
        compute='_compute_practical_amount',
        string='Practical Amount',
        digits=0,
        group_operator="sum",
        store="True")
    theoritical_amount = fields.Float(
        compute='_compute_theoritical_amount',
        string='Theoretical Amount',
        digits=0,
        group_operator="sum",
        store="True")
    percentage = fields.Float(
        compute='_compute_percentage',
        string='Achievement',
        group_operator="avg",
        store="True")
    available_amount = fields.Float(
        compute='_compute_available_amount',
        string='Available Amount',
        group_operator="sum",
        store="True")

    @api.multi
    def _compute_available_amount(self):
        for line in self:
            if line.planned_amount != 0.00:
                line.available_amount = float((line.planned_amount or 0.0) - line.practical_amount)
            else:
                line.available_amount = 0.00
