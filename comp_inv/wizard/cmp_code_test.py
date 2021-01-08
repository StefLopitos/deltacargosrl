from odoo import models, fields, api
from ..models.control_code_generator import ControlCodeGenerator
from ..models import constants


class CmpCodeTest(models.TransientModel):
    _name = 'cmp.code.test'

    control_code = fields.Char('Control code')
    auth_number = fields.Char('Authorization number')
    invoice_number = fields.Integer('Invoice number')
    customer_tin = fields.Char('Customer T.I.N')
    date_emmission = fields.Date('Emmission date')
    amount_total = fields.Float('Total', digits=constants.DIGITS)
    dosage_key = fields.Char('Dosage key')

    def execute_test(self):
        self.ensure_one()
        self.generate_control_code()
        return {
            'view_mode': 'form',
            'res_id': self.id,
            'res_model': 'cmp.code.test',
            'type': 'ir.actions.act_window',
            'context': self.env.context,
            'target': 'new'
        }

    def generate_control_code(self):
        code_gen = ControlCodeGenerator()
        code_gen.set_data(self.auth_number,
                          self.invoice_number,
                          self.customer_tin,
                          self.date_emmission.strftime('%Y-%m-%d'),
                          self.amount_total,
                          self.dosage_key)
        code_gen.generate_control_code()
        self.control_code = code_gen.CONTROL_CODE
