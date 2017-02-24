# -*- coding: utf-8 -*-

from odoo import api, fields, models


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    equipment_count = fields.Integer(
                    compute="_compute_equipment_count", string="Equipments")

    def _compute_equipment_count(self):
        Equipment = self.env['maintenance.equipment']
        for record in self:
            record.equipment_count = Equipment.search_count([
                                        ('x_vehicle_id', '=', self.id)])

    @api.multi
    def act_show_equipment(self):
        """ This opens equipment view to view and add new equipment for this
            vehicle
            @return: the equipment view
        """
        self.ensure_one()
        res = self.env['ir.actions.act_window'].for_xml_id(
                'maintenance', 'hr_equipment_action')
        res.update(
            context=dict(self.env.context, default_x_vehicle_id=self.id),
            domain=[('x_vehicle_id', '=', self.id)]
        )
        return res
