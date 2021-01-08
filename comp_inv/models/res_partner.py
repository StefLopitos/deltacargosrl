# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CmpResPartner(models.Model):
    _inherit = 'res.partner'
    cmp_tin = fields.Char('T.I.N.', help='Tax Identification Number (Just numbers)')
    cmp_customer_code = fields.Char('Customer code', help='Used for computerized invoicing')
