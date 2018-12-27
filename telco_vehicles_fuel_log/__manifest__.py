# -*- coding: utf-8 -*-
# @author Kitcharoen Poolperm <kitcharoenp@gmail.com>
# @copyright Copyright (C) 2017
# @license http://opensource.org/licenses/gpl-3.0.html GNU Public License
{
    'name': 'Telco Vehicles Fuel Log Report',
    'version': '0.01',
    'category': 'Fleet',
    "author": "kicharoenp@gmail.com",
    'summary': 'Vehicles, Fuel',
    'description': """
Vehicle, Fuel
==================================
With this module, It helps you managing all your vehicles fuel log

Main Features
-------------
* Analysis graph for costs with BoxPlot
* Filter report by period
""",
    'depends': ['fleet', 'report'],
    'data': [
        # Actions
        'views/telco_vehicles_fuel_log_form_view.xml',
        'actions/telco_vehicles_fuel_log_act_window.xml',
        # Views
        'views/telco_vehicles_fuel_log_menu_view.xml',
        # Reports and Templates
        'report/telco_vehicles_fuel_log_qweb_report.xml',
        'report/templates/fuel_log_report_template.xml',
        # Security
        'security/x_vehicle_fuel_log_security.xml',

    ],
    'installable': True,
    'auto_install': False,
}
