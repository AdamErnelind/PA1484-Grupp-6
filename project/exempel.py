def create_ui(self):
        'Function: Creates UI'
        self.tileview = lv.tileview(lv.screen_active())
        self.tileview.set_size(600, 450)
        self.tileview.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)

        self.tile1 = self.tileview.add_tile(0, 0, lv.DIR.RIGHT)
        self.tile2 = self.tileview.add_tile(1, 0, lv.DIR.LEFT)

        self.tile1_label = lv.label(self.tile1)
        self.tile1_label.set_text("This is Group 6")
        self.tile1_label.set_text("Verision 0.1")
        self.tile1_label.set_style_text_font(lv.font_montserrat_28, 0)
        self.tile1_label.center()
        self.apply_tile_colors(self.tile1, self.tile1_label, False)

        self.tile2_label = lv.label(self.tile2)
        self.tile2_label.set_text("This is a test")
        self.tile2_label.set_style_text_font(lv.font_montserrat_28, 0)
        self.tile2_label.center()
        self.apply_tile_colors(self.tile2, self.tile2_label, False)
        self.tile2.add_flag(lv.obj.FLAG.CLICKABLE)
        self.tile2.add_event_cb(
            self.on_tile2_clicked, lv.EVENT.CLICKED, None
        )