# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class WithholdingTaxDocument(models.Model):
    _name = "withholding.tax.document"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Withholding Tax Document"
    _order = "date desc, id desc"

    name = fields.Char(
        string='Document Reference',
        required=True,
        index=True,
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
        required=True,
        domain=[('is_withhoding_tax', '=', True)])

    @api.model
    def create(self, vals):
        if not vals.get('name', False) or vals['name'] == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'withholding.tax.document') or _('New')
        result = super(WithholdingTaxDocument, self).create(vals)
        return result
