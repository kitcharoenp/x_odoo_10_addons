# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class res_partner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    x_purchase_taxes_id = fields.Many2many(
                    'account.tax',
                    string='Default Taxes',
                    domain=['|', ('active', '=', False),
                            ('active', '=', True)])
