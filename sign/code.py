############################################################################################################################################################################

# ON AIR / OFF AIR
# Runs on Matrix Portal with 64x32 RGB Matrix display
# Based on the Adafruit RGB Matrix Automatic YouTube ON AIR Sign

############################################################################################################################################################################

import time
import board
import busio
import displayio
import adafruit_display_text.label

import adafruit_requests as requests
import adafruit_esp32spi.adafruit_esp32spi_socket as socket

from adafruit_esp32spi import adafruit_esp32spi
from digitalio import DigitalInOut, Pull
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.polygon import Polygon
from adafruit_bitmap_font import bitmap_font
from adafruit_matrixportal.matrix import Matrix
from adafruit_debouncer import Debouncer

############################################################################################################################################################################

STATUS_URL = 'http://192.168.178.23:6006/get_status'
TIME_URL = 'http://worldtimeapi.org/api/timezone/Europe/Berlin'
NIGHT_MODE = False
TIME_SLEEP = 2
CHECK_TIME_CONST = int(600/TIME_SLEEP) # only check time once ~10 minutes
OFFLINE_MODE = False

############################################################################################################################################################################

# --- Network setup ---

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print('WiFi secrets are kept in secrets.py, please add them there!')
    raise

esp32_cs = DigitalInOut(board.ESP_CS)
esp32_ready = DigitalInOut(board.ESP_BUSY)
esp32_reset = DigitalInOut(board.ESP_RESET)

spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)

requests.set_socket(socket, esp)

# --- Display setup ---
matrix = Matrix()
display = matrix.display

# --- Button setup ---
pin_down = DigitalInOut(board.BUTTON_DOWN)
pin_down.switch_to_input(pull=Pull.UP)
button_down = Debouncer(pin_down)
pin_up = DigitalInOut(board.BUTTON_UP)
pin_up.switch_to_input(pull=Pull.UP)
button_up = Debouncer(pin_up)

# --- Drawing setup ---
group = displayio.Group()
bitmap = displayio.Bitmap(64, 32, 2)  # width, height, bit depth

# Create a color palette
COLOR_BLACK = 0
COLOR_RED = 1
COLOR_WHITE = 2
COLOR_GOLD = 3
COLOR_GREEN = 4
COLOR_BLUE = 5
COLOR_DARK_BLUE = 6
COLOR_DARK_GREEN = 7
COLOR_DARK_RED = 8
COLOR_DARK_GOLD = 9

color = displayio.Palette(10)
color[COLOR_BLACK] = 0x000000
color[COLOR_RED] = 0xFF0000
color[COLOR_WHITE] = 0x444444
color[COLOR_GOLD] = 0xDD8000
color[COLOR_GREEN] = 0x00FF00
color[COLOR_DARK_BLUE] = 0x0000FF
color[COLOR_BLUE] = 0x104BA4
color[COLOR_DARK_RED] = 0x8B0000
color[COLOR_DARK_GREEN] = 0x006400
color[COLOR_DARK_GOLD] = 0xB8860B

# Create a TileGrid using the Bitmap and Palette
tile_grid = displayio.TileGrid(bitmap, pixel_shader=color)
group.append(tile_grid)

# draw the frame for startup
rect1 = Rect(0, 0, 2, 32, fill=color[COLOR_WHITE])
rect2 = Rect(62, 0, 2, 32, fill=color[COLOR_WHITE])
rect3 = Rect(2, 0, 9, 2, fill=color[COLOR_WHITE])
rect4 = Rect(53, 0, 9, 2, fill=color[COLOR_WHITE])
rect5 = Rect(2, 30, 12, 2, fill=color[COLOR_WHITE])
rect6 = Rect(50, 30, 12, 2, fill=color[COLOR_WHITE])

group.append(rect1)
group.append(rect2)
group.append(rect3)
group.append(rect4)
group.append(rect5)
group.append(rect6)

def redraw_frame(fill_color: int):  # to adjust spacing at bottom later
    rect1.fill = color[fill_color]
    rect2.fill = color[fill_color]
    rect3.fill = color[fill_color]
    rect4.fill = color[fill_color]
    rect5.fill = color[fill_color]
    rect6.fill = color[fill_color]

# draw the wings w polygon shapes
wing_polys = []

wing_polys.append(Polygon([(3, 3), (9, 3), (9, 4), (4, 4)], outline=color[COLOR_RED]))
wing_polys.append(Polygon([(5, 6), (9, 6), (9, 7), (6, 7)], outline=color[COLOR_RED]))
wing_polys.append(Polygon([(7, 9), (9, 9), (9, 10), (8, 10)], outline=color[COLOR_RED]))
wing_polys.append(Polygon([(54, 3), (60, 3), (59, 4), (54, 4)], outline=color[COLOR_RED]))
wing_polys.append(Polygon([(54, 6), (58, 6), (57, 7), (54, 7)], outline=color[COLOR_RED]))
wing_polys.append(Polygon([(54, 9), (56, 9), (55, 10), (54, 10)], outline=color[COLOR_RED]))

for wing_poly in wing_polys:
    group.append(wing_poly)

def redraw_wings(index):  # to change colors
    for wing in wing_polys:
        wing.outline = color[index]

# --- Content Setup ---
deco_font = bitmap_font.load_font('/BellotaText-Bold-21.bdf')

# text positions
on_x = 15
on_y = 9
off_x = 12
off_y = 9
air_x = 15
air_y = 25

text_line1 = adafruit_display_text.label.Label(deco_font, color = color[COLOR_WHITE], text = 'OFF')
text_line1.x = off_x
text_line1.y = off_y

text_line2 = adafruit_display_text.label.Label(deco_font, colo = color[COLOR_WHITE], text = 'AIR')
text_line2.x = air_x
text_line2.y = air_y

# Put each line of text into the Group
group.append(text_line1)
group.append(text_line2)

def update_text(is_on_air: bool):
    '''
    Update text according to state and night mode
    True = On Air
    False = Off Air
    '''
    if is_on_air:
        if NIGHT_MODE:
            color_text = COLOR_DARK_RED
            color_frame = COLOR_DARK_GOLD
        else:
            color_text = COLOR_RED
            color_frame = COLOR_GOLD

        text_line1.text = 'ON'
        text_line1.x = on_x
        text_line1.color = color[color_text]
        text_line2.text = 'AIR'
        text_line2.x = air_x
        text_line2.color = color[color_text]
        redraw_wings(color_frame)
        redraw_frame(color_frame)
        display.show(group)

    else:
        if NIGHT_MODE:
            color_text = COLOR_DARK_GREEN
            color_frame = COLOR_DARK_BLUE
        else:
            color_text = COLOR_GREEN
            color_frame = COLOR_BLUE

        text_line1.text = 'OFF'
        text_line1.x = off_x
        text_line1.color = color[color_text]
        text_line2.text = 'AIR'
        text_line2.x = air_x
        text_line2.color = color[color_text]
        redraw_wings(color_frame)
        redraw_frame(color_frame)
        display.show(group)

def connect_ap():
    '''
    Connect access point as defined in secrets file
    '''
    print('ESP connection status: ', esp.is_connected)
    while not esp.is_connected:
        try:
            esp.connect_AP(secrets['ssid'], secrets['password'])
        except OSError as e:
            print('Could not connect to AP, retrying: ', e)
            continue
    print('Connected to', str(esp.ssid, 'utf-8'), '\tRSSI:', esp.rssi)
    print('My IP address is', esp.pretty_ip(esp.ip_address))

def get_status():
    '''
    Get on air / off air status from STATUS_URL
    '''
    print('-' * 40)
    print(f'Fetching status from {STATUS_URL}')
    r = requests.get(STATUS_URL)
    assert r.status_code == 200, f'Request status code: {r.status_code}'
    print('Current status: ', r.text)
    print('-' * 40)
    r.close()

    return r.text.strip()

def check_is_nighttime():
    '''
    Fetch current time and set night time variable, daytime is set to 8:00 - 18:00
    '''
    print('-' * 40)
    print(f'Fetching json from {TIME_URL}')
    r = requests.get(TIME_URL)
    assert r.status_code == 200, f'Request status code: {r.status_code}'
    hour = int(r.json()['datetime'][11:13])
    print('Current hour: ', hour)
    print('-' * 40)
    r.close()

    if hour in range(8, 18):
        return False
    else:
        return True

# Initialize display text
update_text(False)

# Connect
connect_ap()

# Check current time for night mode
try:
    NIGHT_MODE = check_is_nighttime()
except:
    print('Initial time check failed, moving on.')

check_time_count = CHECK_TIME_CONST

while True:

    # Check buttons
    button_down.update()
    button_up.update()
    if button_up.fell:
        print('Button up: ON AIR')
        update_text(True)
    elif button_down.fell:
        print('Button down: OFF AIR')
        update_text(False)

    # Check time for night mode once per interval
    if check_time_count <= 0:
        try:
            NIGHT_MODE = check_is_nighttime()
        except:
            print('Could not reach time server, continuing...')
            check_time_count = CHECK_TIME_CONST

    # Fetch status and update display
    if not OFFLINE_MODE:
        try:
            status = get_status()
            if status.lower() == 'on':
                update_text(True)
            elif status.lower() == 'off':
                update_text(False)
            else:
                print(f'ERROR, unknown status {status}')
        except:
            print('ESP connection status: ', esp.is_connected)
            if not esp.is_connected:
                connect_ap()
            print('Failed request, trying again...')

    check_time_count -= 1
    time.sleep(TIME_SLEEP)

############################################################################################################################################################################