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


logging.basicConfig(level=logging.DEBUG)

def wrap_text(text, box, font_path, max_font_size=20, min_font_size=8, line_spacing=1.1):
    x0, y0, x1, y1 = box
    box_width = x1 - x0
    box_height = y1 - y0
    
    for font_size in range(max_font_size, min_font_size - 1, -1):
        font = ImageFont.truetype(font_path, font_size)
        
        # Get accurate line height
        bbox = font.getbbox("Ay")  # Use char with ascender and descender
        line_height = (bbox[3] - bbox[1]) * line_spacing
        max_lines = int(box_height / line_height)
        
        # Split text into words
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            # Test if adding this word exceeds the width
            test_line = " ".join(current_line + [word])
            test_width = font.getlength(test_line)
            
            if test_width <= box_width:
                # Word fits, add it to current line
                current_line.append(word)
            else:
                # Word doesn't fit
                if current_line:
                    # Save current line and start new one
                    lines.append(" ".join(current_line))
                    current_line = [word]
                    
                    # Check if word itself is too long
                    if font.getlength(word) > box_width:
                        # Need to break the word
                        broken_word = current_line.pop()
                        char_lines = break_word(broken_word, box_width, font)
                        lines.extend(char_lines[:-1])
                        current_line = [char_lines[-1]] if char_lines[-1] else []
                else:
                    # First word is too long, must break it
                    char_lines = break_word(word, box_width, font)
                    lines.extend(char_lines[:-1])
                    current_line = [char_lines[-1]] if char_lines[-1] else []
        
        # Add remaining words
        if current_line:
            lines.append(' '.join(current_line))
        
        # Check if all lines fit
        if len(lines) <= max_lines:
            return lines, font
    
    # If we get here, even min font size doesn't fit
    logging.warning("Could not fit text within box with given font size constraints.")
    font = ImageFont.truetype(font_path, min_font_size)
    return lines[:max_lines], font  # Return truncated lines

def break_word(word, max_width, font):
    lines = []
    current = ""
    
    for char in word:
        test = current + char
        if font.getlength(test) <= max_width:
            current += char
        else:
            if current:
                lines.append(current)
            current = char
    
    if current:
        lines.append(current)
    
    return lines if lines else [""]

def draw_wrapped_text(draw,text,box,font,fill=0,line_spacing=2,align="left"):
    x0,y0,x1,y1 = box
    box_width = x1 - x0

    bbox = font.getbbox("Ay")  # Use char with ascender and descender
    line_height = (bbox[3] - bbox[1]) * line_spacing
    y=y0

    for line in text:
        line_width = font.getlength(line)
        if align == "center":
            x = x0 + (box_width - line_width) / 2
        elif align == "right":
            x = x1 - line_width
        else:  # left
            x = x0
        draw.text((x, y), line, font=font, fill=fill)
        y += line_height

def clear_screen():
    logging.info("Clearing e-Paper display")
    epd = epd2in13_V4.EPD()
    epd.init()
    epd.Clear(0xFF)
    epd2in13_V4.epdconfig.module_exit(cleanup=True)
    with open('current_quote.json', 'w') as f:
        json.dump({"current_quote": "No quote being shown"}, f, indent=4)

def get_random_quote():
    #Load random quote from json
        with open('quotes.json', 'r') as f:
            quotes = json.load(f)
        choice = random.choice(quotes['quotes'])
        quote = choice['quote']
        source = choice['source']
        author = choice['author']

        with open('current_quote.json', 'w') as f:
            json.dump({"current_quote": quote}, f, indent=4)
        return quote, source, author    

def show_quote():
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
        logging.info(f"Image size: {image.size}")  
        draw = ImageDraw.Draw(image)
        
        quote, source, author = get_random_quote()

        #Wrap text to fit screen
        quote_box = (0, 0, epd.height-5, epd.width-40)
        source_box = (0, epd.width - 353, epd.height-5, epd.width)

        wrapped_quote, quote_font = wrap_text(quote, quote_box, os.path.join(fontdir, 'Font.ttc'), max_font_size=24, min_font_size=12)
        wrapped_source, source_font = wrap_text(f"- {source} by {author}", source_box, os.path.join(fontdir, 'Font.ttc'), max_font_size=18, min_font_size=10)

        logging.info(f"Wrapped quote lines: {wrapped_quote}")
        draw_wrapped_text(draw, wrapped_quote, quote_box, quote_font, fill=0, line_spacing=1.2, align="center")
        logging.info(f"Wrapped source lines: {wrapped_source}")
        draw_wrapped_text(draw, wrapped_source, source_box, source_font, fill=0, line_spacing=1.2, align="right")

    
        image = image.rotate(180) # Comment this line if your display is upside down
        epd.display(epd.getbuffer(image))
        epd.sleep()
        logging.info("Display complete")
        epd2in13_V4.epdconfig.module_exit(cleanup=True)


    except IOError as e:
        logging.info(e)
    except KeyboardInterrupt:
        logging.info("ctrl + c:")
        epd2in13_V4.epdconfig.module_exit()
        exit()

if __name__ == "__main__":
    show_quote()