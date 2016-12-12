# -*- coding: utf-8 -*-

from odoo import api, fields, models


class Holidays(models.Model):
    _inherit = "hr.holidays"

    # get a default first Manager from current user Manager
    def _default_manager1_get(self):
        employee = self.env['hr.employee'].search(
                [('user_id', '=', self.env.uid)], limit=1)
        return employee.parent_id

    # get a Second Manager from Manager of present User
    def _default_manager2_get(self):
        employee = self.env['hr.employee'].search(
                [('user_id', '=', self.env.uid)], limit=1)
        return employee.parent_id.parent_id

    manager_id = fields.Many2one(
                    'hr.employee',
                    string='First Approval',
                    readonly=True,
                    default=_default_manager1_get,
                    copy=False,
                    help='This area is automatically filled by the user \
                            who validate the leave')
    manager_id2 = fields.Many2one(
                    'hr.employee',
                    string='Second Approval',
                    readonly=True,
                    default=_default_manager2_get,
                    copy=False,
                    help='This area is automaticly filled by the user who \
                            validate the leave with second level (If Leave \
                            type need second validation)')

    @api.onchange('employee_id')
    def _onchange_employee(self):
        super(Holidays, self)._onchange_employee()
        self.manager_id = self.employee_id.parent_id
        self.manager_id2 = self.employee_id.parent_id.parent_id

    @api.multi
    def action_draft(self):
        for holiday in self:
            if not holiday.can_reset:
                raise UserError(_('Only an HR Manager or the concerned employee can reset to draft.'))
            if holiday.state not in ['confirm', 'refuse']:
                raise UserError(_('Leave request state must be "Refused" or "To Approve" in order to reset to Draft.'))
            holiday.write({
                'state': 'draft'
            })
            linked_requests = holiday.mapped('linked_request_ids')
            for linked_request in linked_requests:
                linked_request.action_draft()
            linked_requests.unlink()
        return True
