# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Laoodoo
# See LICENSE file for full copyright and licensing details.

import base64
import json
import logging
from io import BytesIO
from time import sleep
from PIL import Image
from escpos.printer import Network
from odoo.http import Controller, route, request

_logger = logging.getLogger(__name__)


class EventController(Controller):

    def imgcrop(self, im):
        ret = []
        imgwidth, imgheight = im.size
        xPieces = 1
        yPieces = int(imgheight / 20)

        height = imgheight // yPieces
        width = imgwidth // xPieces
        for i in range(0, yPieces):
            for j in range(0, xPieces):
                end = (i + 1) * height
                if (yPieces == i + 1):
                    end = imgheight
                box = (j * width, i * height, (j + 1) * width, end)
                ret.append(im.crop(box))
        return ret

    @route(['/lo_pos_tcp_escpos_printer/print'], type='json', auth='public', methods=['POST'], csrf=False)
    def lo_pos_tcp_escpos_printer(self):
        try:
            data = json.loads(request.httprequest.data)
            ip = data['ip']
            port = data.get('port', 9100)
            cashdrawer = data.get('escpos_print_cashdrawer', False)
            printer = Network(ip, port)
            if data.get('sticker_printer', False):
                if isinstance(data['sticker_data'], list):
                    for sticker in data['sticker_data']:
                        _logger.info('Printing %s', sticker)
                        sticker = sticker.replace('@', '\n')
                        printer._raw(sticker.encode())
                        printer.cut()
                else:
                    for sticker in data['sticker_data']:
                        _logger.info('Printing %s', sticker)
                        sticker = sticker.replace('@', '\n')
                        printer._raw(sticker.encode())
                        printer.cut()
                sleep(1)
                printer.close()
                return "OK"
            else:
                if cashdrawer:
                    orderprint = 2
                else:
                    orderprint = 1
                for demo in range(0, orderprint):
                    if isinstance(data['img'], list):
                        for im in data['img']:
                            _logger.info('Printing %s', im)
                            imgs = self.imgcrop(Image.open(BytesIO(base64.b64decode(im))))
                            for img in imgs:
                                _logger.info('Printing %s', img)
                                printer.image(img)
                            printer.cut()
                    else:
                        imgs = self.imgcrop(Image.open(BytesIO(base64.b64decode(data['img']))))
                        _logger.info('Printing %s', img)
                        for img in imgs:
                            _logger.info('Printing %s', img)
                            printer.image(img)
                        printer.cut()

                sleep(1)
                if cashdrawer:
                    printer.cashdraw(2)
                printer.close()
                return "OK"

        except Exception as e:
            # Catch any other exceptions and log them
            _logger.error(f"An unexpected error occurred: {e}")
            return {'status': 'error', 'message': 'An unexpected error occurred while processing the print request'}
