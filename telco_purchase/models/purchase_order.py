# -*- coding: utf-8 -*-
# @author Kitcharoen Poolperm <kitcharoenp@gmail.com>
# @copyright Copyright (C) 2017
# @license http://opensource.org/licenses/gpl-3.0.html GNU Public License

from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    x_account_analytic_id = fields.Many2one('account.analytic.account',
                            string='Analytic Account')
    x_manager_id = fields.Many2one('hr.employee',
                            string="Manager")
    x_requestor_id = fields.Many2one('hr.employee',
                            string="Requestor")
    x_other_ref = fields.Char(string='Other Reference')
