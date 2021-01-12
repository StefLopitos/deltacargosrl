from odoo import models, fields, api
from ..models.constants import CMPConstants as constants
import xlwt
from xlwt import easyxf
import io
import base64
from calendar import monthrange


class CMPIvasaleReport(models.TransientModel):
    _name = "cmp.ivasale.report"
    file_name = fields.Char('File name')
    report_file = fields.Binary('Report file')
    report_printed = fields.Boolean('Printed', default=False)
    cmp_dosage_id = fields.Many2one('cmp.dosage', 'Dosage')
    year = fields.Integer('Fiscal year')
    month = fields.Selection(constants.MONTHS, 'Month')

    def generate_excel(self):
        for wizard in self:
            wizard.get_ivasales_records_by_dosage()
            return {
                'view_mode': 'form',
                'res_id': wizard.id,
                'res_model': 'cmp.ivasale.report',
                'view_tye': 'form',
                'type': 'ir.actions.act_window',
                'context': self.env.context,
                'target': 'new'
            }

    def get_ivasales_records_by_dosage(self):
        cell_styles = {
            'DEFAULT': easyxf("""font:height 200;align: horiz right;font:bold False;"""),
            'ROW': easyxf("""font:height 200;font:bold False"""),
            'HEADING': easyxf("""font:height 200;font:bold True; 
                                        borders: bottom thin"""),
            'BOLD_TITLE': easyxf("""font:height 200; align: horiz center; font:bold False;
             pattern:pattern solid, fore_colour gray25;""")
        }
        workbook = xlwt.Workbook(style_compression=2)
        worksheet = workbook.add_sheet('PURCHASE REPORT')
        header_row = 2
        header_columns = [
            'Nro.',
            'Fecha Emision',
            'Nro Factura',
            'Num Autorizacion',
            'Estado',
            'NIT CLIENTE',
            'RAZON SOCIAL',
            'MONTO TOTAL',
            'ICE',
            'EXENTOS',
            'TASA CERO',
            'SUBTOTAL',
            'DESCUENTOS',
            'IMPORTE BASE',
            'DEBITO FISCAL',
            'COD DE CONTROL'
        ]
        for column_pos in range(len(header_columns)):
            worksheet.write(header_row,
                            column_pos,
                            header_columns[column_pos],
                            cell_styles['HEADING'])
            worksheet.col(column_pos).width = 5600
        current_row = header_row + 1
        # Search invoices
        env_inv = self.env['cmp.invoice']
        start_date = '%s-%s-01' % (self.year, self.month)
        end_date = '%s-%s-%s' % (self.year, self.month,
                                 monthrange(self.year, int(self.month))[1])
        inv_domain = [
            ('dosage_id', '=', self.cmp_dosage_id.id),
            ('date_emission', '>=', start_date),
            ('date_emission', '<=', end_date),
            ('state', 'not in', [constants.DRAFT])
        ]
        inv_records = [inv for inv in env_inv.search(
            inv_domain, order='invoice_number')]
        record_counter = 1
        for invoice in inv_records:
            a = invoice.amount_total  # importe total Vta
            b = 0  # Otros no sujetos a IVA
            c = 0  # Operaciones exentas
            d = 0  # Vtas tasa cero
            e = a - b - c - d  # subtotal
            f = invoice.amount_discount  # Dctos rebajas sujetos a IVA
            g = e - f  # Importe base debito fiscal
            h = g * 0.13  # Debito fiscal
            spl_date = invoice.date_emission.split('-')
            invoice_date = '%s/%s/%s' % (spl_date[2], spl_date[1], spl_date[0])
            worksheet = self.fill_row(worksheet, current_row, [
                record_counter,
                invoice_date,
                invoice.invoice_number,
                invoice.auth_number,
                invoice.state,
                invoice.customer_tin if invoice.state != constants.INVOICE_VOID else 0,
                invoice.customer_business_name  if invoice.state != constants.INVOICE_VOID else 'S/N',
                a if invoice.state != constants.INVOICE_VOID else 0,
                b if invoice.state != constants.INVOICE_VOID else 0,
                c if invoice.state != constants.INVOICE_VOID else 0,
                d if invoice.state != constants.INVOICE_VOID else 0,
                e if invoice.state != constants.INVOICE_VOID else 0,
                f if invoice.state != constants.INVOICE_VOID else 0,
                g if invoice.state != constants.INVOICE_VOID else 0,
                h if invoice.state != constants.INVOICE_VOID else 0,
                invoice.control_code if invoice.state != constants.INVOICE_VOID else '0'
            ], cell_styles['DEFAULT'])
            record_counter += 1
            current_row += 1
        with io.BytesIO() as fp:
            workbook.save(fp)
            excel_file = base64.encodebytes(fp.getvalue())
            self.report_file = excel_file
        self.file_name = 'IVAV_%s.xls' % fields.datetime.today().strftime('%Y-%m-%d')
        self.report_printed = True

    @staticmethod
    def fill_row(worksheet, row=0, values=[], style=None):
        for i in range(len(values)):
            worksheet.write(row, i, values[i], style)
        return worksheet
