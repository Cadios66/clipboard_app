import json
from tkinter import END
import tkinter as tk
from PIL import Image, ImageTk
import config
from datetime import date
from pathlib import Path
import os, io
import customtkinter as ctk
from datetime import datetime, timedelta

import tkinter as tk
import customtkinter as ctk
import os
from datetime import date
import config

import tkinter as tk
import os
from datetime import date
import config


def formated_text(list_of_text):
    def copy_to_clipboard(text):
        list_of_text.clipboard_clear()
        list_of_text.clipboard_append(text)

    list_of_text.configure(state="normal")

    for child in list_of_text.winfo_children():
        child.destroy()

    list_of_text.delete(1.0, "end")

    raw_width = list_of_text.winfo_width()
    tab_pos = raw_width - 60 if raw_width > 10 else 500
    list_of_text.configure(tabs=(tab_pos, tk.RIGHT))

    today_date = date.today()
    directory = os.path.join(config.folder_path, str(today_date))

    if not os.path.exists(directory):
        list_of_text.insert("end", "Папка с данными не найдена\n")
        list_of_text.configure(state="disabled")
        return

    counter = 1
    for entry in os.scandir(directory):
        if entry.is_file() and entry.name.endswith('.txt'):
            try:
                with open(entry.path, "r", encoding='utf-8') as file:
                    content = file.read().strip()

                list_of_text.insert("end", f"{counter}: {content}")
                list_of_text.insert("end", "\t")

                copy_btn = tk.Button(
                    list_of_text,
                    text="📋",
                    command=lambda c=content: copy_to_clipboard(c),
                    bg="#f0f0f0",
                    fg="black",
                    relief="groove",
                    font=("Arial", 9),
                    cursor="hand2",
                    bd=1,
                    padx=5
                )

                list_of_text.window_create("end", window=copy_btn)
                list_of_text.insert("end", "\n" + "_" * 70 +"\n\n")
                counter += 1
            except Exception as e:
                print(f"Error: {e}")

    list_of_text.configure(state="disabled")
    list_of_text.see('1.0')


def show_links(list_of_text):
    today_date = date.today()
    dir = os.path.join(config.folder_path, str(today_date))
    list_of_text.delete(1.0, "end")
    counter = 1

    if not os.path.exists(dir):
        list_of_text.insert("end", "Папка с данными не найдена\n")
        return

    for entry in os.scandir(dir):
        if entry.is_file() and entry.name.endswith('.txt'):
            try:
                with open(entry, "r", encoding='utf-8') as file:
                    content = file.read().strip()

                if content.startswith(('http://', 'https://', 'www.')):
                    list_of_text.insert("end", f"{counter}: {content}\n")
                    list_of_text.insert("end", "-" * 65 + "\n")
                    counter += 1
            except Exception as e:
                print(f"Ошибка чтения {entry.name}: {e}")

    if counter == 1:
        list_of_text.insert("end", "Ссылки не найдены\n")

    list_of_text.see("end")


def show_text(list_of_text):
    today_date = date.today()
    dir = os.path.join(config.folder_path, (str(today_date)))
    list_of_text.delete(1.0, END)
    counter = 1

    for entry in os.scandir(dir):
        if entry.is_file():
            type_of_file = Path(entry)
            if type_of_file.suffix == ".txt":
                with open(entry, "r", encoding='utf-8') as file:
                    content = file.read()
                list_of_text.insert(END, f"{counter}: {content}\n")
                list_of_text.insert(END, "-" * 65 + "\n")
            counter += 1

    list_of_text.see(END)


def show_images(list_of_text):
    list_of_text.configure(state="normal")
    list_of_text.delete(1.0, END)

    today_date = date.today()
    directory = os.path.join(config.folder_path, str(today_date))

    if not os.path.exists(directory):
        list_of_text.insert(END, "Папка с данными не найдена\n")
        list_of_text.configure(state="disabled")
        return

    config.image_references.clear()

    image_files = [f for f in os.listdir(directory) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]

    if not image_files:
        list_of_text.insert(END, "Изображения не найдены\n")
    else:
        for i, img_name in enumerate(image_files, 1):
            try:
                img_path = os.path.join(directory, img_name)

                pil_img = Image.open(img_path)
                max_size = (350, 350)
                pil_img.thumbnail(max_size)

                tk_img = ImageTk.PhotoImage(pil_img)
                config.image_references.append(tk_img)

                list_of_text.insert(END, f"Файл: {img_name}\n")
                list_of_text.image_create(END, image=tk_img)
                list_of_text.insert(END, "\n" + "-" * 65 + "\n")

            except Exception as e:
                print(f"Ошибка загрузки {img_name}: {e}")

    list_of_text.see(END)

def date_filter():
    file_path = os.path.join(config.root_folder, 'settings.json')
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                paths = data.get("folder_path")
                if paths and os.path.exists(paths):
                    dates = os.listdir(paths)
                    dates.append('Все')
                    return dates
                else: return ["Все"]
        else:
            return ["Все"]
    except Exception as e:
        return ["Все"]

def create_json():
    path = os.path.join(config.root_folder, 'settings.json')
    if not os.path.exists(path):
        data = {'auto_delete' : {"period": 0,
            "start_date": datetime.now().isoformat()}, 'bg_color': '#ffffff', 'folder_path':None}
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

print(date_filter())