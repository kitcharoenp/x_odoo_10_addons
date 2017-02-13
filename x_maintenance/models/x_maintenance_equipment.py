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
    product_id = fields.Many2one(
        'product.product',
        string='Equipment Product',
        domain=[('is_equipment', '=', True)])
    image = fields.Binary(
        related='product_id.image', string="Equipment Logo")
    image_small = fields.Binary(
        related='product_id.image_small', string="Equipment Logo (small)")
    image_medium = fields.Binary(
        related='product_id.image_medium', string="Equipment Logo (medium)")

    @api.onchange('product_id')
    def _onchange_model(self):
        if self.product_id:
            self.image_medium = self.product_id.image
            self.name = self.product_id.name
        else:
            self.image_medium = False

    def _resize_big_images(self, images, values):
        for image in images:
            if image in values:
                values.update(tools.image_get_resized_images(
                        values[image],
                        return_big=True,
                        big_name=image))

    @api.model
    def create(self, vals):
        tools.image_resize_images(vals)
        images = ['image01', 'image02', 'image03', 'image04']
        self._resize_big_images(images, vals)
        result = super(MaintenanceEquipment, self).create(vals)
        return result

    @api.multi
    def write(self, vals):
        tools.image_resize_images(vals)
        images = ['image01', 'image02', 'image03', 'image04']
        self._resize_big_images(images, vals)
        return super(MaintenanceEquipment, self).write(vals)
