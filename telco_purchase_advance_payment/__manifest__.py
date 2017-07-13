# -*- coding: utf-8 -*-
# @author Kitcharoen Poolperm <kitcharoenp@gmail.com>
# @copyright Copyright (C) 2017
# @license http://opensource.org/licenses/gpl-3.0.html GNU Public License

{
    'name': 'Telco Purchase Advance Payment',
    'version': '0.01',
    'category': 'Purchases',
    "author": "kicharoenp@gmail.com",
    'summary': 'Telco Purchase Advance Payment invoice',
    'description': """
When you pay a deposit you are paying in part for a product (or service).
Paying a deposit shows that you intend to buy the item and it means
you are entering into a contract with the business.
There may or may not be a contract in writing,
but doing it verbally still means a contract is in place,
meaning there are obligations on both you and the business.

When you pay a deposit, you and the business agree:
    1. the exact product or service that you are buying
    2. the amount of deposit you pay
    3. when the balance has to be paid
    4. when the product or service will be provided

It is important to make sure that you and the business are clear
about all the details. Ask for written confirmation
that includes all of the information above.
    """,
    'depends': ['purchase', 'sale'],
    'data': [
        # Actions
        'actions/telco_purchase_advance_payment_act_window.xml',
        # Views
        'views/telco_purchase_advance_payment_form_view.xml',
        'views/inherit_purchase_order_form.xml',
        # Reports and Templates
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
