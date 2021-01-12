# -*- coding: utf-8 -*-
import base64
from io import BytesIO
import math
from num2words import num2words
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from .constants import CMPConstants as constants
from .control_code_generator import ControlCodeGenerator
import qrcode
import werkzeug

class CMPAccountMove(models.Model):
    _inherit = 'account.move'
    cmp_code = fields.Char('Control code', track_visibility='always')
    cmp_number = fields.Integer('Invoice Number', default=0)
    cmp_issue = fields.Date('date of issue')
    cmp_literal = fields.Char('Literal')
    cmp_ice = fields.Float('ICE', digits=constants.DIGITS)
    cmp_dosage_id = fields.Many2one(
        'cmp.dosage', 'Dosage', help='Company\'s dosage', required=False)
    cmp_nit = fields.Char('Customer NIT')
    cmp_business_name = fields.Char('Costumer BN', help='Costumer\'s Business Name')
    cmp_state = fields.Selection(constants.INVOICE_STATES, string='Status',
                                 default=constants.DRAFT, track_visibility='always')
    cmp_qr_content = fields.Char('QR string', compute='get_qr_content')
    cmp_qr_image = fields.Binary('QR Code', compute='generate_qr_code')

    def cmp_validate(self):
        self.ensure_one()
        if not self.cmp_issue:
            self.cmp_issue = fields.date.today()
        update_data = self.cmp_dosage_id.validate_invoice(
            self.cmp_number,
            self.cmp_nit,
            self.cmp_issue,
            self.amount_total)
        self.update(update_data)

    """Generate QR String based on list of values"""

    @api.depends('cmp_dosage_id', 'amount_total', 'cmp_ice', 'cmp_nit', 'cmp_code', 'cmp_issue', 'cmp_number')
    def get_qr_content(self):
        for move in self:
            # Importe Ventas tasa cero
            amount_notax = 0
            # Importe No sujeto a CF
            icf = 0
            base_taxable = self.amount_total
            base_taxable -= 0  # self.amount_discount
            base_taxable -= icf
            base_taxable -= amount_notax

            values = [
                self.cmp_dosage_id.tin,
                self.cmp_number,
                self.cmp_dosage_id.auth_number,
                self.cmp_issue.strftime('%d/%m/%Y') if self.cmp_issue is not False else '00',
                '{:12.2f}'.format(self.amount_total).strip(),
                '{:12.2f}'.format(base_taxable).strip(),
                self.cmp_code,
                self.cmp_nit or '0',
                '{:12.2f}'.format(self.cmp_ice).strip(),
                '{:12.2f}'.format(amount_notax).strip(),
                '{:12.2f}'.format(icf).strip(),
                # discount
                '{:12.2f}'.format(0).strip()
            ]
            vals = [str(x) for x in values]
            qr_text = str.join('|', vals)
            move.update({'cmp_qr_content': qr_text})

    @api.depends('cmp_qr_content')
    def generate_qr_code(self):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.cmp_qr_content)
        qr.make(fit=True)
        img = qr.make_image()
        temp = BytesIO()
        img.save(temp, format="PNG")
        qr_image = base64.b64encode(temp.getvalue())
        self.cmp_qr_image = qr_image

    @api.model
    def get_qr_url(self):
        qr_code = self.cmp_qr_content
        base_text = "/report/barcode/"
        base_text += "?type=%s&value=%s&width=%s&height=%s&humanreadable=1"
        return base_text % ('QR', werkzeug.url_quote_plus(qr_code), 128, 128)

    @staticmethod
    def display_literal(number, language='en', suffix=''):
        trunc_number = math.trunc(number)
        cents = round(number % math.trunc(number) * 100)
        return '%s %s/100 %s' % (num2words(trunc_number,
                                           lang=language), cents, suffix)

    @api.onchange('cmp_dosage_id')
    def change_cmp_dosage_id(self):
        self.ensure_one()
        if self.cmp_dosage_id.id:
            if self.cmp_dosage_id.type_dosage in [constants.STD, constants.ZTS]:
                self.cmp_nit = self.partner_id.vat or '0'
                self.cmp_business_name = self.partner_id.name

    @api.constrains('cmp_dosage_id', 'cmp_number')
    def constraint_dosage_number(self):
        for record in self:
            if record.cmp_number > 0:
                search_count_domain = [
                    ('cmp_dosage_id', '=', record.cmp_dosage_id.id),
                    ('cmp_number', '=', record.cmp_number)
                ]
                invoice_number_matches = self.search_count(search_count_domain)
                if invoice_number_matches > 1:
                    raise ValidationError(
                        _('The selected dosage already has the %s invoice number' % record.cmp_number))
