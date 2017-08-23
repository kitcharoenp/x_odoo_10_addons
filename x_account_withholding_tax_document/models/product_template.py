# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    for_withhoding_tax_doc = fields.Boolean(
        string="For Withholding Tax Doc",
        help="Specify whether the product can be selected in \
            an Withholding Tax Document.")

    @api.model
    def create(self, vals):
        res = super(ProductTemplate, self).create(vals)
        if vals.get('for_withhoding_tax_doc', True):
            vals.update({'supplier_taxes_id': False})
        return res
