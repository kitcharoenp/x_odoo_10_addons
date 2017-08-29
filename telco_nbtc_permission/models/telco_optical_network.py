# -*- coding: utf-8 -*-
# @author Kitcharoen Poolperm <kitcharoenp@gmail.com>
# @copyright Copyright (C) 2017
# @license http://opensource.org/licenses/gpl-3.0.html GNU Public License

from odoo import api, fields, models, _


class TelcoOpticalNetwork(models.Model):
    _inherit = ['telco.optical.network', ]

    nbtc_permission_id = fields.Many2one(
        'telco.nbtc.permission',
        string='NBTC Permission',
        readonly=True, copy=False)
