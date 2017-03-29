# -*- coding: utf-8 -*-

{
    'name': 'Fleet Vehicle Fuel Log',
    'version': '1.0',
    'license': 'AGPL-3',
    'category': 'Fleet, Vehicle',
    'description': """
Fleet Vehicle Fuel Log :
-------------
    * compute cousumption base on mileage and litre
        """,
    'depends': ['fleet'],
    'summary': 'Fleet Vehicle Fuel Log',
    'data': [
        # View
        'views/x_fleet_fuel_log_form_view.xml',
        'views/x_fleet_fuel_log_tree_view.xml',
        'views/x_fleet_fuel_log_graph_view.xml'
    ],
    'installable': True,
    'auto-install': False,
}
