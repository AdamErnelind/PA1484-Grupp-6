import sys
import time

import lvgl as lv
import network

from board_lvgl import start_board
from debug_log import log

from secrets import WIFI_SSID, WIFI_PASSWORD


class Application:
    def __init__(self):
        self.display, self.touch, self.handler = start_board()
        self.tile2_dark = False
        self.create_ui()
        self.connect_wifi()
        log("student application ready")

    @staticmethod
    def apply_tile_colors(tile, label, dark):
        tile.set_style_bg_opa(lv.OPA.COVER, 0)
        tile.set_style_bg_color(
            lv.color_hex(0x000000 if dark else 0xFFFFFF), 0
        )
        label.set_style_text_color(
            lv.color_hex(0xFFFFFF if dark else 0x000000), 0
        )

    def on_tile2_clicked(self, _event):
        self.tile2_dark = not self.tile2_dark
        self.apply_tile_colors(self.tile2, self.tile2_label, self.tile2_dark)

    def create_ui(self):
        'Function: Creates UI'
        self.tileview = lv.tileview(lv.screen_active())
        self.tileview.set_size(600, 450)
        self.tileview.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)

        self.tile1 = self.tileview.add_tile(0, 0, lv.DIR.RIGHT)
        self.tile2 = self.tileview.add_tile(1, 0, lv.DIR.LEFT)

        self.tile1.set_style_bg_opa(lv.OPA.COVER, 0)
        self.tile1.set_style_bg_color(lv.color_hex(0xFFFFFF), 0)

        self.tile2_label = lv.label(self.tile2)
        self.tile2_label.set_text("This is a test")
        self.tile2_label.set_style_text_font(lv.font_montserrat_28, 0)
        self.tile2_label.center()
        self.apply_tile_colors(self.tile2, self.tile2_label, False)
        self.tile2.add_flag(lv.obj.FLAG.CLICKABLE)
        self.tile2.add_event_cb(self.on_tile2_clicked, lv.EVENT.CLICKED, None)
        # 1. Projektnamn
        self.title_label = lv.label(self.tile1)
        self.title_label.set_text("Public Transport Info")
        self.title_label.set_style_text_font(lv.font_montserrat_28, 0)
        self.title_label.set_style_text_color(lv.color_hex(0x000000), 0)
        # Centrera i toppen och flytta ner 40 pixlar
        self.title_label.align(lv.ALIGN.TOP_MID, 0, 40)
        # 2. Programversion
        self.version_label = lv.label(self.tile1)
        self.version_label.set_text("Version: 1.0.0")
        self.version_label.set_style_text_color(lv.color_hex(0x000000), 0)
        # Flytta ner 80 pixlar från toppen så den hamnar under titeln
        self.version_label.align(lv.ALIGN.TOP_MID, 0, 80)

        # 3. Gruppnummer
        self.group_label = lv.label(self.tile1)
        self.group_label.set_text("Grupp 6") 
        self.group_label.set_style_text_color(lv.color_hex(0x000000), 0)
        # Utgå från mitten men flytta upp 30 pixlar (negativt Y-värde)
        self.group_label.align(lv.ALIGN.CENTER, 0, -30)

        # 4. Gruppmedlemmar
        self.members_label = lv.label(self.tile1)
        self.members_label.set_text("Medlemmar:\nAdam\nOlle\nOliver\nPetter\nFritz")
        self.members_label.set_style_text_color(lv.color_hex(0x000000), 0)
        # Utgå från mitten och flytta ner 25 pixlar
        self.members_label.align(lv.ALIGN.CENTER, 0, 25)

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

