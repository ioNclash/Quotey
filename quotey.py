import sys
import os

fontdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
libdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
import epd2in13_V4
import time
from PIL import Image,ImageDraw,ImageFont
import traceback
import json
import random
import textwrap

logging.basicConfig(level=logging.DEBUG)

def wrap_text(text, box, font_path, max_font_size=20, min_font_size=8, line_spacing=1.1):
    x0, y0, x1, y1 = box
    box_width = x1 - x0
    box_height = y1 - y0

    for font_size in range(max_font_size, min_font_size - 1, -1):
        font = ImageFont.truetype(font_path, font_size)

        # Estimate line height using getbbox
        bbox = font.getbbox("A")
        line_height = bbox[3] - bbox[1]
        max_lines = int(box_height // (line_height * line_spacing))

        lines = []
        # Estimate average char width for wrapping
        avg_char_width = font.getlength("M")
        est_chars_per_line = max(1, int(box_width / avg_char_width))
        wrapped_lines = textwrap.wrap(text, width=est_chars_per_line)

        for line in wrapped_lines:
            line_width = font.getlength(line)
            if line_width <= box_width:
                lines.append(line)
            else:
                # If still too long, wrap again with finer width
                sub_lines = textwrap.wrap(line, width=int(len(line) * box_width / line_width))
                lines.extend(sub_lines)

        if len(lines) <= max_lines:
            return lines, font

    return None, None


try:
    #Initialize and Clear e-Paper display
    logging.info("Starting e-Paper quote display")
    epd = epd2in13_V4.EPD()
    logging.info("init and Clear")
    epd.init()
    epd.Clear(0xFF)

    #Display Quote
    logging.info("Showing quote on e-Paper")
    image = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame    
    draw = ImageDraw.Draw(image)
    
    #Load random quote from json
    with open('quotes.json', 'r') as f:
        quotes = json.load(f)
    choice = random.choice(quotes['quotes'])
    quote = "I am testing that my text can properly wrap itself around the screen without collision issues"#choice['quote']
    source = choice['source']
    author = choice['author']

    #Wrap text to fit screen
    quote_box = (0, 0, epd.height-5, epd.width - 50)
    source_box = (0, epd.width - 50, epd.height-5, epd.width)

    wrapped_quote, quote_font = wrap_text(quote, quote_box, os.path.join(fontdir, 'Font.ttc'), max_font_size=24, min_font_size=12)
    wrapped_source, source_font = wrap_text(f"- {source} by {author}", source_box, os.path.join(fontdir, 'Font.ttc'), max_font_size=18, min_font_size=10)

    draw.multiline_text((quote_box[0], quote_box[1]),"\n".join(wrapped_quote), font=quote_font, fill=0, spacing=2)
    draw.multiline_text((source_box[0], source_box[1]),"\n".join(wrapped_source), font=source_font, fill=0, spacing=2)

   
    # image = image.rotate(180) # Uncomment this line if your display is upside down
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
