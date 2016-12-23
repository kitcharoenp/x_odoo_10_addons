# -*- coding: utf-8 -*-

{
    'name': 'Withholding Tax Document',
    'version': '1.0',
    'license': 'AGPL-3',
    'category': 'Accounting & Finance',
    'description': """
        Withholding Tax Document""",
    'depends': ['report'],
    'summary': 'Withholding Tax Document',
    'data': [
    # Reports
        'report/x_withholding_tax_document_report.xml',
    # Report Templates
        'report/templates/x_withholding_tax_document_template.xml',
        'report/templates/x_wht_document_company_section_template.xml',
        'report/templates/x_wht_document_taxpayer_section_template.xml',
        'report/templates/x_wht_document_income_section_template.xml',
    ],
    'installable': True,
    'auto-install': True,
}
