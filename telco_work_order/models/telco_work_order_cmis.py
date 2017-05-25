# -*- coding: utf-8 -*-

from odoo import models
from odoo.addons.cmis_field.fields import CmisFolder


class TelcoWorkOrderCmis(models.Model):
    _inherit = 'telco.work.order'

    cmis_folder = CmisFolder()
