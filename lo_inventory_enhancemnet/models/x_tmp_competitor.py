# -*- coding: utf-8 -*-
from odoo import fields, models


class TmpCompetitor(models.Model):
    _name = "x.tmp_competitor"
    _description = "Temp_Competior"

    x_name = fields.Char('Name')
    x_competitor_1 = fields.Float('J-Mart')
    x_competitor_2 = fields.Float('Sokthavy')
    x_competitor_3 = fields.Float('D-Mart')
    x_competitor_4 = fields.Float('Ramping')
    x_competitor_5 = fields.Float('Paksun')
