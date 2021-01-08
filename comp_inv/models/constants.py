# -*- coding: utf-8 -*-


# str values
DRAFT = 'draft'
VALID = 'valid'
ACTIVE = 'active'
EXPIRED = 'expired'
VOID = 'void'
STD = 'std'
ZTS = 'zts'
CASH = 'cash'
CARD = 'card'
PERCENT = 'percent'
FIXED = 'fixed'
DIGITS = (4, 2)

INVOICE_VALID = 'V'
INVOICE_VOID = 'A'
INVOICE_LOST = 'E'
INVOICE_NOTUSED = 'N'
INVOICE_CONTINGENCE = 'C'
INVOICE_FREE = 'L'

# list values
INVOICE_STATES = [
    (DRAFT, 'Draft'),
    (INVOICE_VALID, 'Valid'),
    (INVOICE_VOID, 'Void'),
    (INVOICE_LOST, 'Lost invoice'),
    (INVOICE_NOTUSED, 'Not Used'),
    (INVOICE_CONTINGENCE, 'Contingence emmission'),
    (INVOICE_FREE, 'Free consignation')
]
INVOICE_PAYMENTS = [(CASH, 'Cash'), (CARD, 'Card')]

DOSAGE_STATES = [(DRAFT, 'Draft'), (ACTIVE, 'Active'), (EXPIRED, 'Expired')]
DOSAGE_TYPES = [(STD, 'Standard'), (ZTS, 'Zero Tax Sales')]

TAX_TYPES = [(PERCENT, 'Percent'), (FIXED, 'Fixed')]

MONTHS = [
    ('01', 'JANUARY'), ('02', 'FEBRAURY'), ('03', 'MARCH'),
    ('04', 'APRIL'), ('05', 'MAY'), ('06', 'JUNE'),
    ('07', 'JULY'), ('08', 'AUGUST'), ('09', 'SEPTEMBER'),
    ('10', 'OCTOBER'), ('11', 'NOVEMBER'), ('12', 'DECEMBER')
]
