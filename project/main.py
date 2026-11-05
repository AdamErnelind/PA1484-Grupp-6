import sys
import time

import lvgl as lv
import network

from board_lvgl import start_board
from debug_log import log

from secrets import WIFI_SSID, WIFI_PASSWORD

BLACK = lv.color_hex(0x000000)
WHITE = lv.color_hex(0xFFFFFF)

# Exempeldata: hållplatsnamn och deras avgångar
# Varje avgång är (tid, linje, destination, status)
STOPS = [
    ("Karlskrona Resecentrum", [
        ("14:30", "1", "Lyckeby", "On time"),
        ("14:42", "4", "Nattraby", "Delayed +3 min"),
        ("14:55", "2", "Rodeby", "Scheduled"),
        ("15:10", "1", "Lyckeby", "Cancelled"),
    ]),
    ("Karlskrona Pottholmen", [
        ("14:35", "3", "Jamjo", "On time"),
        ("14:50", "1", "Resecentrum", "On time"),
        ("15:05", "3", "Jamjo", "Scheduled"),
    ]),
    ("Karlskrona Campus", [
        ("14:38", "2", "Resecentrum", "Delayed +5 min"),
        ("15:00", "4", "NAttraby", "On time"),
    ]),
]

TRANSPORT_TYPES = ["All", "Bus", "Train", "Ferry"]

class Application:
    def __init__(self):
        self.display, self.touch, self.handler = start_board()
        self.create_ui()
        self.show_departures()   # visa avgångar för första hållplatsen
        self.connect_wifi()
        log("student application ready")

    def create_ui(self):
        'Function: Creates UI'
        self.tileview = lv.tileview(lv.screen_active())
        self.tileview.set_size(600, 450)
        self.tileview.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)

        self.tile1 = self.tileview.add_tile(0, 0, lv.DIR.RIGHT)
        self.tile2 = self.tileview.add_tile(1, 0, lv.DIR.HOR)
        self.tile3 = self.tileview.add_tile(2, 0, lv.DIR.LEFT)

        # Vit bakgrund på alla skärmar så att svart text syns
        for tile in (self.tile1, self.tile2, self.tile3):
            tile.set_style_bg_opa(lv.OPA.COVER, 0)
            tile.set_style_bg_color(WHITE, 0)

        self.create_start_screen()
        self.create_departure_screen()
        self.create_settings_screen()

    def create_start_screen(self):
        'Function: Creates the start screen (US1.1)'
        # 1. Projektnamn
        self.title_label = lv.label(self.tile1)
        self.title_label.set_text("Public Transport Info")
        self.title_label.set_style_text_font(lv.font_montserrat_28, 0)
        self.title_label.set_style_text_color(BLACK, 0)
        # Centrera i toppen och flytta ner 40 pixlar
        self.title_label.align(lv.ALIGN.TOP_MID, 0, 40)
        # 2. Programversion
        self.version_label = lv.label(self.tile1)
        self.version_label.set_text("Version: 1.0.0")
        self.version_label.set_style_text_color(BLACK, 0)
        # Flytta ner 80 pixlar från toppen så den hamnar under titeln
        self.version_label.align(lv.ALIGN.TOP_MID, 0, 80)

        # 3. Gruppnummer
        self.group_label = lv.label(self.tile1)
        self.group_label.set_text("Grupp 6")
        self.group_label.set_style_text_color(BLACK, 0)
        # Utgå från mitten men flytta upp 30 pixlar (negativt Y-värde)
        self.group_label.align(lv.ALIGN.CENTER, 0, -30)

        # 4. Gruppmedlemmar
        self.members_label = lv.label(self.tile1)
        self.members_label.set_text("Medlemmar:\nAdam\nOlle\nOliver\nPetter\nFritz")
        self.members_label.set_style_text_color(BLACK, 0)
        # Utgå från mitten och flytta ner 25 pixlar
        self.members_label.align(lv.ALIGN.CENTER, 0, 25)

        #Välj transportmedel
        self.transport_hint = lv.label(self.tile3)
        self.transport_hint.set_text("Select transport type:")
        self.transport_hint.set_style_text_color(BLACK, 0)
        self.transport_hint.align(lv.ALIGN.TOP_MID, 0, 220)

        self.transport_dropdown = lv.dropdown(self.tile3)
        self.transport_dropdown.set_options("\n".join(TRANSPORT_TYPES))
        self.transport_dropdown.set_width(400)
        self.transport_dropdown.align(lv.ALIGN.TOP_MID, 0, 250)

    def create_departure_screen(self):
        'Function: Creates the departure screen (US1.2B)'
        # Hållplatsens namn högst upp
        self.stop_label = lv.label(self.tile2)
        self.stop_label.set_text("Departures")
        self.stop_label.set_style_text_font(lv.font_montserrat_28, 0)
        self.stop_label.set_style_text_color(BLACK, 0)
        self.stop_label.align(lv.ALIGN.TOP_MID, 0, 8)

        # Tabell med 4 kolumner: tid, linje, destination, status
        self.table = lv.table(self.tile2)
        self.table.set_size(580, 330)
        self.table.align(lv.ALIGN.TOP_MID, 0, 55)
        self.table.set_column_count(4)
        self.table.set_column_width(0, 90)
        self.table.set_column_width(1, 80)
        self.table.set_column_width(2, 250)
        self.table.set_column_width(3, 160)
        self.table.set_style_bg_color(WHITE, lv.PART.ITEMS)
        self.table.set_style_text_color(BLACK, lv.PART.ITEMS)

    def create_settings_screen(self):
        'Function: Creates the settings screen (US3.1, US3.2B)'
        self.settings_title = lv.label(self.tile3)
        self.settings_title.set_text("Settings")
        self.settings_title.set_style_text_font(lv.font_montserrat_28, 0)
        self.settings_title.set_style_text_color(BLACK, 0)
        self.settings_title.align(lv.ALIGN.TOP_MID, 0, 40)

        self.stop_hint = lv.label(self.tile3)
        self.stop_hint.set_text("Select stop:")
        self.stop_hint.set_style_text_color(BLACK, 0)
        self.stop_hint.align(lv.ALIGN.TOP_MID, 0, 100)

        # Dropdown där man väljer hållplats. Namnen hämtas från STOPS.
        namn = [stop_namn for stop_namn, _ in STOPS]
        self.stop_dropdown = lv.dropdown(self.tile3)
        self.stop_dropdown.set_options("\n".join(namn))
        self.stop_dropdown.set_width(400)
        self.stop_dropdown.align(lv.ALIGN.TOP_MID, 0, 130)
        self.stop_dropdown.add_event_cb(
            self.on_stop_selected, lv.EVENT.VALUE_CHANGED, None
        )

    def on_stop_selected(self, _event):
        'Function: Körs när man väljer en annan hållplats'
        self.show_departures()

    def show_departures(self):
        'Function: Visar avgångarna för vald hållplats i tabellen'
        # Vilken hållplats är vald i dropdownen? (0 = första, 1 = andra, ...)
        index = self.stop_dropdown.get_selected()
        stop_namn, avgangar = STOPS[index]
        self.stop_label.set_text(stop_namn)

        # Rubrikrad + en rad per avgång
        self.table.set_row_count(len(avgangar) + 1)
        for kolumn, text in enumerate(("Time", "Line", "Destination", "Status")):
            self.table.set_cell_value(0, kolumn, text)
        for rad, avgang in enumerate(avgangar, 1):
            for kolumn, text in enumerate(avgang):
                self.table.set_cell_value(rad, kolumn, text)

    @staticmethod
    def connect_wifi():
        'Function: Connects to WiFi'
        log("connecting to Wi-Fi SSID: " + WIFI_SSID)
        station = network.WLAN(network.STA_IF)
        station.active(True)
        station.connect(WIFI_SSID, WIFI_PASSWORD)
        started = time.ticks_ms()
        while (not station.isconnected() and
               time.ticks_diff(time.ticks_ms(), started) < 15_000):
            time.sleep_ms(250)
        log("Wi-Fi connected" if station.isconnected()
            else "Wi-Fi could not connect (timeout)")


try:
    app = Application()
except Exception as error:
    log("FATAL: %r" % (error,))
    sys.print_exception(error)
    raise