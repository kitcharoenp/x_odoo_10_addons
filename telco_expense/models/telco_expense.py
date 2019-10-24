# -*- coding: utf-8 -*-
# @author Kitcharoen Poolperm <kitcharoenp@gmail.com>
# @copyright Copyright (C) 2017
# @license http://opensource.org/licenses/gpl-3.0.html GNU Public License

from odoo import api, fields, models, _


class TelcoExpense(models.Model):
    _inherit = "hr.expense"

    accounting_date = fields.Date(
        string="Accounting Date",
        readonly=True,
        states={'reported': [('readonly', False)],
                'done': [('readonly', False)]})
    # overide payment_mode set default to company_account
    payment_mode = fields.Selection([
        ("own_account", "Employee (to reimburse)"),
        ("company_account", "Company")],
        default='company_account',
        states={
            'done': [('readonly', True)],
            'post': [('readonly', True)]},
        string="Payment By")

    x_partner_id = fields.Many2one(
        'res.partner',
        string='Vendor')

    x_project_id = fields.Many2one(
        'project.project',
        'Project',
        domain=[('active', '=', True)])

    """
    # verbose available_amount of budget
    @api.multi
    def submit_expenses(self):
        # verbose null  analytic_account_id
        if not self.analytic_account_id:
            raise UserError(_("You cannot report expenses for NULL Analytic Account!"))

        if not self.account_id:
            raise UserError(_("You cannot report expenses for NULL Account!"))

        # get Budgetary Position
        general_budget_id = self.env['account.budget.post'].sudo().search(
            [('account_ids', 'in', [self.account_id]),
             ],limit=1)

        # get Budget Line
        crossovered_budget_line = self.env['crossovered.budget.lines'].search(
            [('analytic_account_id', '=', self.analytic_account_id),
             ('date_to', '>', self.date),
             ('general_budget_id', '=', general_budget_id),
             ],limit=1)

        if (crossovered_budget_line):
            if(crossovered_budget_line.planned_amount > 0 and crossovered_budget_line.available_amount < 0)
                raise UserError(_("You cannot report expenses for Negative available Budget!"))

        return super(HrExpense, self).submit_expenses()
    """

    # onchange employee_id set the analytic_account_id is employee_id.x_analytic_account_id
    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id:
            self.analytic_account_id = self.employee_id.x_analytic_account_id
