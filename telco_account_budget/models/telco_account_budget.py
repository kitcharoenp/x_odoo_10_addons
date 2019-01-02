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
        compute='_compute_x_practical_amount',
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
                line.available_amount = float((line.planned_amount or 0.0) - line.x_practical_amount)
            else:
                line.available_amount = 0.00

    @api.multi
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
            line.x_practical_amount = result

    @api.multi
    def _compute_x_percentage(self):
        for line in self:
            if line.theoritical_amount != 0.00:
                line.x_percentage = float((line.practical_amount or 0.0) / line.theoritical_amount) * 100
            else:
                line.percentage = 0.00
