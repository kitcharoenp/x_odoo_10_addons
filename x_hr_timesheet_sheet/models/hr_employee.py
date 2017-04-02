# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    x_signature_img = fields.Binary(
        string="Signature Image",
        attachment=True)
    x_administrator_id = fields.Many2one(
        'hr.employee',
        string='Administrator')
    x_state_id = fields.Many2one(
        "res.country.state",
        string='State')

    @api.model
    def create(self, vals):
        if 'x_signature_img' in vals:
            vals.update(self._image_get_resized_signature(
                            vals['x_signature_img'],
                            image_name='x_signature_img'))
        result = super(HrEmployee, self).create(vals)
        return result

    @api.multi
    def write(self, vals):
        if 'x_signature_img' in vals:
            vals.update(self._image_get_resized_signature(
                            vals['x_signature_img'],
                            image_name='x_signature_img'))
        return super(HrEmployee, self).write(vals)

    def _image_get_resized_signature(
            self, base64_source, image_name='x_signature_img'):
        return_dict = dict()
        return_dict[image_name] = tools.image_resize_image(
                base64_source,
                size=(200, 100),
                encoding='base64',
                filetype=None,
                avoid_if_small=True)
        return return_dict
