# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from odoo.modules.module import get_module_resource


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    @api.model
    def _default_image(self):
        image_path = get_module_resource(
            'x_maintenance', 'static/src/img', 'default_image.png')
        return tools.image_resize_image_big(
            open(image_path, 'rb').read().encode('base64'))

    x_vehicle_id = fields.Many2one(
        'fleet.vehicle',
        string='Vehicle')
    x_asset_number = fields.Char('Asset Number', copy=False)
    image01 = fields.Binary(
        string="Image01",
        default=_default_image,
        attachment=True)
    image02 = fields.Binary(
        string="Image02",
        default=_default_image,
        attachment=True)
    image03 = fields.Binary(
        string="Image03",
        default=_default_image,
        attachment=True)
    image04 = fields.Binary(
        string="Image04",
        default=_default_image,
        attachment=True)

    @api.model
    def create(self, vals):
        if 'image01' in vals:
            vals.update(tools.image_get_resized_images(vals['image01'],
                        return_big=True,
                        big_name='image01'))
        if 'image02' in vals:
            vals.update(tools.image_get_resized_images(vals['image02'],
                        return_big=True,
                        big_name='image02'))
        if 'image03' in vals:
            vals.update(tools.image_get_resized_images(vals['image03'],
                        return_big=True,
                        big_name='image03'))
        if 'image04' in vals:
            vals.update(tools.image_get_resized_images(vals['image04'],
                        return_big=True,
                        big_name='image04'))
        result = super(MaintenanceEquipment, self).create(vals)
        return result

    @api.multi
    def write(self, vals):
        if 'image01' in vals:
            vals.update(tools.image_get_resized_images(vals['image01'],
                        return_big=True,
                        big_name='image01'))
        if 'image02' in vals:
            vals.update(tools.image_get_resized_images(vals['image02'],
                        return_big=True,
                        big_name='image02'))
        if 'image03' in vals:
            vals.update(tools.image_get_resized_images(vals['image03'],
                        return_big=True,
                        big_name='image03'))
        if 'image04' in vals:
            vals.update(tools.image_get_resized_images(vals['image04'],
                        return_big=True,
                        big_name='image04'))
        return super(MaintenanceEquipment, self).write(vals)
