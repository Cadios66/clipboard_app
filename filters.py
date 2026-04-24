import json
from tkinter import END
import tkinter as tk
from PIL import Image, ImageTk
import config
from datetime import date
from pathlib import Path
import os, io
from datetime import date, datetime
from settings import setting
import win32clipboard

def date_to_show(date_combobox, selection = None):
    selected_date = selection if selection else date_combobox.get()
    if selected_date == "Все":
        return config.folder_path
    path = os.path.join(config.folder_path, selected_date)
    return path if os.path.exists(path) else None
def pin_activate_btn(btn):
    if btn.cget("text") == "☆":
        btn.configure(text="★", fg="#f1c40f")
    else:  btn.configure(text = "☆", fg = 'black')
def copy_to_clipboard(text, list_of_text):
    list_of_text.clipboard_clear()
    config.ignore_next_clipboard = True
    list_of_text.clipboard_append(text)

def copy_image_to_clipboard(img_path):
    try:
        from PIL import Image
        import io
        image = Image.open(img_path)
        output = io.BytesIO()
        image.convert("RGB").save(output, "BMP")
        data = output.getvalue()[14:]
        output.close()
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
        win32clipboard.CloseClipboard()
    except Exception as e:
        return print(e)

def wrap_text(text, width=70):
    result = []
    for i in range(0, len(text), width):
        chunk = text[i: i + width]
        result.append(chunk)
    return '\n'.join(result)
def append_row(list_of_text, content, counter):
    btn_bg = setting.lighten_color(0.2)
    formated = wrap_text(content)
    list_of_text.insert("end", f"{counter}: {formated}")
    list_of_text.insert("end", "\t")

    copy_btn = tk.Button(
        list_of_text,
        text="📋",
        bg=btn_bg,
        fg="black",
        bd=0,
        highlightthickness=0,
        relief="groove",
        font=("Arial", 14),
        cursor="hand2",
        padx=5,
        highlightbackground=btn_bg,
        activebackground=btn_bg
    )
    copy_btn.configure(command=lambda c=content: copy_to_clipboard(c, list_of_text))
    pin_btn = tk.Button(
        list_of_text,
        text="☆",
        bg=btn_bg,
        fg="black",
        bd=0,
        highlightthickness=0,
        relief="groove",
        font=("Arial", 13),
        cursor="hand2",
        padx=5,
        highlightbackground=btn_bg,
        activebackground=btn_bg
    )
    pin_btn.configure(command=lambda b=pin_btn: pin_activate_btn(b))
    list_of_text.window_create("end", window=pin_btn, align="center")
    list_of_text.insert("end", " ")
    list_of_text.window_create("end", window=copy_btn, align="center")
    list_of_text.insert("end", "\n" + "_" * 60 + "\n\n")


def append_image_row(list_of_text, img_name, tk_img, counter, img_path):
    btn_bg = setting.lighten_color(0.2)
    list_of_text.insert("end", f"{counter}: {img_name}\n")

    list_of_text.image_create("end", image=tk_img)
    list_of_text.insert("end", "\t")

    copy_btn = tk.Button(
        list_of_text,
        text="📋",
        bg=btn_bg,
        fg="black",
        bd=0,
        highlightthickness=0,
        relief="groove",
        font=("Arial", 14),
        cursor="hand2",
        padx=5,
        highlightbackground=btn_bg,
        activebackground=btn_bg,
        command=lambda p=img_path: copy_image_to_clipboard(p))

    pin_btn = tk.Button(
        list_of_text,
        text="☆",
        bg=btn_bg,
        fg="black",
        bd=0,
        highlightthickness=0,
        relief="groove",
        font=("Arial", 13),
        cursor="hand2",
        padx=5,
        highlightbackground=btn_bg,
        activebackground=btn_bg
    )
    pin_btn.configure(command=lambda b=pin_btn: pin_activate_btn(b))
    list_of_text.window_create("end", window=pin_btn, align="center")
    list_of_text.window_create("end", window=copy_btn, align="center")
    list_of_text.insert("end", "\n" + "-" * 65 + "\n\n")


def formated_text(list_of_text, date_combobox):
    selected_date = date_combobox.get()
    list_of_text.configure(state="normal")

    for child in list_of_text.winfo_children():
        child.destroy()
    list_of_text.delete(1.0, "end")

    raw_width = list_of_text.winfo_width()
    if raw_width > 100:
        list_of_text.configure(tabs=(raw_width - 70, tk.CENTER, raw_width - 35, tk.CENTER))

    counter = 1

    if selected_date == "Все":
        base_path = config.folder_path
        if not os.path.exists(base_path):
            list_of_text.insert("end", "Базовая папка не найдена\n")
            return

        for root, dirs, files in os.walk(base_path):
            for file in files:
                if file.endswith(".txt"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding='utf-8') as f:
                            content = f.read().strip()
                        append_row(list_of_text, content, counter)
                        counter += 1
                    except:
                        continue
    else:
        directory = date_to_show(date_combobox)
        if directory and os.path.exists(directory):
            for entry in os.scandir(directory):
                if entry.is_file() and entry.name.endswith('.txt'):
                    try:
                        with open(entry.path, "r", encoding='utf-8') as file:
                            content = file.read().strip()
                        append_row(list_of_text, content, counter)
                        counter += 1
                    except:
                        continue
        else:
            list_of_text.insert("end", "Папка за эту дату не найдена\n")

    list_of_text.configure(state="disabled")
    list_of_text.see('1.0')

    list_of_text.configure(state="disabled")
    list_of_text.see('end')


def show_links(list_of_text, date_combobox):
    selected_date = date_combobox.get()
    directory = date_to_show(date_combobox)
    list_of_text.delete(1.0, "end")
    raw_width = list_of_text.winfo_width()
    if raw_width > 100:
        list_of_text.configure(tabs=(raw_width - 70, tk.CENTER, raw_width - 35, tk.CENTER))
    counter = 1

    if not os.path.exists(directory):
        list_of_text.insert("end", "Папка с данными не найдена\n")
        return

    if selected_date == "Все":
        base_path = config.folder_path
        if not os.path.exists(base_path):
            list_of_text.insert("end", "Базовая папка не найдена\n")
            return

        for root, dirs, files in os.walk(base_path):
            for file in files:
                if file.endswith(".txt"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding='utf-8') as f:
                            content = f.read().strip()
                            if content.startswith(('http://', 'https://', 'www.')):
                                append_row(list_of_text, content, counter)
                                counter += 1
                    except:
                        continue
    else:
        directory = date_to_show(date_combobox)
        if directory and os.path.exists(directory):
            for entry in os.scandir(directory):
                if entry.is_file() and entry.name.endswith('.txt'):
                    try:
                        with open(entry.path, "r", encoding='utf-8') as file:
                            content = file.read().strip()
                            if content.startswith(('http://', 'https://', 'www.')):
                                append_row(list_of_text, content, counter)
                                counter += 1
                    except:
                        continue
        else:
            list_of_text.insert("end", "Папка за эту дату не найдена\n")

    list_of_text.see("end")


def show_text(list_of_text, date_combobox):
    directory = date_to_show(date_combobox)
    list_of_text.delete(1.0, END)
    raw_width = list_of_text.winfo_width()
    if raw_width > 100:
        list_of_text.configure(tabs=(raw_width - 70, tk.CENTER, raw_width - 35, tk.CENTER))
    counter = 1

    for entry in os.scandir(directory):
        if entry.is_file():
            type_of_file = Path(entry)
            if type_of_file.suffix == ".txt":
                with open(entry, "r", encoding='utf-8') as file:
                    content = file.read()
                append_row(list_of_text, content, counter)
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

    image_files = [f for f in os.listdir(directory) if
                   f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]

    if not image_files:
        list_of_text.insert(END, "Изображения не найдены\n")
    else:
        raw_width = list_of_text.winfo_width()
        tab_pos = raw_width - 40 if raw_width > 10 else 500
        list_of_text.configure(tabs=(tab_pos, tk.RIGHT))

        for i, img_name in enumerate(image_files, 1):
            img_path = os.path.join(directory, img_name)
            try:

                pil_img = Image.open(img_path)
                max_size = (350, 350)
                pil_img.thumbnail(max_size)

                tk_img = ImageTk.PhotoImage(pil_img)
                config.image_references.append(tk_img)
                append_image_row(list_of_text, img_name, tk_img, i, img_path)
            except Exception as e:
                print(f"Ошибка загрузки {img_name}: {e}")

    list_of_text.see("end")

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