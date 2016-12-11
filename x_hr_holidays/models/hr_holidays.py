# -*- coding: utf-8 -*-

from odoo import api, fields, models


class Holidays(models.Model):
    _inherit = "hr.holidays"

    @api.onchange('employee_id')
    def _onchange_employee(self):
        super(Holidays, self)._onchange_employee()
        self.manager_id = self.employee_id.parent_id
        self.manager_id2 = self.employee_id.parent_id.parent_id
