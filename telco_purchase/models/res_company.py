# -*- coding: utf-8 -*-
# @author Kitcharoen Poolperm <kitcharoenp@gmail.com>
# @copyright Copyright (C) 2017
# @license http://opensource.org/licenses/gpl-3.0.html GNU Public License

from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = "res.company"

    x_managing_director_id = fields.Many2one('hr.employee',
                            string="Managing Director")
    x_accounting_director_id = fields.Many2one('hr.employee',
                            string="Accounting Director")
