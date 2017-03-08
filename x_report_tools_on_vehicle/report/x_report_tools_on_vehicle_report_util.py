# -*- coding: utf-8 -*-

from odoo import api, fields, models


class xToolsOnVehicleReportUtil(models.AbstractModel):
    # _name is format:
    # report.module_name.template_id
    _name = 'report.x_report_tools_on_vehicle.x_tools_on_vehicle_template'

    def _get_data_for_report(self, vehicle_id):
        result = []
        Equipment = self.env['maintenance.equipment']
        for equip in Equipment.search(
                        [('x_vehicle_id', '=', vehicle_id)],
                        order="name asc"):
                res = {}
                res['category'] = equip.category_id.name
                res['image_small'] = equip.image_small
                res['name'] = equip.name
                res['model'] = equip.model
                res['serial_no'] = equip.serial_no
                res['x_asset_number'] = equip.x_asset_number
                res['note'] = equip.note
                result.append(res)
        return result

    @api.model
    def render_html(self, docids, data=None):
        Report = self.env['report']
        # get report template from template id
        tools_on_vehicle_report = Report._get_report_from_name(
            'x_report_tools_on_vehicle.x_tools_on_vehicle_template')
        fleet_vehicles = self.env['fleet.vehicle'].browse(docids)
        docargs = {
            'doc_ids': docids,
            'doc_model': tools_on_vehicle_report.model,
            'docs': fleet_vehicles,
            'get_data_for_report': self._get_data_for_report,
        }
        return Report.render(
            'x_report_tools_on_vehicle.x_tools_on_vehicle_template', docargs)
