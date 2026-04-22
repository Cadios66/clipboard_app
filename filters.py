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


def formated_text(list_of_text):
    list_of_text.delete(1.0, END)
    today_date = date.today()
    dir = os.path.join(config.folder_path, str(today_date))

    if not os.path.exists(dir):
        list_of_text.insert("end", "Папка с данными не найдена\n")
        return

    counter = 1
    config.image_references.clear()

    for entry in os.scandir(dir):
        if entry.is_file() and entry.name.endswith('.txt'):
            try:
                with open(entry, "r", encoding='utf-8') as file:
                    content = file.read().strip()
                list_of_text.insert("end", f"{counter}: {content}\n")

                list_of_text.insert("end", "-" * 65 + "\n")
                counter += 1
            except Exception as e:
                print(f"Ошибка: {e}")

    list_of_text.see('end')


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
    list_of_text.delete(1.0, END)
    list_of_text.configure(state="normal")

    today_date = date.today()
    dir = os.path.join(config.folder_path, str(today_date))

    if not os.path.exists(dir):
        list_of_text.insert(END, "Папка с данными не найдена\n")
        list_of_text.configure(state="disabled")
        return

    image_files = []
    for entry in os.scandir(dir):
        if entry.is_file() and entry.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            image_files.append(entry.name)

    if not image_files:
        list_of_text.insert(END, "Изображения не найдены\n")
    else:
        for i, img_name in enumerate(image_files, 1):
            list_of_text.insert(END, f"{i}. {img_name}\n")
            list_of_text.insert(END, "-" * 65 + "\n")

    list_of_text.configure(state="disabled")

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