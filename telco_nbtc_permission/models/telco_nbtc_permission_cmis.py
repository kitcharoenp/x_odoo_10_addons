# -*- coding: utf-8 -*-

from odoo import models
from odoo.addons.cmis_field.fields import CmisFolder


class TelcoNbtcPermissionCmis(models.Model):
    _inherit = 'telco.nbtc.permission'

    cmis_folder = CmisFolder()
