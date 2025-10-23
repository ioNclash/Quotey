import sys
import os

fontdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'font')
libdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
import epd2in13_V4
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

logging.basicConfig(level=logging.DEBUG)

try:
    #Initialize and Clear e-Paper display
    logging.info("Starting e-Paper quote display")
    epd = epd2in13_V4.EPD()
    logging.info("init and Clear")
    epd.init()
    epd.Clear(0xFF)

    # load font
    font15 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 15)
    font24 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 24)

    #Display Quote
    logging.info("Showing quote on e-Paper")
    image = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame    
    draw = ImageDraw.Draw(image)
    quote = "It's not a bug, it's a feature"
    draw.text(120,60, quote, font = font24, fill = 0)
    epd.display(epd.getbuffer(image))
    epd.sleep()

    time.sleep(15)
    logging.info("Done")
    epd.init()
    epd.Clear(0xFF)
    epd2in13_V4.epdconfig.module_exit(cleanup=True)


except IOError as e:
    logging.info(e)
except KeyboardInterrupt:
    logging.info("ctrl + c:")
    epd2in13_V4.epdconfig.module_exit()
    exit()