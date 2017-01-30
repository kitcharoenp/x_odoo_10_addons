# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.modules.module import get_module_resource


class FleetVehicleClaims(models.Model):
    _name = "fleet.vehicle.claims"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Fleet Vehicle Claims"
    _order = "date desc, id desc"

    @api.model
    def _default_image(self):
        image_path = get_module_resource(
            'hr', 'static/src/img', 'default_image.png')
        return tools.image_resize_image_big(
            open(image_path, 'rb').read().encode('base64'))

    name = fields.Char(
        string='Sequence',
        required=True,
        readonly=True,
        index=True,
        copy=False,
        default=lambda self: _('New'))
    date = fields.Datetime(
        string="Date",
        required=True,
        default=fields.Date.context_today)
    vehicle_id = fields.Many2one(
        'fleet.vehicle',
        string='Vehicle',
        required=True,
        help='Vehicle concerned by this claims')
    driver_id = fields.Many2one(
        'hr.employee',
        string='Driver',
        required=True,
        help='Driver of the vehicle')
    third_party_id = fields.Many2one(
        'res.partner',
        string='Third Party',
        help=' Third Party ์Name')
    third_party_plate = fields.Char(
        string='Third party plate',
        help='License plate number of the third party vehicle')
    description = fields.Text('Description')
    claimed = fields.Boolean(default=False)
    at_fault_driver = fields.Boolean(default=False)
    at_fault_third_party = fields.Boolean(default=False)
    image = fields.Binary(
        string="Image",
        default=_default_image,
        attachment=True)
    image01 = fields.Binary(
        string="Image01",
        default=_default_image,
        attachment=True)
    image02 = fields.Binary(
        string="Image02",
        default=_default_image,
        attachment=True)
    description_image = fields.Char(
        string='Description Image')
    description_image01 = fields.Char(
        string='Description Image01')
    description_image02 = fields.Char(
        string='Description Image02')
    street = fields.Char()

    @api.model
    def create(self, vals):
        tools.image_resize_images(vals)
        if 'image01' in vals:
            vals.update(tools.image_get_resized_images(vals['image01'],
                        return_big=True,
                        big_name='image01'))
        if 'image02' in vals:
            vals.update(tools.image_get_resized_images(vals['image02'],
                        return_big=True,
                        big_name='image02'))
        if not vals.get('name', False) or vals['name'] == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'fleet.vehicle.claims') or _('New')
        result = super(FleetVehicleClaims, self).create(vals)
        return result

    @api.multi
    def write(self, vals):
        tools.image_resize_images(vals)
        if 'image01' in vals:
            vals.update(tools.image_get_resized_images(vals['image01'],
                        return_big=True,
                        big_name='image01'))
        if 'image02' in vals:
            vals.update(tools.image_get_resized_images(vals['image02'],
                        return_big=True,
                        big_name='image02'))
        return super(FleetVehicleClaims, self).write(vals)
