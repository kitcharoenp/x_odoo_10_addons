# -*- coding: utf-8 -*-

from odoo import models
from odoo.addons.cmis_field import fields


class TelcoWorkOrderCmis(models.Model):
    _inherit = 'telco.work.order'

    cmis_folder = fields.CmisFolder()
