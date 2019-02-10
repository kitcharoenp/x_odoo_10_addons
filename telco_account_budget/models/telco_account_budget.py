# -*- coding: utf-8 -*-
# @author Kitcharoen Poolperm <kitcharoenp@gmail.com>
# @copyright Copyright (C) 2018
# @license http://opensource.org/licenses/gpl-3.0.html GNU Public License

from odoo import api, fields, models, tools


class CrossoveredBudgetLines(models.Model):
    _inherit = 'crossovered.budget.lines'

    x_internal_reference = fields.Char('Internal Reference',)
    x_practical_amount = fields.Float(
        compute='_compute_x_practical_amount',
        group_operator="sum",
        store="True",
        string='Post Amount', digits=0)
    available_amount = fields.Float(
        compute='_compute_x_available_amount',
        string='Available Amount',
        group_operator="sum",
        store="True")
    x_available_amount = fields.Float(
        compute='_compute_x_available_amount',
        string='Available Amount',
        group_operator="sum",
        store="True")
    x_percentage = fields.Float(
        compute='_compute_x_percentage',
        group_operator="avg",
        store="True",
        string='Availability %')

    @api.multi
    @api.depends('general_budget_id', 'date_to', 'date_from', 'analytic_account_id', 'practical_amount')
    def _compute_x_practical_amount(self):
        for line in self:
            result = 0.0
            acc_ids = line.general_budget_id.account_ids.ids
            if not acc_ids:
                raise UserError(_("The Budget '%s' has no accounts!") % ustr(line.general_budget_id.name))
            date_to = self.env.context.get('wizard_date_to') or line.date_to
            date_from = self.env.context.get('wizard_date_from') or line.date_from
            if line.analytic_account_id.id:
                self.env.cr.execute("""
                    SELECT SUM(amount)
                    FROM account_analytic_line
                    WHERE account_id=%s
                        AND (date between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))
                        AND general_account_id=ANY(%s)""",
                (line.analytic_account_id.id, date_from, date_to, acc_ids,))
                result = self.env.cr.fetchone()[0] or 0.0
            if(result!=0.0):
                line.x_practical_amount = result
            else:
                line.x_practical_amount = line.practical_amount

    @api.multi
    @api.depends('planned_amount', 'x_practical_amount')
    def _compute_x_available_amount(self):
        for line in self:
            if line.x_practical_amount != 0.00:
                # x_practical_amount return with minus sign
                line.x_available_amount = float((line.planned_amount or 0.0) + line.x_practical_amount)
            else:
                line.x_available_amount = 0.00

    @api.multi
    @api.depends('planned_amount', 'x_available_amount')
    def _compute_x_percentage(self):
        for line in self:
            if line.planned_amount != 0.00:
                line.x_percentage = float((line.x_available_amount or 0.0) / line.planned_amount) * 100
            else:
                line.x_percentage = 0.00
