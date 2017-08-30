# -*- coding: utf-8 -*-
# @author Kitcharoen Poolperm <kitcharoenp@gmail.com>
# @copyright Copyright (C) 2017
# @license http://opensource.org/licenses/gpl-3.0.html GNU Public License

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp


class TelcoOpticalNetwork(models.Model):
    _name = "telco.optical.network"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Telco Optical Network"
    _order = "id desc"

    name = fields.Char(
        required=True,
        index=True,
        copy=False,
        default=lambda self: _('New'))
    state = fields.Selection([
                ('draft', 'Draft'),
                ('under_construction', 'Under Construction'),
                ('exists', 'Exists')],
                string='Status',
                required=True,
                readonly=True,
                copy=False,
                default='draft')

    # Ownership and Authority
    ownership_id = fields.Many2one(
        'res.partner',
        string='Ownership',)
    government_agency_id = fields.Many2one(
        'res.partner',
        string='Government Agency',)
    authority_id = fields.Many2one(
        'res.partner',
        string='Authority',)

    # Optical fibre information
    product_id = fields.Many2one(
        'product.product',
        string='Optical Fibre Type',
        domain=[('purchase_ok', '=', True)],
        change_default=True,)
    distance = fields.Float(
        string="Distance",
        digits=dp.get_precision('Product Unit of Measure'),
        group_operator="sum",
        required=True)
    diameter = fields.Float()
    pole = fields.Integer()
