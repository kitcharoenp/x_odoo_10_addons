# -*- coding: utf-8 -*-

{
    'name': 'Fleet Vehicle',
    'version': '1.0',
    'license': 'AGPL-3',
    'category': 'Fleet',
    'description': """
Enhancement Information on a vehicle :
-------------
    * First Driver field related to employee
    * Second driver field related to employee
    * Maintenance Administrator field related to employee
        """,
    'depends': ['hr', 'fleet'],
    'summary': 'Enhancement Information on a vehicle',
    'data': [
        'views/x_fleet_vehicle_form_view.xml',
        'views/x_fleet_vehicle_tree_view.xml',
    ],
    'installable': True,
    'auto-install': False,
}
