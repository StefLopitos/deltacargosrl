import math
import base64


class ControlCodeGenerator(object):
    AUTH_NUMBER = ''
    INVOICE_NUMBER = ''
    CUSTOMER_TIN = ''
    TRANSACTION_DATE = ''
    TRANSACTION_AMOUNT = 0
    DOSAGE_KEY = ''
    CONTROL_CODE = ''

    def test(self):
        self.code_64 = self.getb64(19058106)
        self.code_64_base = base64.b64encode(123456789)

    def set_data(self, auth_number, invoice_number, customer_tin, trans_date, trans_amount, dosage_key):
        self.AUTH_NUMBER = str(auth_number).strip()
        self.INVOICE_NUMBER = str(invoice_number).strip()
        # Case of space character
        for tin_number in str(customer_tin).split(' '):
            if len(tin_number) > 0 and tin_number.isdigit():
                self.CUSTOMER_TIN = tin_number
        td_split = trans_date.split('-')
        self.TRANSACTION_DATE = td_split[0] + td_split[1] + td_split[2]
        self.TRANSACTION_AMOUNT = str(math.trunc(round(trans_amount, 0)))
        self.DOSAGE_KEY = dosage_key

    def generate_control_code(self):
        invoice_number_verhoeff = self.INVOICE_NUMBER + self.get_verhoeff(self.INVOICE_NUMBER)
        str_verhoeff1 = invoice_number_verhoeff + self.get_verhoeff(invoice_number_verhoeff)

        customer_tin_verhoeff = self.CUSTOMER_TIN + self.get_verhoeff(self.CUSTOMER_TIN)
        str_verhoeff2 = customer_tin_verhoeff + self.get_verhoeff(customer_tin_verhoeff)

        date_trans_verhoeff = self.TRANSACTION_DATE + self.get_verhoeff(self.TRANSACTION_DATE)
        str_verhoeff3 = date_trans_verhoeff + self.get_verhoeff(date_trans_verhoeff)

        amount_verhoeff = self.TRANSACTION_AMOUNT + self.get_verhoeff(self.TRANSACTION_AMOUNT)
        str_verhoeff4 = amount_verhoeff + self.get_verhoeff(amount_verhoeff)

        int_verhoeff5 = int(str_verhoeff1)
        int_verhoeff5 += int(str_verhoeff2)
        int_verhoeff5 += int(str_verhoeff3)
        int_verhoeff5 += int(str_verhoeff4)
        str_verhoeff5 = str(int_verhoeff5)
        for x in range(5):
            str_verhoeff5 = str_verhoeff5 + self.get_verhoeff(str_verhoeff5)
        lc1 = int(str_verhoeff5[-5]) + 1
        lc2 = int(str_verhoeff5[-4]) + 1
        lc3 = int(str_verhoeff5[-3]) + 1
        lc4 = int(str_verhoeff5[-2]) + 1
        lc5 = int(str_verhoeff5[-1]) + 1
        str_1 = self.substring(self.DOSAGE_KEY, 0, lc1)
        str_2 = self.substring(self.DOSAGE_KEY, lc1, lc2)
        str_3 = self.substring(self.DOSAGE_KEY, lc1 + lc2, lc3)
        str_4 = self.substring(self.DOSAGE_KEY, lc1 + lc2 + lc3, lc4)
        str_5 = self.substring(self.DOSAGE_KEY, lc1 + lc2 + lc3 + lc4, lc5)
        # str_1 = self.DOSAGE_KEY[0:lc1]
        # str_2 = self.DOSAGE_KEY[lc1: lc1 + lc2]
        # str_3 = self.DOSAGE_KEY[(lc1 + lc2): (lc1 + lc2 + lc3)]
        # str_4 = self.DOSAGE_KEY[(lc1 + lc2 + lc3): (lc1 + lc2 + lc3 + lc4)]
        # str_5 = self.DOSAGE_KEY[(lc1 + lc2 + lc3 + lc4): (lc1 + lc2 + lc3 + lc4 + lc5)]

        auth_number = self.AUTH_NUMBER + str_1
        invoice_number = str_verhoeff1 + str_2
        tin_number = str_verhoeff2 + str_3
        date_number = str_verhoeff3 + str_4
        amount_number = str_verhoeff4 + str_5

        message = auth_number + invoice_number + tin_number + date_number + amount_number
        key_str = self.DOSAGE_KEY + str_verhoeff5[-5:]
        control_code = self.encrypt_message(message, key_str, 0).upper()

        ord_unicode1 = self.get_unicode(control_code, 0, 0)
        ord_unicode2 = self.get_unicode(control_code, 1, 0)
        ord_unicode3 = self.get_unicode(control_code, 2, 0)
        ord_unicode4 = self.get_unicode(control_code, 3, 0)
        ord_unicode5 = self.get_unicode(control_code, 4, 0)

        total_ord_unicode = ord_unicode1 + ord_unicode2 + ord_unicode3 + ord_unicode4 + ord_unicode5
        p51 = total_ord_unicode * ord_unicode1
        p52 = total_ord_unicode * ord_unicode2
        p53 = total_ord_unicode * ord_unicode3
        p54 = total_ord_unicode * ord_unicode4
        p55 = total_ord_unicode * ord_unicode5
        t51 = math.trunc(p51 / lc1)
        t52 = math.trunc(p52 / lc2)
        t53 = math.trunc(p53 / lc3)
        t54 = math.trunc(p54 / lc4)
        t55 = math.trunc(p55 / lc5)
        t5 = t51 + t52 + t53 + t54 + t55
        t5_base64 = self.getb64(t5)
        code = self.encrypt_message(t5_base64, key_str, 1)
        self.CONTROL_CODE = code.upper()
        # self.CONTROL_CODE = self.encrypt_message(t5_base64, key_str, 1).upper()

    @staticmethod
    def substring(string, start_position, total_chars):
        ncad = ""
        cad = str(string)
        for i in range(start_position, start_position + total_chars):
            ncad = ncad + string[i]
        return ncad

    @staticmethod
    def getb64(number):
        chars_dct = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F", "G", "H", "I",
                     "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "a", "b",
                     "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u",
                     "v", "w", "x", "y", "z", "+", "/"]
        cos = 1.0
        result = ""
        while cos > 0:
            cos = math.trunc(number / 64)
            mod_number = number % 64
            result = chars_dct[mod_number] + result
            number = cos
        return result

    @staticmethod
    def get_unicode(str_code, str_position, unicode_ord):
        while str_position < len(str_code):
            unicode_ord += ord(str_code[str_position])
            str_position += 5
        return unicode_ord

    def encrypt_message(self, message, key_str, guide):
        x = 0
        y = 0
        index1 = 0
        index2 = 0
        encrypted = ""
        state = [a for a in range(0, 256)]
        for i in range(0, 256):
            index2 = (ord(key_str[index1]) + state[i] + index2) % 256
            aux = state[i]
            state[i] = state[index2]
            state[index2] = aux
            index1 = (index1 + 1) % len(key_str)
        for i in range(0, len(message)):
            x = (x + 1) % 256
            y = ((state[x] + y) % 256)
            aux = state[x]
            state[x] = state[y]
            state[y] = aux
            number_reference = ord(message[i]) ^ state[(state[x] + state[y]) % 256]
            if guide == 1:
                encrypted = encrypted + "-" + self.fill_zeros(hex(number_reference), 2)
            else:
                encrypted = encrypted + self.fill_zeros(hex(number_reference), 2)
        if guide != 1:
            encrypted = "-" + encrypted
        # return encrypted[1:]
        return self.substring(encrypted, 1, len(encrypted) - 1)

    @staticmethod
    def fill_zeros(str_number, length):
        n_string = str_number[2:]
        for i in range(len(n_string), length):
            n_string = "0" + n_string
        return n_string

    @staticmethod
    def get_verhoeff(str_number: str):
        mul = [
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            [1, 2, 3, 4, 0, 6, 7, 8, 9, 5],
            [2, 3, 4, 0, 1, 7, 8, 9, 5, 6],
            [3, 4, 0, 1, 2, 8, 9, 5, 6, 7],
            [4, 0, 1, 2, 3, 9, 5, 6, 7, 8],
            [5, 9, 8, 7, 6, 0, 4, 3, 2, 1],
            [6, 5, 9, 8, 7, 1, 0, 4, 3, 2],
            [7, 6, 5, 9, 8, 2, 1, 0, 4, 3],
            [8, 7, 6, 5, 9, 3, 2, 1, 0, 4],
            [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
        ]
        per = [
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            [1, 5, 7, 6, 2, 8, 3, 0, 9, 4],
            [5, 8, 0, 3, 7, 9, 6, 1, 4, 2],
            [8, 9, 1, 6, 0, 4, 3, 5, 2, 7],
            [9, 4, 5, 3, 1, 2, 6, 8, 7, 0],
            [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
            [2, 7, 9, 3, 8, 0, 6, 4, 1, 5],
            [7, 0, 4, 6, 9, 1, 3, 2, 5, 8]
        ]
        inv = [0, 4, 3, 2, 1, 5, 6, 7, 8, 9]
        check = 0
        reversed_number = str_number[::-1]
        for i in range(0, len(reversed_number)):
            per_row = ((i + 1) % 8)
            per_col = int(reversed_number[i])
            mul_row = check
            mul_column = per[per_row][per_col]
            check = mul[mul_row][mul_column]
        return str(inv[check])


if __name__ == '__main__':
    test = ControlCodeGenerator()
    test.test()
