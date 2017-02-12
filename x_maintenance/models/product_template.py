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
        # When creating an product on the fly, you don't expect to
        # have taxes on it
        if vals.get('is_equipment', False):
            vals.update({'supplier_taxes_id': False})
        return super(ProductTemplate, self).create(vals)
