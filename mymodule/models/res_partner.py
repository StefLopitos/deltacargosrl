# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    url_google_maps = fields.Char(
        'Direccion Entrega Google Maps',
        compute='_compute_url_google_maps',
        store=True)

    def _compute_url_google_maps(self):
        for partner in self:
            partner.url_google_maps = 'https://www.google.com/maps/place/' + str(
                partner.zip) + ',' + str(partner.city)