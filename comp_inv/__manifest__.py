# -*- coding: utf-8 -*-

{
    'name': "Basic Computerized Invoicing",

    'summary': """
       """,

    'description': """
        Long description of module's purpose
    """,

    'author': "Mikrogets",
    'website': "http://www.mikrogets.tech",

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/cmp_invoice_form.xml',
        'views/cmp_invoice_tree.xml',
        'views/cmp_invoice_action.xml',
        'views/cmp_dosage_form.xml',
        'views/cmp_dosage_tree.xml',
        'views/cmp_dosage_action.xml',
        # 'views/res_partner.xml',
        # 'views/sale_order.xml',
        # 'views/pos_order.xml',
        'views/menu.xml',
        # 'wizard/cmp_ivasale_report_view.xml',
        # 'wizard/cmp_code_test_view.xml',
        # 'wizard/cmp_pos_details.xml',
         'data/ir_sequence_data.xml',
        # 'data/paperformats.xml',
        'reports/cmp_invoice_report.xml',
        #  'reports/cmp_invoice_roll_report.xml',
        # 'reports/cmp_pos_details_report.xml'
    ],
    'qweb':[
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
