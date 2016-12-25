# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_withhoding_tax = fields.Boolean(
        string="Is Withholding Tax",
        help="Specify whether the product can be selected in \
            an Withholding Tax Document.")
