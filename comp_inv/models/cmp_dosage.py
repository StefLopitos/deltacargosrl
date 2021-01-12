# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from .constants import CMPConstants as constants
from .control_code_generator import ControlCodeGenerator


class CmpDosage(models.Model):
    _name = 'cmp.dosage'
    _description = 'Company Invoicing Dosage'

    name = fields.Char('Reference name')
    company_logo = fields.Binary('Logo')
    invoice_header = fields.Text('Header', help='Header\'s text')
    invoice_footer = fields.Text('Footer', help='Footer\'s text')

    business_name = fields.Char('Business name', required=True)
    business_description = fields.Text(
        'Business description', help='Address, phone, etc.')
    tin = fields.Char('TIN', help='Tax Identification Number', required=True)

    initial_invoice_number = fields.Integer('Initial invoice number')
    initial_invoice_number_c = fields.Integer('Initial invoice number')
    dosage_key = fields.Char('Dosage key')
    dosage_key_c = fields.Char('Confirm')
    auth_number = fields.Char('Authorization number', size=15)
    auth_number_c = fields.Char('Confirm', size=15)
    date_due = fields.Date('Due date')
    date_due_c = fields.Date('Confirm')

    sfc = fields.Char('SFC')
    location = fields.Char('Location')
    is_branch = fields.Boolean(
        'Branch', default=False, help='Let this empty if this dosage is not for branch use')
    branch_code = fields.Char('Branch code')
    activity_id = fields.Many2one('cmp.activity', 'Business Activity')
    type_dosage = fields.Selection(
        constants.DOSAGE_TYPES, string='Type', default=constants.STD)
    state = fields.Selection(constants.DOSAGE_STATES, default=constants.DRAFT)
    limit_lines = fields.Integer('Invoice lines limit', default=0)
    limit_detail = fields.Integer('Detail size', default=50)
    limit_detail_display = fields.Integer('Display to', default=50)
    taxes_ids = fields.Many2many(
        'cmp.tax', 'cmp_dosage_tax_rel', column1='dosage_id', column2='tax_id', string='Taxes')

    def get_next_number(self):
        for dosage in self:
            next_number = dosage.initial_invoice_number
            self.env.cr.execute("""SELECT MAX(cmp_number) AS max_number 
            FROM account_move WHERE cmp_dosage_id=%s""" % dosage.id)
            for foo in self.env.cr.dictfetchall():
                if foo['max_number'] is None or foo['max_number'] == 0:
                    next_number = dosage.initial_invoice_number
                else:
                    next_number = foo['max_number'] + 1
        return next_number

    def validate_invoice(self, invoice_number, customer_nit, invoice_issue, invoice_total):
        code_gen = ControlCodeGenerator()
        if invoice_number == 0:
            invoice_number = self.get_next_number()
        code_gen.set_data(self.auth_number,
                          invoice_number,
                          customer_nit,
                          invoice_issue.strftime('%Y-%m-%d'),
                          invoice_total,
                          self.dosage_key)
        code_gen.generate_control_code()
        return {
            'cmp_number': invoice_number,
            'cmp_issue': invoice_issue,
            'cmp_code': code_gen.CONTROL_CODE,
            'cmp_state': constants.INVOICE_VALID
        }

    def set_active(self):
        for dsg in self:
            dsg.update({'state': constants.ACTIVE})

    def set_draft(self):
        env_am = self.env['account.move']
        for dsg in self:
            count_inv = env_am.search_count([('cmp_dosage_id', '=', dsg.id)])
            if count_inv >= 1:
                print("hello")
                # raise UserError(
                #     _('Can not set as draft when you have one or more invoices related'))
            dsg.update({'state': constants.DRAFT})

    def set_expired(self):
        for dsg in self:
            dsg.update({'state': constants.EXPIRED})

    @api.constrains('initial_invoice_number', 'initial_invoice_number_c')
    def constraint_initial_invoice_number(self):
        for dosage in self:
            if dosage.initial_invoice_number != dosage.initial_invoice_number_c:
                raise ValidationError(
                    _('Must confirm the current Initial invoice number properly'))

    @api.constrains('dosage_key', 'dosage_key_c')
    def constraint_dosage_key(self):
        for dosage in self:
            if dosage.dosage_key != dosage.dosage_key_c:
                raise ValidationError(
                    _('Must confirm the current dosage key properly'))

    @api.constrains('auth_number', 'auth_number_c')
    def constraint_auth_number(self):
        for dosage in self:
            if dosage.auth_number != dosage.auth_number_c:
                raise ValidationError(
                    _('Must confirm the current authorization number properly'))

    @api.constrains('date_due', 'date_due_c')
    def constraint_date_due(self):
        for dosage in self:
            if dosage.date_due != dosage.date_due_c:
                raise ValidationError(
                    _('Must confirm the current due date properly'))


class CmpTax(models.Model):
    _name = 'cmp.tax'
    name = fields.Char('Name', required=True)
    amount = fields.Float('Amount', digits=constants.DIGITS, required=True)
    type_tax = fields.Selection(
        constants.TAX_TYPES, string='Type', default=constants.PERCENT)


class CmpActivity(models.Model):
    _name = 'cmp.activity'
    _description = 'Business activity'

    name = fields.Char('Name', required=True)
    description = fields.Char('Description')
