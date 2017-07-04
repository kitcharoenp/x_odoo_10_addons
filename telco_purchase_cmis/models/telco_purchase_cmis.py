# -*- coding: utf-8 -*-
# @author Kitcharoen Poolperm <kitcharoenp@gmail.com>
# @copyright Copyright (C) 2017
# @license http://opensource.org/licenses/gpl-3.0.html GNU Public License

from odoo import models
from odoo.addons.cmis_field.fields import CmisFolder


class TelcoPurchaseCmis(models.Model):
    _inherit = 'purchase.order'

    cmis_folder = CmisFolder()
