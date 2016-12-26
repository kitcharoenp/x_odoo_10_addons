# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

import odoo.addons.decimal_precision as dp


class WithholdingTaxDocument(models.Model):
    _name = "withholding.tax.document"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Withholding Tax Document"
    _order = "date desc, id desc"

    name = fields.Char(
        string='Sequence',
        required=True,
        readonly=True,
        index=True,
        copy=False,
        default=lambda self: _('New'))
    date = fields.Date(
        string="Date Paid",
        default=fields.Date.context_today)
    employee_id = fields.Many2one(
        'hr.employee',
        string="Payer",
        required=True,
        default=lambda self: self.env['hr.employee'].search([
            ('user_id', '=', self.env.uid)], limit=1))
    product_id = fields.Many2one(
        'product.product',
        string='Type of Income',
        required=True)
    product_uom_id = fields.Many2one(
        'product.uom',
        string='Unit of Measure',
        required=True,
        default=lambda self: self.env['product.uom'].search(
            [], limit=1, order='id'))
    unit_amount = fields.Float(
        string='Unit Price',
        required=True,
        digits=dp.get_precision('Product Price'))
    quantity = fields.Float(
        required=True,
        digits=dp.get_precision('Product Unit of Measure'),
        default=1)
    tax_ids = fields.Many2many(
        'account.tax',
        string='Taxes')
    untaxed_amount = fields.Float(
        string='Subtotal',
        store=True,
        compute='_compute_amount',
        digits=dp.get_precision('Account'))
    total_amount = fields.Float(
        string='Total',
        store=True,
        compute='_compute_amount',
        digits=dp.get_precision('Account'))
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        readonly=True,
        default=lambda self: self.env.user.company_id)
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        readonly=True,
        default=lambda self: self.env.user.company_id.currency_id)
    partner_id = fields.Many2one(
        'res.partner',
        string='Vendor',
        required=True,
        help='Choose vendor for whom will be withholded tax.')
    origin = fields.Char(string="Source Document")

    @api.depends('quantity', 'unit_amount', 'tax_ids', 'currency_id')
    def _compute_amount(self):
        for record in self:
            record.untaxed_amount = record.unit_amount * record.quantity
            taxes = record.tax_ids.compute_all(
                record.unit_amount,
                record.currency_id,
                record.quantity,
                record.product_id,
                record.employee_id.user_id.partner_id)
            record.total_amount = taxes.get('total_included')

    @api.model
    def create(self, vals):
        if not vals.get('name', False) or vals['name'] == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'withholding.tax.document') or _('New')
        result = super(WithholdingTaxDocument, self).create(vals)
        return result
