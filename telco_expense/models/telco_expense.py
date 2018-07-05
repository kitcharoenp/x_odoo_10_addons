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
