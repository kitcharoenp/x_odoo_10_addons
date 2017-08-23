# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_equipment = fields.Boolean(
        string="Is Equipment",
        help="Specify whether the product can be selected in \
            an Equipment.")

    @api.model
    def create(self, vals):
        res = super(ProductTemplate, self).create(vals)
        if vals.get('is_equipment', True):
            vals.update({'supplier_taxes_id': False})
        return res
