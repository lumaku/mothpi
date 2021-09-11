# !/usr/bin/python3
# -*- coding:utf-8 -*-

import logging
import datetime
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont  # import the image libraries

EPAPER_HEIGHT = 264
EPAPER_WIDTH = 176

LIST_OF_FONTS = [
    "/usr/share/fonts/truetype/google/Bangers-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/ubuntu/Ubuntu-M.ttf",
    "usr/share/fonts/noto/NotoSansMono-Regular.ttf",
]
DISPLAY_FONT = None
for item in LIST_OF_FONTS:
    if Path(item).exists():
        DISPLAY_FONT = item

try:
    from waveshare_epd import epd2in7
    from gpiozero import Button  # import the Button control from gpiozero

    button_pins = {1: 5, 2: 6, 3: 13, 4: 19}
    button_by_pin = {v: k for k, v in button_pins.items()}
    btn1 = Button(button_pins[1])  # assign each button to a variable
    btn2 = Button(button_pins[2])  # by passing in the pin number
    btn3 = Button(button_pins[3])  # associated with the button
    btn4 = Button(button_pins[4])  #

    epd = epd2in7.EPD()  # get the display object and assing to epd
    epd.init()  # initialize the display
    print("Clear...")  # print message to console (not display) for debugging
    epd.Clear(0xFF)  # clear the display

    DISPLAY_AVAILABLE = True
    logging.info("Display found.")
except:
    logging.error("No display found!")
    DISPLAY_AVAILABLE = False
    epd = False

# Handle button presses
# param Button (passed from when_pressed)
def handle_btn_press(btn):
    # get the button pin number
    pin_number = btn.pin.number
    Epaper.write_string(button_by_pin[pin_number])


class Epaper:
    is_available = DISPLAY_AVAILABLE

    @staticmethod
    def set_button_handler(button_nr, handler_fn):
        logging.info(f"Set button {button_nr} handler to {handler_fn.__name__}")
        if not DISPLAY_AVAILABLE:
            return
        if button_nr == 1:
            btn1.when_pressed = handler_fn
        elif button_nr == 2:
            btn2.when_pressed = handler_fn
        elif button_nr == 3:
            btn3.when_pressed = handler_fn
        elif button_nr == 4:
            btn4.when_pressed = handler_fn
        else:
            raise ValueError(f"button_nr has to be in [1,2,3,4]! ({button_nr})")

    @staticmethod
    def display(HBlackImage: Image):
        HBlackImage.save("/tmp/epaper_display.jpg")
        if DISPLAY_AVAILABLE:
            epd.display(epd.getbuffer(HBlackImage))

    @staticmethod
    def write_string(output_string):
        logging.info(f"Display: {output_string}")
        if not DISPLAY_AVAILABLE:
            return
        HBlackImage = paint_simple_text_output(output_string)
        # Add the images to the display. Both the black and red layers need
        # o be passed in, even if we did not add anything to one of them
        epd.display(epd.getbuffer(HBlackImage))


def paint_simple_text_output(output_string):
    # Drawing on the Horizontal image. We must create an image object
    # for both the black layer and the red layer, even if we are only
    # printing to one layer
    HBlackImage = Image.new("1", (EPAPER_HEIGHT, EPAPER_WIDTH), 255)  # 298*126
    # create a draw object and the font object we will use for the display
    draw = ImageDraw.Draw(HBlackImage)
    font = ImageFont.truetype(font=DISPLAY_FONT, size=30)
    # draw the text to the display. First argument is starting location
    # of the text in pixels
    draw.text((25, 65), output_string, font=font, fill=0)
    return HBlackImage


def paint_status_page(state_dict):
    HBlackImage = Image.new("1", (EPAPER_HEIGHT, EPAPER_WIDTH), 255)  # 298*126
    # create a draw object and the font object we will use for the display
    draw = ImageDraw.Draw(HBlackImage)
    font = ImageFont.truetype(font=DISPLAY_FONT, size=16)
    titlestr = "Mothpi"
    timestr = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    draw.text((15, 15), titlestr, font=font, fill=0)
    draw.text((15, 40), timestr, font=font, fill=0)
    if "last_picture" in state_dict:
        last_pic_str = "~" + state_dict["last_picture"]
        draw.text((15, 60), last_pic_str, font=font, fill=0)
    if "camera" in state_dict:
        camera_str = "OK" if state_dict["camera"] else "??"
        camera_str = f"Cam {camera_str}"
        draw.text((15, 80), camera_str, font=font, fill=0)
    if "display" in state_dict:
        display_str = "OK" if state_dict["display"] else "??"
        display_str = f"Display {display_str}"
        draw.text((100, 80), display_str, font=font, fill=0)
    if "num_pics" in state_dict:
        num_pics_str = f"#{state_dict['num_pics']}"
        draw.text((15, 100), num_pics_str, font=font, fill=0)
    if "footer1" in state_dict:
        draw.text((15, 132), state_dict["footer1"], font=font, fill=0)
    if "footer2" in state_dict:
        draw.text((15, 152), state_dict["footer2"], font=font, fill=0)
    return HBlackImage
