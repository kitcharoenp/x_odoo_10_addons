# -*- coding: utf-8 -*-

{
    'name': 'Tools on Vehicle Report',
    'version': '1.0',
    'license': 'AGPL-3',
    'category': 'Fleet',
    'description': """
        Tools on Vehicle Report""",
    'depends': ['x_maintenance', 'report', 'x_fleet_vehicle'],
    'summary': 'Tools on Vehicle Report',
    'data': [
        # Views
        # Menu and Action
        # Report
        'report/templates/x_tools_on_vehicle_template.xml',
        'report/x_report_tools_on_vehicle_report.xml',
        # Security
    ],
    'installable': True,
    'auto-install': False,
}
