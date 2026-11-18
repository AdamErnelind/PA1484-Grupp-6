import sys
import time
import json
import network
import requests
import lvgl as lv

from board_lvgl import start_board 
from debug_log import log
from secrets import WIFI_SSID, WIFI_PASSWORD, TRAFIKLAB_KEY

BLACK = lv.color_hex(0x000000)
WHITE = lv.color_hex(0xFFFFFF)

TRANSPORT_TYPES = ["All", "Bus", "Train", "Ferry"]
STOPS = ["Karlskrona Resecentrum", "Karlskrona Pottholmen", "Karlskrona Campus"]
API = "https://realtime-api.trafiklab.se/v1" 

def hämta_avgångar(stop_namn):
    pass

class Application:
    def __init__(self):
        self.display, self.touch, self.handler = start_board()
        
        # Ladda sparade inställningar när enheten startar
        self.settings = self.load_settings()
        
        self.create_ui()
        self.connect_wifi()
        self.show_departures()
        log("student application ready")

    def load_settings(self):
        'Laddar inställningar från fil, returnerar default om filen inte finns.'
        try:
            with open("settings.json", "r") as f:
                return json.load(f)
        except Exception:
            return {"stop_index": 0, "transport_index": 0}

    def save_settings(self, _event):
        'Sparar nuvarande val som standard (US3.4)'
        self.settings["stop_index"] = self.stop_dropdown.get_selected()
        self.settings["transport_index"] = self.transport_dropdown.get_selected()
        try:
            with open("settings.json", "w") as f:
                json.dump(self.settings, f)
            log("Settings saved to flash.")
        except Exception as e:
            log("Failed to save settings: %r" % (e,))

    def reset_settings(self, _event):
        '''Återställer till sparade inställningar från filen (US3.5)'''
        self.settings = self.load_settings()
        self.stop_dropdown.set_selected(self.settings.get("stop_index", 0))
        self.transport_dropdown.set_selected(self.settings.get("transport_index", 0))
        self.show_departures()

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
        self.title_label = lv.label(self.tile1)
        self.title_label.set_text("Public Transport Info")
        self.title_label.set_style_text_font(lv.font_montserrat_28, 0)
        self.title_label.set_style_text_color(BLACK, 0)
        self.title_label.align(lv.ALIGN.TOP_MID, 0, 40)
        
        self.version_label = lv.label(self.tile1)
        self.version_label.set_text("Version: 3.0.0")
        self.version_label.set_style_text_color(BLACK, 0)
        self.version_label.align(lv.ALIGN.TOP_MID, 0, 80)

        self.group_label = lv.label(self.tile1)
        self.group_label.set_text("Grupp 6")
        self.group_label.set_style_text_color(BLACK, 0)
        self.group_label.align(lv.ALIGN.CENTER, 0, -30)

        self.members_label = lv.label(self.tile1)
        self.members_label.set_text("Medlemmar:\nAdam\nOlle\nOliver\nPetter\nFritz")
        self.members_label.set_style_text_color(BLACK, 0)
        self.members_label.align(lv.ALIGN.CENTER, 0, 25)
        
        self.tile3 = self.tileview.add_tile(0, 1, lv.DIR.TOP)

    def create_departure_screen(self):
        'Function: Creates the departure screen (US1.2B)'
        self.stop_label = lv.label(self.tile2)
        self.stop_label.set_text("Departures")
        self.stop_label.set_style_text_font(lv.font_montserrat_28, 0)
        self.stop_label.set_style_text_color(BLACK, 0)
        self.stop_label.align(lv.ALIGN.TOP_MID, 0, 8)

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
        'Function: Creates the settings screen (US3.1, US3.2B, US3.4, US3.5)'
        self.settings_title = lv.label(self.tile3)
        self.settings_title.set_text("Settings")
        self.settings_title.set_style_text_font(lv.font_montserrat_28, 0)
        self.settings_title.set_style_text_color(BLACK, 0)
        self.settings_title.align(lv.ALIGN.TOP_MID, 0, 40)

        # Välj Hållplats
        self.stop_hint = lv.label(self.tile3)
        self.stop_hint.set_text("Select stop:")
        self.stop_hint.set_style_text_color(BLACK, 0)
        self.stop_hint.align(lv.ALIGN.TOP_MID, 0, 100)

        self.stop_dropdown = lv.dropdown(self.tile3)
        self.stop_dropdown.set_options("\n".join(STOPS)) # Ändrad från den tidigare listkomprehensionen som kraschade
        self.stop_dropdown.set_width(400)
        self.stop_dropdown.align(lv.ALIGN.TOP_MID, 0, 130)
        self.stop_dropdown.set_selected(self.settings.get("stop_index", 0))
        self.stop_dropdown.add_event_cb(self.on_stop_selected, lv.EVENT.VALUE_CHANGED, None)

        # Välj Transportmedel
        self.transport_hint = lv.label(self.tile3)
        self.transport_hint.set_text("Select transport type:")
        self.transport_hint.set_style_text_color(BLACK, 0)
        self.transport_hint.align(lv.ALIGN.TOP_MID, 0, 180)

        self.transport_dropdown = lv.dropdown(self.tile3)
        self.transport_dropdown.set_options("\n".join(TRANSPORT_TYPES))
        self.transport_dropdown.set_width(400)
        self.transport_dropdown.align(lv.ALIGN.TOP_MID, 0, 210)
        self.transport_dropdown.set_selected(self.settings.get("transport_index", 0))

        # Spara inställningar
        self.save_btn = lv.btn(self.tile3)
        self.save_btn.align(lv.ALIGN.TOP_MID, -80, 280)
        self.save_btn.add_event_cb(self.save_settings, lv.EVENT.CLICKED, None)
        self.save_label = lv.label(self.save_btn)
        self.save_label.set_text("Save Default")

        # Återställa inställningar
        self.reset_btn = lv.btn(self.tile3)
        self.reset_btn.align(lv.ALIGN.TOP_MID, 80, 280)
        self.reset_btn.add_event_cb(self.reset_settings, lv.EVENT.CLICKED, None)
        self.reset_label = lv.label(self.reset_btn)
        self.reset_label.set_text("Reset Default")

    def on_stop_selected(self, _event):
        'Function: Körs när man väljer en annan hållplats'
        self.show_departures()

    def show_departures(self):
        'Function: Visar avgångarna för vald hållplats i tabellen'
        index = self.stop_dropdown.get_selected()
        stop_namn = STOPS[index]
        self.stop_label.set_text(stop_namn)
        
        # En platshållare tills din faktiska API-hämtning läggs in
        avgangar = [("--:--", "-", "Ingen data", "-")]

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

# Denna API-request lämnas orörd från din originalkod
r = requests.get("https://realtime-api.trafiklab.se/v1/stops/list?key=88c347806f764951ba7df2c95a79735b")
if r.status_code == 200:
    r.json()["stations"]