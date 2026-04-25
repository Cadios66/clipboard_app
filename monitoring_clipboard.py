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
        image.save(buffer, format="PNG", quality=m)
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


def preload_data():
    current_folder = create_folder_for_days()
    if not current_folder or not os.path.exists(current_folder):
        return

    if not hasattr(config, 'image_hashes'):
        config.image_hashes = set()
    image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp')
    for entry in os.scandir(current_folder):
        if entry.is_file():
            if entry.name.endswith('.txt'):
                try:
                    with open(entry.path, "r", encoding='utf-8') as f:
                        content = f.read().strip()
                        if content not in config.copied_things:
                            config.copied_things.append(content)
                except:
                    continue
            elif entry.name.endswith(image_extensions):
                try:
                    with Image.open(entry.path) as img:
                        temp_box = io.BytesIO()
                        img.save(temp_box, format='PNG')
                        config.image_hashes.add(hashlib.md5(temp_box.getvalue()).hexdigest())
                except:
                    continue


def create_folder_for_days():
    if not config.folder_to_save:
        if not config.show_warning:
            messagebox.showwarning("Внимание", "Перед началом работы приложения, выберите папку для сохранения")
            config.show_warning = True
        return None
    try:
        today_date = str(date.today())
        path = os.path.join(config.folder_path, today_date)
        if not os.path.exists(path):
            os.makedirs(path)
        gui.update_combobox_date(today_date)
        return path
    except Exception as e:
        print(f"Ошибка: {e}")
        return None


def find_duplicate(content, directory):
    if not os.path.exists(directory): return False
    for entry in os.scandir(directory):
        if entry.is_file() and entry.name.endswith('.txt'):
            try:
                with open(entry.path, "r", encoding='utf-8') as f:
                    if f.read().strip() == content.strip(): return True
            except:
                continue
    return False


def check_clipboard(app, selected_sort, combobox):
    preload_data()
    try:
        last_clipboard = app.clipboard_get()
    except:
        last_clipboard = ""

    last_image_hash = None
    was_monitoring_last_state = config.monitoring

    while not config.stop:
        if config.monitoring:
            if not was_monitoring_last_state:
                try:
                    last_clipboard = app.clipboard_get()
                    img_init = ImageGrab.grabclipboard()
                    if isinstance(img_init, Image.Image):
                        buf = io.BytesIO()
                        img_init.save(buf, format='PNG')
                        last_image_hash = hashlib.md5(buf.getvalue()).hexdigest()
                except:
                    pass
                was_monitoring_last_state = True

            img = ImageGrab.grabclipboard()
            if isinstance(img, Image.Image):
                if config.stop or not config.monitoring: continue
                try:
                    img_byte_arr = io.BytesIO()
                    img.save(img_byte_arr, format='PNG')
                    img_bytes = img_byte_arr.getvalue()
                    current_hash = hashlib.md5(img_bytes).hexdigest()

                    if not hasattr(config, 'image_hashes'):
                        config.image_hashes = set()

                    if current_hash != last_image_hash and current_hash not in config.image_hashes:
                        current_folder = create_folder_for_days()
                        if not current_folder:
                            time.sleep(1)
                            continue

                        config.copied_things.append(img)
                        config.image_hashes.add(current_hash)

                        name_of_image = f"image_{datetime.now().strftime('%H-%M-%S')}.png"
                        full_path = os.path.join(current_folder, name_of_image)
                        shrink_the_image(img, full_path, 1000000)

                        last_image_hash = current_hash
                        last_clipboard = ""
                        if app.winfo_exists():
                            current_filter = combobox.get()
                            app.after(0, lambda f=current_filter: gui.selected_sort(f))
                except Exception as e:
                    print(f"Ошибка картинки: {e}")
            else:
                try:
                    current_clipboard = app.clipboard_get()
                    if current_clipboard != last_clipboard and current_clipboard:
                        if getattr(config, 'ignore_next_clipboard', False):
                            config.ignore_next_clipboard = False
                            last_clipboard = current_clipboard
                            continue

                        if current_clipboard in config.copied_things:
                            last_clipboard = current_clipboard
                            continue

                        current_folder = create_folder_for_days()
                        if not current_folder:
                            time.sleep(1)
                            continue

                        if find_duplicate(current_clipboard, current_folder):
                            last_clipboard = current_clipboard
                            if current_clipboard not in config.copied_things:
                                config.copied_things.append(current_clipboard)
                            continue

                        config.copied_things.append(current_clipboard)
                        curr_time = datetime.now().strftime("%H_%M_%S")
                        file_path = os.path.join(current_folder, f"{curr_time}.txt")

                        with open(file_path, "w", encoding='utf-8') as file:
                            file.write(current_clipboard)

                        last_clipboard = current_clipboard
                        last_image_hash = None
                        if app.winfo_exists():
                            current_filter = combobox.get()
                            app.after(0, lambda f=current_filter: gui.selected_sort(f))
                except tk.TclError:
                    pass
                except Exception as e:
                    print(f"Ошибка текста: {e}")
        else:
            was_monitoring_last_state = False
            try:
                last_clipboard = app.clipboard_get()
            except:
                pass
            time.sleep(0.5)
        time.sleep(0.2)


def start_monitoring(app, selected_sort, combobox):
    clipboard_thread = threading.Thread(
        target=check_clipboard,
        args=(app, selected_sort, combobox),
        daemon=True
    )
    clipboard_thread.start()
    return clipboard_thread