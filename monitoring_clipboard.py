import datetime
import math
import time
import threading
import hashlib
import io
from datetime import date
from datetime import datetime
from PIL import ImageGrab, Image
import tkinter as tk
import config
import os
from tkinter import messagebox
import filters
import gui


def shrink_the_image(image, filename, target):
    min_quality, max_quality = 25, 96
    Qacc = -1
    while min_quality <= max_quality:
        m = math.floor((min_quality + max_quality) / 2)
        buffer = io.BytesIO()
        image.save(buffer, format = "PNG", quality = m)
        s = buffer.getbuffer().nbytes
        if s <= target:
            Qacc = m
            min_quality = m + 1
        elif s > target:
            max_quality = m - 1
        if Qacc > -1:
            image.save(filename, format="PNG", quality=Qacc)
        else:
            print("ERROR: No acceptble quality factor found")

def create_folder_for_days():
    if not config.folder_to_save:
        if not config.show_warning:
            messagebox.showwarning("Внимание", "Перед началом работы приложения, выберите папку для сохранения", )
            config.show_warning = True
        return None
    try:
        today_date = date.today()
        path = os.path.join(config.folder_path, str(today_date))
        if not os.path.exists(path):
            os.makedirs(path)
            gui.update_combobox_date()
            print(f"Папка на {today_date} создана")
        else:
            print(f"Папка на {today_date} уже существует")
        return path
    except Exception as e:
        print(f"Ошибка: {e}")
        return None


def find_duplicate(content, directory):
    if not os.path.exists(directory):
        return False

    for entry in os.scandir(directory):
        if entry.is_file() and entry.name.endswith('.txt'):
            try:
                with open(entry.path, "r", encoding='utf-8') as f:
                    if f.read().strip() == content.strip():
                        return True
            except:
                continue
    return False

def check_clipboard(app, selected_sort, combobox):
    try:
        last_clipboard = app.clipboard_get()
    except:
        last_clipboard = ""
    current_choice = combobox.get()
    last_image_hash = None


    while not config.stop:
        if config.monitoring:
            img = ImageGrab.grabclipboard()
            if isinstance(img, Image.Image):
                if config.stop or not config.monitoring:
                    continue

                try:
                    img_byte_arr = io.BytesIO()
                    img.save(img_byte_arr, format='PNG')
                    img_bytes = img_byte_arr.getvalue()
                    current_hash = hashlib.md5(img_bytes).hexdigest()

                    if current_hash != last_image_hash:
                        if config.stop or not config.monitoring:
                            continue

                        current_folder = create_folder_for_days()
                        gui.update_combobox_date()
                        if not current_folder:
                            print("Ошибка при создании папки")
                            time.sleep(1)
                            continue

                        if config.stop or not config.monitoring:
                            continue

                        config.copied_things.append(img)
                        name_of_image = f"image_{datetime.now().hour}-{datetime.now().minute}-{datetime.now().second}.png"
                        full_path = os.path.join(current_folder, name_of_image)
                        shrink_the_image(img, full_path, 1000000)

                        if not config.stop:
                            app.after(0, current_choice)

                        last_image_hash = current_hash
                        last_clipboard = ""
                        current_filter = combobox.get()
                        app.after(0, lambda: gui.selected_sort(current_filter))
                        print(f"Добавлено новое изображение: {img.size}")
                except Exception as e:
                    print(f"Ошибка обработки изображения: {e}")

            else:
                try:
                    current_clipboard = app.clipboard_get()
                    if current_clipboard != last_clipboard and current_clipboard:
                        if getattr(config, 'ignore_next_clipboard', False):
                            config.ignore_next_clipboard = False
                            last_clipboard = current_clipboard
                            continue
                        if config.stop or not config.monitoring:
                            continue

                        if (not config.copied_things or
                                not isinstance(config.copied_things[-1], str) or
                                config.copied_things[-1] != current_clipboard):

                            current_folder = create_folder_for_days()
                            gui.update_combobox_date()
                            if not current_folder:
                                print("Ошибка при создании папки")
                                time.sleep(1)
                                continue
                            else:
                                if find_duplicate(current_clipboard, current_folder):
                                    last_clipboard = current_clipboard
                                    continue
                            if config.stop or not config.monitoring:
                                continue

                            config.copied_things.append(current_clipboard)
                            curr_time = f"{datetime.now().hour}_{datetime.now().minute}_{datetime.now().second}"
                            file_path = os.path.join(config.folder_path, str(date.today()), f"{curr_time}.txt")

                            with open(file_path, "w", encoding='utf-8') as file:
                                file.write(current_clipboard)

                            if not config.stop:
                                app.after(0, current_choice)

                            last_clipboard = current_clipboard
                            last_image_hash = None
                            current_filter = combobox.get()
                            app.after(0, lambda: gui.selected_sort(current_filter))
                            print(f"Добавлен текст: {current_clipboard[:50]}...")
                except tk.TclError:
                    pass
                except Exception as e:
                    print(f"Ошибка при получении текста: {e}")

        else:
            time.sleep(0.5)

        time.sleep(0.1)


def start_monitoring(app, selected_sort, combobox):
    clipboard_thread = threading.Thread(
        target=check_clipboard,
        args=(app, selected_sort, combobox),
        daemon=True
    )
    clipboard_thread.start()
    return clipboard_thread