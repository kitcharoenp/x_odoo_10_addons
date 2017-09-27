# -*- coding: utf-8 -*-
# @author Kitcharoen Poolperm <kitcharoenp@gmail.com>
# @copyright Copyright (C) 2017
# @license http://opensource.org/licenses/gpl-3.0.html GNU Public License

from odoo import api, fields, models, _


class TelcoExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"

    @api.onchange('accounting_date')
    def _onchange_accounting_date(self):
        if self.accounting_date:
            for expense_line in self.expense_line_ids:
                expense_line.accounting_date = self.accounting_date
