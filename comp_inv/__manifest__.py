# -*- coding: utf-8 -*-

{
    'name': "Basic Computerized Invoicing",

    'summary': """
       """,

    'description': """
        Long description of module's purpose
    """,

    'author': "MF CONSULTING",
    'website': "http://mfconsulting.mikrogets.tech",

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/cmp_dosage_form.xml',
        'views/cmp_dosage_tree.xml',
        'views/cmp_dosage_action.xml',
        'views/menu.xml',
        #  'reports/cmp_invoice_roll_report.xml',
        # 'reports/cmp_pos_details_report.xml'
        'views/account_move.xml',
        'reports/cmp_account_move_report.xml'
    ],
    'qweb':[
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
