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
