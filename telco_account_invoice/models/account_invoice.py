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
    x_service_order = fields.Char(string='Service Order')
    x_circuit_id = fields.Char(string='Circuit Id')
    x_description = fields.Text(string='Description')
    x_processing = fields.Selection([
                ('draft', 'Draft'),
                ('in_progress', 'In Progress'),
                ('clearing', 'Clearing'),
                ('paid', 'Paid')],
                string='Processing',
                copy=False,
                default='draft')
    x_sap_network = fields.Char(string='Sap Network')


    @api.onchange('invoice_line_ids')
    def _onchange_origin(self):
        res = super(AccountInvoice, self)._onchange_origin()
        purchase_ids = self.invoice_line_ids.mapped('purchase_id')
        if purchase_ids:

            self.comment = ', '.join(
                        v for v in purchase_ids.mapped('x_description') if v)
            self.reference = ', '.join(
                        x for x in purchase_ids.mapped('partner_ref') if x)

            self.x_service_order = ', '.join(
                        x for x in purchase_ids.mapped('x_service_order') if x)
            self.x_circuit_id = ', '.join(
                        x for x in purchase_ids.mapped('x_circuit_id') if x)

            self.x_sap_network = ', '.join(
                        x for x in purchase_ids.mapped('x_sap_network') if x)
            self.x_description = ', '.join(
                        x for x in purchase_ids.mapped('x_description') if x)
        return res
