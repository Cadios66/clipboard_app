import shutil
from tkinter import colorchooser
import os
import colorsys
import config
import json

class setting:
    def __init__(self, main_window):
        self.main_window = main_window

    def color_choose(self):
        color = colorchooser.askcolor()
        if color and color[1]:
            config.background_color = color[1]
            self.main_window.configure(bg = config.background_color)

            import gui
            gui.update_button_colors(self)
            choice = gui.combobox.get()
            gui.selected_sort(choice)
        file_path = config.settings_path
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    settings = json.load(f)
            settings['bg_color'] = config.background_color
            with open(file_path, 'w') as f:
                json.dump(settings, f)
        except Exception as e:
            print(f"Ошибка: {e}")

    def quit_app(self):
        lock_path = os.path.join(config.folder_path, "running.txt")
        if os.path.exists(lock_path):
            os.remove(lock_path)
        self.main_window.quit()

    @staticmethod
    def lighten_color(amount=0.5):
        color = config.background_color

        if not color:
            return "#808080"

        if isinstance(color, str):
            if color.startswith('#'):
                hex_color = color.lstrip('#')
            else:
                hex_color = color
        else:
            return "#808080"
        if len(hex_color) < 6:
            return "#808080"

        try:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
        except ValueError:
            return "#808080"

        r_norm = r / 255.0
        g_norm = g / 255.0
        b_norm = b / 255.0
        h, l, s = colorsys.rgb_to_hls(r_norm, g_norm, b_norm)

        if amount > 0:
            new_l = min(l + amount, 1.0)
        else:
            new_l = max(l + amount, 0.0)

        new_r_norm, new_g_norm, new_b_norm = colorsys.hls_to_rgb(h, new_l, s)

        new_r = int(new_r_norm * 255)
        new_g = int(new_g_norm * 255)
        new_b = int(new_b_norm * 255)

        return f'#{new_r:02x}{new_g:02x}{new_b:02x}'.upper()