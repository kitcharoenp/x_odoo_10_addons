# -*- coding: utf-8 -*-
# @author Kitcharoen Poolperm <kitcharoenp@gmail.com>
# @copyright Copyright (C) 2017
# @license http://opensource.org/licenses/gpl-3.0.html GNU Public License

from odoo import api, fields, models, _


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    x_account_payment_method = fields.Many2one(
                            'account.payment.method',
                            string='Payment Methods')
