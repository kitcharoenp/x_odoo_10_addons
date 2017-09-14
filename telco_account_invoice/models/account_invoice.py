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

    @api.onchange('invoice_line_ids')
    def _onchange_origin(self):
        res = super(AccountInvoice, self)._onchange_origin()
        purchase_ids = self.invoice_line_ids.mapped('purchase_id')
        if purchase_ids:
            self.comment = ', '.join(
                        str(v) for v in purchase_ids.mapped('x_description'))
            self.reference = ', '.join(
                        str(x) for x in purchase_ids.mapped('x_other_ref'))
        return res
