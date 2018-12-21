# -*- coding: utf-8 -*-
# @author Kitcharoen Poolperm <kitcharoenp@gmail.com>
# @copyright Copyright (C) 2018
# @license http://opensource.org/licenses/gpl-3.0.html GNU Public License

from odoo import api, fields, models, tools


class CrossoveredBudgetLines(models.Model):
    _inherit = 'crossovered.budget.lines'

    x_internal_reference = fields.Char('Internal Reference',)
