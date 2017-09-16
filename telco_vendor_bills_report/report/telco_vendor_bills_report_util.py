# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
# @author Kitcharoen Poolperm <kitcharoenp@gmail.com>
# @copyright Copyright (C) 2017
# @license http://opensource.org/licenses/gpl-3.0.html GNU Public License

from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models


class TelcoVendorBillsReportUtil(models.AbstractModel):
    # _name is format:
    # report.module_name.template_id
    _name = 'report.telco_vendor_bills_report.bills_report_template'

    def _get_data_for_report1(self, data):
        res = []
        due_date = fields.Date.from_string(data['due_date'])
        VendorBills = self.env['account.invoice']
        if 'project_ids' in data:
            for project in self.env['project.project'].browse(
                    data['project_ids']):
                res.append({
                    'project_name': project.name,
                    'data': []})
                for vendor_bill in VendorBills.search([
                    ('date_due', 'like', str(due_date)), ],
                        order="partner_id asc"):
                    purchase_ids = vendor_bill.invoice_line_ids.mapped(
                        'purchase_line_id.order_id')

                    purchase_ids = vendor_bill.invoice_line_ids.mapped('purchase_id')
                    if purchase_ids[0]:
                        other_po_ref = purchase_ids[0].x_other_ref
                        primary_po = purchase_ids[0].name
                        x_issue_date = purchase_ids[0].x_issue_date
                        x_description = purchase_ids[0].x_description
                        analytic_id = purchase_ids[0].x_account_analytic_id.id

                    if vendor_bill.comment:
                        description = vendor_bill.comment
                    else:
                        description = x_description

                    if vendor_bill.reference:
                        reference = vendor_bill.reference
                    else:
                        reference = other_po_ref

                    if (project.analytic_account_id.id == analytic_id):
                        res[len(res)-1]['data'].append({
                            'other_po_ref': reference,
                            'primary_po': primary_po,
                            'issue_date': x_issue_date,
                            'x_description': description,
                            'vendor_name': vendor_bill.partner_id.name,
                            'reference': vendor_bill.reference,
                            'due_date': fields.Date.from_string(vendor_bill.date_due),
                            'amount_total': vendor_bill.amount_total,
                            'payment_method': vendor_bill.x_account_payment_method.name,
                            })
        return res

    def _get_data_for_report2(self, data):
        res = []
        due_date = fields.Date.from_string(data['due_date'])
        issue_date = fields.Date.from_string(data['issue_date'])
        VendorBills = self.env['account.invoice']
        res.append({
                    'project_name': '',
                    'data': []})
        for vendor_bill in VendorBills.search([
                    ('date_due', 'like', str(due_date)), ],
                        order="partner_id asc"):
            purchase_ids = vendor_bill.invoice_line_ids.mapped(
                'purchase_line_id.order_id')
            if purchase_ids[0]:
                other_po_ref = purchase_ids[0].x_other_ref
                primary_po = purchase_ids[0].name
                x_issue_date = fields.Date.from_string(
                                    purchase_ids[0].x_issue_date)
                x_description = purchase_ids[0].x_description
                analytic_id = purchase_ids[0].x_account_analytic_id.id

            if vendor_bill.comment:
                description = vendor_bill.comment
            else:
                description = x_description

            if vendor_bill.reference:
                reference = vendor_bill.reference
            else:
                reference = other_po_ref

            if (issue_date == x_issue_date):
                res[len(res)-1]['data'].append({
                    'other_po_ref': reference,
                    'primary_po': primary_po,
                    'issue_date': x_issue_date,
                    'x_description': description,
                    'vendor_name': vendor_bill.partner_id.name,
                    'reference': vendor_bill.reference,
                    'due_date': fields.Date.from_string(vendor_bill.date_due),
                    'amount_total': vendor_bill.amount_total,
                    'payment_method': vendor_bill.x_account_payment_method.name,
                })
        return res

    def _get_data_for_report(self, data):
        if len(data['project_ids']) > 0:
            res = self._get_data_for_report1(data)
        else:
            res = self._get_data_for_report2(data)
        return res

    @api.model
    def render_html(self, docids, data=None):
        Report = self.env['report']
        # get report template from template id
        vendor_bills_report = Report._get_report_from_name(
            'telco_vendor_bills_report.bills_report_template')
        account_invoices = self.env['account.invoice'].browse(docids)
        docargs = {
            'doc_ids': docids,
            'doc_model': vendor_bills_report.model,
            'docs': account_invoices,
            'get_data_for_report': self._get_data_for_report(data['form']),
        }
        return Report.render(
            'telco_vendor_bills_report.bills_report_template',
            docargs)
