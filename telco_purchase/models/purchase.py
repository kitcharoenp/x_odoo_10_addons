# -*- coding: utf-8 -*-
# @author Kitcharoen Poolperm <kitcharoenp@gmail.com>
# @copyright Copyright (C) 2017
# @license http://opensource.org/licenses/gpl-3.0.html GNU Public License

from odoo import api, fields, models, _


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    x_account_analytic_id = fields.Many2one('account.analytic.account',
                            string='Analytic Account')
    x_manager_id = fields.Many2one('hr.employee',
                            string="Manager")
    x_requestor_id = fields.Many2one('hr.employee',
                            string="Requestor")
    x_other_ref = fields.Char(string='Other Reference')

    x_work_order_id = fields.Many2one('telco.work.order',
                            string="Work Order")
    x_fault_id = fields.Many2one('telco.fault.management',
                            string="Fault Reference")
    x_invoice_receipt_date = fields.Datetime(string= 'Invoice Receipt',
                            default=fields.Datetime.now)
    x_invoice_receipt_by = fields.Many2one(
                            'hr.employee',
                            string="Receipt By",)

    @api.multi
    @api.depends('name', 'partner_ref')
    def name_get(self):
        result = super(PurchaseOrder, self).name_get()
        result = []
        for po in self:
            name = po.name
            result.append((po.id, name))
        return result
