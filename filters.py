import json
from tkinter import END
import tkinter as tk
from PIL import Image, ImageTk
import config
from datetime import date
from pathlib import Path
import os, io
import customtkinter as ctk


def formated_text(list_of_text):
    list_of_text.configure(state="normal")
    list_of_text.delete(1.0, END)

    today_date = date.today()
    dir = os.path.join(config.folder_path, (str(today_date)))

    if not os.path.exists(dir):
        list_of_text.insert(END, "Папка с данными не найдена\n")
        list_of_text.configure(state="disabled")
        return
    counter = 1
    config.image_references.clear()

    list_of_text.configure(state="normal")
    list_of_text.delete(1.0, END)
    counter = 1

    for entry in os.scandir(dir):
        if entry.is_file():
            file_path = Path(entry)
            file_extension = file_path .suffix.lower()
            if file_extension == ".txt":
                with open(entry, "r") as file:
                    content = file.read()
                list_of_text.insert(END, f"{counter}: {content}\n")
                list_of_text.insert(END, "-" * 65 + "\n")

        list_of_text.see("end")
        list_of_text.configure(state="disabled")


def show_links(list_of_text):
    today_date = date.today()
    dir = os.path.join(config.folder_path, (str(today_date)))
    list_of_text.configure(state="normal")
    list_of_text.delete(1.0, END)
    counter = 1

    for entry in os.scandir(dir):
        if entry.is_file():
            type_of_file = Path(entry)
            if type_of_file.suffix == ".txt":
                with open(entry, "r") as file:
                    content = file.read()
                    if content.startswith('http') or content.startswith('https'):
                        list_of_text.insert(END, f"{counter}: {content}\n")
                        list_of_text.insert(END, "-" * 65 + "\n")
                        counter += 1

    list_of_text.see(END)
    list_of_text.configure(state="disabled")


def show_text(list_of_text):
    today_date = date.today()
    dir = os.path.join(config.folder_path, (str(today_date)))
    list_of_text.configure(state="normal")
    list_of_text.delete(1.0, END)
    counter = 1

    for entry in os.scandir(dir):
        if entry.is_file():
            type_of_file = Path(entry)
            if type_of_file.suffix == ".txt":
                with open(entry, "r") as file:
                    content = file.read()
                list_of_text.insert(END, f"{counter}: {content}\n")
                list_of_text.insert(END, "-" * 65 + "\n")
            counter += 1

    list_of_text.see(END)
    list_of_text.configure(state="disabled")


def show_images(list_of_text):
    list_of_text.configure(state="normal")
    list_of_text.delete(1.0, END)
    counter = 1

    config.image_references.clear()

    for i, item in enumerate(config.copied_things):
        if isinstance(item, Image.Image):

            try:
                list_of_text.insert(END, f"{counter}. Изображение {item.width}x{item.height}\n")

                display_img = item.copy()
                max_width = 300

                if display_img.width > max_width:
                    ratio = max_width / display_img.width
                    new_height = int(display_img.height * ratio)
                    display_img = display_img.resize((max_width, new_height), Image.Resampling.LANCZOS)

                photo = ImageTk.PhotoImage(display_img)
                config.image_references.append(photo)


                counter += 1
            except Exception as e:
                list_of_text.insert(END, f"{counter}. Не удалось загрузить изображение\n")
                list_of_text.insert(END, "-" * 65 + "\n")
                counter += 1
    if counter == 1:
        list_of_text.insert(END, "Нет изображений в истории\n")
    list_of_text.see(END)
    list_of_text.configure(state="disabled")

def date_filter():
    file_path = os.path.join(config.root_folder, 'settings.json')
    with open(file_path, 'r') as f:
        data = json.load(f)
        paths = data.get("folder_path")
    dates = os.listdir(paths)
    dates.append('Все')
    return dates


print(date_filter())