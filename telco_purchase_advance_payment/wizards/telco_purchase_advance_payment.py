# -*- coding: utf-8 -*-
# @author Kitcharoen Poolperm <kitcharoenp@gmail.com>
# @copyright Copyright (C) 2017
# @license http://opensource.org/licenses/gpl-3.0.html GNU Public License

import time
from datetime import datetime

from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError


class TelcoPurchaseAdvancePayment(models.TransientModel):
    _name = "telco.purchase.advance.payment"
    _description = "Purchase Advance Payment Invoice"

    @api.model
    def _count(self):
        return len(self._context.get('active_ids', []))

    @api.model
    def _get_advance_payment_method(self):
        if self._count() == 1:
            purchase_obj = self.env['purchase.order']
            purchase_order = purchase_obj.browse(
                self._context.get('active_ids'))[0]
            # fix invoice_policy on sale
            """
            if all([line.product_id.invoice_policy == 'order'
                    for line in purchase_order.order_line]) or purchase_order.invoice_count:
                return 'all'
            """
        return 'delivered'

    # Deposit Product
    @api.model
    def _default_product_id(self):
        product_id = self.env['ir.values'].get_default(
            'sale.config.settings', 'deposit_product_id_setting')
        return self.env['product.product'].browse(product_id)

    # Expense Account
    @api.model
    def _default_deposit_account_id(self):
        return self._default_product_id().property_account_expense_id

    # Vendor Taxes
    @api.model
    def _default_deposit_taxes_id(self):
        return self._default_product_id().supplier_taxes_id

    advance_payment_method = fields.Selection([
        ('delivered', 'Invoiceable lines'),
        ('all', 'Invoiceable lines (deduct down payments)'),
        ('percentage', 'Down payment (percentage)'),
        ('fixed', 'Down payment (fixed amount)')
        ],
        string='What do you want to invoice?',
        default=_get_advance_payment_method,
        required=True)
    product_id = fields.Many2one(
        'product.product',
        string='Down Payment Product',
        domain=[('type', '=', 'service')],
        default=_default_product_id)
    count = fields.Integer(
        default=_count,
        string='# of Orders')
    amount = fields.Float(
        string='Down Payment Amount',
        digits=dp.get_precision('Account'),
        help="The amount to be invoiced in advance, taxes excluded.")
    deposit_account_id = fields.Many2one(
        "account.account",
        string="Expense Account",
        domain=[('deprecated', '=', False)],
        help="Account used for deposits",
        default=_default_deposit_account_id)
    deposit_taxes_id = fields.Many2many(
        "account.tax",
        string="Vendor Taxes",
        help="Taxes used for deposits",
        default=_default_deposit_taxes_id)

    @api.onchange('advance_payment_method')
    def onchange_advance_payment_method(self):
        if self.advance_payment_method == 'percentage':
            return {'value': {'amount': 0}}
        return {}

    @api.multi
    def _create_invoice(self, order, po_line, amount):
        inv_obj = self.env['account.invoice']
        ir_property_obj = self.env['ir.property']

        # Evaluate Expense Account
        account_id = False
        if self.product_id.id:
            account_id = self.product_id.property_account_expense_id.id
        if not account_id:
            expense_account = ir_property_obj.get(
                'property_account_expense_categ_id',
                'product.category')
            account_id = order.fiscal_position_id.map_account(expense_account).id if expense_account else False
        if not account_id:
            raise UserError(
                _('There is no income account defined for this product: "%s". \
                You may have to install a chart of account from \
                Accounting app, settings menu.') %
                (self.product_id.name,))

        # Evaluate amount
        if self.amount <= 0.00:
            raise UserError(_('The value of the down payment \
                amount must be positive.'))
        if self.advance_payment_method == 'percentage':
            amount = order.amount_untaxed * self.amount / 100
            name = _("Down payment of %s%%") % (self.amount,)
        else:
            amount = self.amount
            name = _('Down Payment')

        # Evaluate tax
        taxes = self.product_id.taxes_id.filtered(
            lambda r: not order.company_id or r.company_id == order.company_id)
        if order.fiscal_position_id and taxes:
            tax_ids = order.fiscal_position_id.map_tax(taxes).ids
        else:
            tax_ids = taxes.ids

        # todo : validate invoice parameter
        invoice = inv_obj.create({
            'name': order.name,
            'origin': order.name,
            'type': 'in_invoice',
            'reference': False,
            'account_id': order.partner_id.property_account_payable_id.id,
            'partner_id': order.partner_id.id,
            # 'partner_shipping_id': order.partner_shipping_id.id, Delivery Address
            'invoice_line_ids': [(0, 0, {
                'name': name,
                'origin': order.name,
                'account_id': account_id,
                'price_unit': amount,
                'quantity': 1.0,
                'discount': 0.0,
                'uom_id': self.product_id.uom_id.id,
                'product_id': self.product_id.id,
                'purchase_line_id': po_line.id,
                'invoice_line_tax_ids': [(6, 0, tax_ids)],
            })],
            'currency_id': order.currency_id.id,
            'payment_term_id': order.payment_term_id.id,
            'fiscal_position_id': order.fiscal_position_id.id or \
            order.partner_id.property_account_position_id.id,
            'comment': order.notes,
        })

        invoice.compute_taxes()
        invoice.message_post_with_view(
                    'mail.message_origin_link',
                    values={'self': invoice, 'origin': order},
                    subtype_id=self.env.ref('mail.mt_note').id)
        return invoice

    @api.multi
    def create_invoices(self):
        purchase_orders = self.env['purchase.order'].browse(
            self._context.get('active_ids', []))

        if self.advance_payment_method == 'delivered':
            # todo : auto action open invoice with inv_line
            purchase_orders.action_view_invoice()
        elif self.advance_payment_method == 'all':
            # todo : auto action open invoice with inv_line
            purchase_orders.action_view_invoice()
        else:
            # Create deposit product if necessary
            if not self.product_id:
                vals = self._prepare_deposit_product()
                self.product_id = self.env['product.product'].create(vals)
                self.env['ir.values'].sudo().set_default(
                    'sale.config.settings',
                    'deposit_product_id_setting',
                    self.product_id.id)

            purchase_line_obj = self.env['purchase.order.line']

            for order in purchase_orders:
                if self.advance_payment_method == 'percentage':
                    amount = order.amount_untaxed * self.amount / 100
                    name = ("Down payment of %s%%") % (self.amount,)
                else:
                    amount = self.amount
                    name = _('Down Payment: %s') % (time.strftime('%m %Y'),)
                # fix invoice_policy on sale
                """
                if self.product_id.invoice_policy != 'order':
                    raise UserError(_(
                        'The product used to invoice a down payment \
                        should have an invoice policy set to \
                        "Ordered quantities". Please update your deposit \
                        product to be able to create a deposit invoice.'))
                """
                if self.product_id.type != 'service':
                    raise UserError(_("The product used to invoice \
                    a down payment should be of type 'Service'. \
                    Please use another product or update this product."))

                # evaluate tax_ids for po_line
                taxes = self.product_id.taxes_id.filtered(
                    lambda r: not order.company_id or
                    r.company_id == order.company_id)
                if order.fiscal_position_id and taxes:
                    tax_ids = order.fiscal_position_id.map_tax(taxes).ids
                else:
                    tax_ids = taxes.ids

                # prepare po_line for deposit product
                po_line = purchase_line_obj.create({
                    'name': name,
                    'price_unit': amount,
                    'product_qty': 0.0,
                    'order_id': order.id,
                    'product_uom': self.product_id.uom_id.id,
                    'product_id': self.product_id.id,
                    'taxes_id': [(6, 0, tax_ids)],
                    'date_planned': datetime.today().strftime(
                                        DEFAULT_SERVER_DATETIME_FORMAT),
                })
                self._create_invoice(order, po_line, amount)
                # end else

        if self._context.get('open_invoices', False):
            return purchase_orders.action_view_invoice()
        return {'type': 'ir.actions.act_window_close'}

    def _prepare_deposit_product(self):
        return {
            'name': 'Down payment',
            'type': 'service',
            # fix invoice_policy on sale
            # 'invoice_policy': 'order',
            'property_account_expense_id': self.deposit_account_id.id,
            'supplier_taxes_id': [(6, 0, self.deposit_taxes_id.ids)],
        }
