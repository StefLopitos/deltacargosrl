import werkzeug
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import math
from . import constants
from num2words import num2words
from .control_code_generator import ControlCodeGenerator


class CmpInvoice(models.Model):
    _name = 'cmp.invoice'
    _description = 'Invoice'
    _inherit = ['mail.thread']

    user_id = fields.Many2one('res.users',
                              'User',
                              default=lambda self: self.env.user)
    name = fields.Char('Reference Number')
    control_code = fields.Char('Control code', track_visibility='always')
    invoice_lines = fields.One2many('cmp.invoice.line', 'invoice_id', 'Lines')
    comments = fields.Char('Comment')
    invoice_number = fields.Integer('Invoice Number', default=0)
    # Dates
    date_invoice = fields.Date('Date', deafult=fields.date.today())
    date_emission = fields.Date('Emission date', default=fields.date.today())
    date_due = fields.Date('Due date')
    # Amounts
    literal = fields.Char('Literal')
    amount_tax = fields.Float(
        'Taxes', digits=constants.DIGITS, compute='_cmp_total')
    amount_discount = fields.Float(
        'Discount (-)', digits=constants.DIGITS, compute='_cmp_total')
    amount_untaxed = fields.Float(
        'Untaxed', digits=constants.DIGITS, compute='_cmp_total')
    amount_ice = fields.Float(
        'ICE', digits=constants.DIGITS, compute='_cmp_total')
    amount_total = fields.Float(
        'Total', digits=constants.DIGITS, compute='_cmp_total')
    literal = fields.Char('Literal amount')
    # Company's info
    dosage_id = fields.Many2one(
        'cmp.dosage', 'Dosage', help='Company\'s dosage', required=True)
    use_dosage_taxes = fields.Boolean('Dosage Taxes', default=False)
    company_tin = fields.Char(
        'Company TIN', help='Company\'s Tax Identification Number')
    auth_number = fields.Char('Auth. Number')
    company_business_name = fields.Char('Company business name')
    location = fields.Char('Location')
    # Customer's info
    customer_id = fields.Many2one('res.partner', string='Customer')
    customer_tin = fields.Char(
        'Customer TIN', help='Customer\'s Tax Identification Number')
    customer_business_name = fields.Char(
        'Costumer BN', help='Costumer\'s Business Name')
    customer_code = fields.Char('Customer code')
    payment = fields.Selection(
        constants.INVOICE_PAYMENTS, string='Payment type', default=constants.CASH)
    state = fields.Selection(constants.INVOICE_STATES, string='Status',
                             default=constants.DRAFT, track_visibility='always')
    qr_code = fields.Binary('QR code', compute='compute_qr_code')

    @api.constrains('dosage_id', 'invoice_number')
    def constraint_dosage_number(self):
        for record in self:
            if record.invoice_number > 0:
                search_count_domain = [('dosage_id', '=', record.dosage_id.id),
                                       ('invoice_number', '=',
                                        record.invoice_number)]
                invoice_number_matches = self.search_count(search_count_domain)
                if invoice_number_matches > 1:
                    raise ValidationError(
                        _('The invoice number was duplicated'))

    def get_dosage_id(self, uid):
        dosage_domain = [('state', '=', constants.ACTIVE)]
        return self.env['cmp.dosage'].search(dosage_domain, limit=1).id

    @api.model
    def create(self, vals):
        if 'name' not in vals.keys():
            vals['name'] = 'FF%s-%s-%s' % (
                '{:02}'.format(
                    vals['dosage_id']), '{:03}'.format(self.env.uid),
                fields.datetime.now().strftime('%y%m%d%H%M%S'))
        result = super(CmpInvoice, self).create(vals)
        return result

    @api.onchange('dosage_id')
    def change_dosage(self):
        for inv in self:
            inv.auth_number = inv.dosage_id.auth_number

    @api.onchange('customer_id')
    def change_customer(self):
        for inv in self:
            inv.customer_tin = inv.customer_id.cmp_tin
            inv.customer_code = inv.customer_id.cmp_customer_code
            inv.customer_business_name = inv.customer_id.name

    @staticmethod
    def display_literal(number, language='en', suffix=''):
        trunc_number = math.trunc(number)
        cents = round(number % math.trunc(number) * 100)
        return '%s %s/100 %s' % (num2words(trunc_number,
                                           lang=language), cents, suffix)

    def validate_invoice(self):
        for invoice in self:
            code_gen = ControlCodeGenerator()
            # date_transaction = fields.date.today().strftime('%Y-%m-%d')
            if invoice.date_emission is False:
                date_transaction = fields.date.today().strftime('%Y-%m-%d')
            else:
                date_transaction = invoice.date_emission.strftime('%Y-%m-%d')
            # uncomment for outdate invoice validation
            # if invoice.date_emission is not None:
            #     date_transaction = invoice.date_emission
            invoice_number = invoice.invoice_number if invoice.invoice_number > 0 else invoice.dosage_id.get_next_number()
            code_gen.set_data(invoice.auth_number, invoice_number,
                              invoice.customer_tin, date_transaction,
                              invoice.amount_total,
                              invoice.dosage_id.dosage_key)
            code_gen.generate_control_code()
            invoice_values = {
                'invoice_number': invoice_number,
                'date_emission': date_transaction,
                'date_due': invoice.dosage_id.date_due,
                'control_code': code_gen.CONTROL_CODE,
                'state': constants.INVOICE_VALID
            }
            print(invoice_values)
            invoice.update(invoice_values)

    def set_expired(self):
        for dosage in self:
            dosage.update({'state': constants.ACTIVE})

    def set_void(self):
        for inv in self:
            inv.update({'state': constants.INVOICE_VOID})

    @api.depends('invoice_lines.price_total')
    def _cmp_total(self):
        for inv in self:
            amount_discount = amount_ice = amount_untaxed = amount_tax = 0.0
            for line in inv.invoice_lines:
                # amount_ice += #importe ICE IEHD TASAS
                amount_discount += line.price_discount
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            inv.update({
                'amount_ice': amount_ice,
                'amount_tax': amount_tax,
                'amount_untaxed': amount_untaxed,
                'amount_discount': amount_discount,
                'amount_total': amount_untaxed + amount_tax
            })

    """Generate QR String based on list of values"""

    @api.model
    def get_qr_content(self):
        # Importe Ventas tasa cero
        amount_notax = 0
        # Importe No sujeto a CF
        icf = 0
        base_taxable = self.amount_total
        base_taxable -= self.amount_discount
        base_taxable -= icf
        base_taxable -= amount_notax

        values = [
            self.dosage_id.tin,
            self.invoice_number,
            self.dosage_id.auth_number,
            self.date_emission.strftime('%d/%m/%Y'),
            '{:12.2f}'.format(self.amount_total).strip(),
            '{:12.2f}'.format(base_taxable).strip(),
            self.control_code or '0',
            self.customer_tin or '0',
            '{:12.2f}'.format(self.amount_ice).strip(),
            '{:12.2f}'.format(amount_notax).strip(),
            '{:12.2f}'.format(icf).strip(),
            '{:12.2f}'.format(self.amount_discount).strip()
        ]
        vals = [str(x) for x in values]
        qr_text = str.join('|', vals)
        return qr_text

    @api.model
    def get_qr_url(self):
        qr_code = self.get_qr_content()
        # qr_encoded = None
        # with io.BytesIO() as qr_bytes:
        #     qr_content = qrcode.make(qr_code)
        #     qr_content.save(qr_bytes)
        #     qr_encoded = base64.encodebytes(qr_bytes.getvalue())
        base_text = "/report/barcode/"
        base_text += "?type=%s&value=%s&width=%s&height=%s&humanreadable=1"
        return base_text % ('QR', werkzeug.url_quote_plus(qr_code), 128, 128)


class CmpInvoiceLine(models.Model):
    _name = 'cmp.invoice.line'
    _description = 'Invoice detail record'

    invoice_id = fields.Many2one('cmp.invoice',
                                 'Invoice',
                                 required=True,
                                 ondelete='cascade')
    product_id = fields.Many2one('product.product',
                                 'Product',
                                 ondelete='set null')
    name = fields.Char('Description')
    product_qty = fields.Float('Quantity', required=True, default=1)
    price_unit = fields.Float('Unit price', digits=constants.DIGITS)
    # taxes_ids = fields.Many2many('account.tax', 'Taxes' )
    price_tax = fields.Float('Taxes', digits=constants.DIGITS, store=True)
    price_discount = fields.Float('Discount', digits=constants.DIGITS)
    price_subtotal = fields.Float('Subtotal (taxed)',
                                  digits=constants.DIGITS,
                                  compute='_compute_price_total')
    price_total = fields.Float('Subtotal',
                               digits=constants.DIGITS,
                               compute='_compute_price_total')

    @api.depends('price_unit', 'product_qty', 'price_discount', 'invoice_id')
    def _compute_price_total(self):
        for line in self:
            price_total = line.price_unit * line.product_qty
            price_tax = line.price_tax
            # Just in case of direct form creation
            if line.invoice_id.use_dosage_taxes:
                price_total = (line.price_unit *
                               line.product_qty) - line.price_discount
                price_tax = 0
                for tax in line.invoice_id.dosage_id.taxes_ids:
                    if tax.type_tax == constants.PERCENT:
                        price_tax += price_total * (tax.amount / 100)
                    elif tax.type_tax == constants.FIXED:
                        price_tax += tax.amount
            else:
                price_total -= line.price_discount
            line.update({
                # 'price_tax': price_tax,
                'price_subtotal': price_total + (-1 * price_tax),
                'price_total': price_total
            })

    @staticmethod
    def cut_name(string: str, max_length=20):
        return string if max_length == 0 else string.lower()[0:max_length]
