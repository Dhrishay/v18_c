# -*- coding: utf-8 -*-
###############################################################################
#
#   Copyright (C) 2004-today OpenERP SA (<http://www.openerp.com>)
#   Copyright (C) 2016-today Geminate Consultancy Services (<http://geminatecs.com>).
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
{
    'name': 'POS Inventory Adjustment',
    "version": "18.0.0.1",
    'category': 'Point of Sale',
    'summary': "Geminate comes with a feature for inventory adjustments using point of sale. In the POS screen, you can add multiple products with different qtys and whenever you click on the 'Adjust Inventory' button it will create new Inventory Adjustments.",
    'website': '',
    'author': '',
    'license': 'Other proprietary',
    'depends': ['point_of_sale','lo_inventory_enhancemnet'],
    "description": "Geminate comes with a feature for inventory adjustments using point of sale. In the POS screen, you can add multiple products with different qtys and whenever you click on the 'Adjust Inventory' button it will create new Inventory Adjustments. If the inventory adjustment checkbox is checked on POS session configuration then only the 'Adjust Inventory' button will be available on POS screen. you can configure the inventoried location on POS session configuration which will set as stock location on inventory adjustment.",
    'data': [
            'security/ir.model.access.csv',

            # 'wizard/counted_wizard_view.xml',
            'wizard/corrected_wizard_view.xml',

            # 'report/stock_counted_template.xml',
            # 'report/stock_summary_template.xml',
            # 'report/stock_corrected_template.xml',
            # 'report/stock_diff_amount_template.xml',
            # 'report/stock_notscan_template.xml',
            # 'report/report.xml',

            'views/pos_config_view.xml',
            'views/pos_inventory_adjustments_view.xml',
            'views/prepare_count.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'lo_pos_inventory_adjustment/static/src/js/inventory_adjustment.js',
            'lo_pos_inventory_adjustment/static/src/js/hide_numpad.js',
            'lo_pos_inventory_adjustment/static/src/xml/hide_numpad.xml',
            'lo_pos_inventory_adjustment/static/src/xml/inventory_adjustment.xml',
        ],
    },
    'images': ['static/description/pos_inventory_adjustment.png'],
    'installable': True,
    'auto_install': False,
    'application': False,
    'price': 54.99,
    'currency': 'EUR'
}
#
###############################################################################
