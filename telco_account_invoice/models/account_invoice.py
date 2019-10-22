# -*- coding: utf-8 -*-
# @author Kitcharoen Poolperm <kitcharoenp@gmail.com>
# @copyright Copyright (C) 2017
# @license http://opensource.org/licenses/gpl-3.0.html GNU Public License

from odoo import api, fields, models, _
from odoo.tools.float_utils import float_compare

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


    def _prepare_invoice_line_from_po_line(self, line):
        res = super(AccountInvoice, self)._prepare_invoice_line_from_po_line(line)

        if line.product_id.code.startswith('ZSER'):
            qty = line.product_qty - line.qty_invoiced
        elif line.product_id.purchase_method == 'purchase':
            qty = line.product_qty - line.qty_invoiced
        else:
            qty = line.qty_received - line.qty_invoiced

        # FIXME: this cause invoice line quantity is equal zero     
        #if float_compare(qty, 0.0, precision_rounding=line.product_uom.rounding) <= 0:
        #    qty = 0.0

        taxes = line.taxes_id
        invoice_line_tax_ids = line.order_id.fiscal_position_id.map_tax(taxes)
        invoice_line = self.env['account.invoice.line']
        data = {
            'purchase_line_id': line.id,
            'name': line.order_id.name+': '+line.name,
            'origin': line.order_id.origin,
            'uom_id': line.product_uom.id,
            'product_id': line.product_id.id,
            'account_id': invoice_line.with_context({'journal_id': self.journal_id.id, 'type': 'in_invoice'})._default_account(),
            'price_unit': line.order_id.currency_id.with_context(date=self.date_invoice).compute(line.price_unit, self.currency_id, round=False),
            'quantity': qty,
            'discount': 0.0,
            'account_analytic_id': line.account_analytic_id.id,
            'analytic_tag_ids': line.analytic_tag_ids.ids,
            'invoice_line_tax_ids': invoice_line_tax_ids.ids
        }
        account = invoice_line.get_invoice_line_account('in_invoice', line.product_id, line.order_id.fiscal_position_id, self.env.user.company_id)
        if account:
            data['account_id'] = account.id
        return data

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
