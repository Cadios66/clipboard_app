import json
from tkinter import END
import tkinter as tk
from PIL import Image, ImageTk
import config
import os, io
from datetime import date, datetime
from settings import setting
import win32clipboard
from PIL import Image
import io


def date_to_show(date_combobox, selection=None):
    selected_date = selection if selection else date_combobox.get()
    if selected_date == "Все":
        return config.folder_path
    path = os.path.join(config.folder_path, selected_date)
    return path if os.path.exists(path) else None



def copy_to_clipboard(text, list_of_text):
    list_of_text.clipboard_clear()
    config.ignore_next_clipboard = True
    list_of_text.clipboard_append(text)


def copy_image_to_clipboard(img_path):
    try:
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
        print(e)


def wrap_text(text, width=70):
    result = []
    for i in range(0, len(text), width):
        chunk = text[i: i + width]
        result.append(chunk)
    return '\n'.join(result)


def is_file_pinned(file_path):
    settings_path = config.settings_path
    if not os.path.exists(settings_path): return False
    try:
        with open(settings_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return file_path in data.get("pinned_files", [])
    except:
        return False


def toggle_pin(file_path, btn):
    settings_path = config.settings_path
    try:
        with open(settings_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if "pinned_files" not in data:
            data["pinned_files"] = []
        if file_path in data["pinned_files"]:
            data["pinned_files"].remove(file_path)
            btn.configure(text="☆", fg="black")
        else:
            data["pinned_files"].append(file_path)
            btn.configure(text="★", fg="#f1c40f")
        with open(settings_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(e)


def append_row(list_of_text, content, counter, file_path):
    btn_bg = setting.lighten_color(0.2)
    formated = wrap_text(content)
    is_pinned = is_file_pinned(file_path)
    pin_symbol = "★" if is_pinned else "☆"
    pin_color = "#f1c40f" if is_pinned else "black"

    list_of_text.insert("end", f"{counter}: {formated}")
    list_of_text.insert("end", "\t")

    copy_btn = tk.Button(
        list_of_text, text="📋", bg=btn_bg, fg="black", bd=0, highlightthickness=0,
        relief="groove", font=("Arial", 14), cursor="hand2", padx=5,
        highlightbackground=btn_bg, activebackground=btn_bg
    )
    copy_btn.configure(command=lambda c=content: copy_to_clipboard(c, list_of_text))

    pin_btn = tk.Button(
        list_of_text, text=pin_symbol, bg=btn_bg, fg=pin_color, bd=0, highlightthickness=0,
        relief="groove", font=("Arial", 13), cursor="hand2", padx=5,
        highlightbackground=btn_bg, activebackground=btn_bg
    )
    pin_btn.configure(command=lambda: toggle_pin(file_path, pin_btn))

    list_of_text.window_create("end", window=pin_btn, align="center")
    list_of_text.insert("end", " ")
    list_of_text.window_create("end", window=copy_btn, align="center")
    list_of_text.insert("end", "\n" + "_" * 60 + "\n\n")


def append_image_row(list_of_text, img_name, tk_img, counter, img_path):
    btn_bg = setting.lighten_color(0.2)
    is_pinned = is_file_pinned(img_path)
    pin_symbol = "★" if is_pinned else "☆"
    pin_color = "#f1c40f" if is_pinned else "black"

    list_of_text.insert("end", f"{counter}: {img_name}\n")
    list_of_text.image_create("end", image=tk_img)
    list_of_text.insert("end", "\t")

    copy_btn = tk.Button(
        list_of_text, text="📋", bg=btn_bg, fg="black", bd=0, highlightthickness=0,
        relief="groove", font=("Arial", 14), cursor="hand2", padx=5,
        highlightbackground=btn_bg, activebackground=btn_bg,
        command=lambda p=img_path: copy_image_to_clipboard(p)
    )

    pin_btn = tk.Button(
        list_of_text, text=pin_symbol, bg=btn_bg, fg=pin_color, bd=0, highlightthickness=0,
        relief="groove", font=("Arial", 13), cursor="hand2", padx=5,
        highlightbackground=btn_bg, activebackground=btn_bg
    )
    pin_btn.configure(command=lambda: toggle_pin(img_path, pin_btn))

    list_of_text.window_create("end", window=pin_btn, align="center")
    list_of_text.insert("end", " ")
    list_of_text.window_create("end", window=copy_btn, align="center")
    list_of_text.insert("end", "\n" + "-" * 65 + "\n\n")


def formated_text(list_of_text, date_combobox):
    selected_date = date_combobox.get()
    list_of_text.configure(state="normal")

    for child in list_of_text.winfo_children():
        child.destroy()
    list_of_text.delete(1.0, "end")
    config.image_references.clear()

    raw_width = list_of_text.winfo_width()
    if raw_width > 100:
        list_of_text.configure(tabs=(raw_width - 90, tk.CENTER, raw_width - 35, tk.CENTER))

    base_path = config.folder_path if selected_date == "Все" else date_to_show(date_combobox)
    if not base_path or not os.path.exists(base_path):
        list_of_text.configure(state="disabled")
        return

    all_files = []
    images = ('.png', '.jpg', '.jpeg', '.gif', '.bmp')

    if selected_date == "Все":
        for root, dirs, files in os.walk(base_path):
            for f in files:
                all_files.append(os.path.join(root, f))
    else:
        for f in os.listdir(base_path):
            all_files.append(os.path.join(base_path, f))

    all_files.sort(key=lambda x: os.path.getctime(x))

    counter = 1
    for file_path in all_files:
        if file_path.endswith(".txt"):
            try:
                with open(file_path, "r", encoding='utf-8') as f:
                    content = f.read().strip()
                append_row(list_of_text, content, counter, file_path)
                counter += 1
            except:
                continue
        elif file_path.lower().endswith(images):
            try:
                pil_img = Image.open(file_path)
                pil_img.thumbnail((350, 350))
                tk_img = ImageTk.PhotoImage(pil_img)
                config.image_references.append(tk_img)
                append_image_row(list_of_text, os.path.basename(file_path), tk_img, counter, file_path)
                counter += 1
            except:
                continue

    list_of_text.configure(state="disabled")
    list_of_text.see("end")


def show_links(list_of_text, date_combobox):
    selected_date = date_combobox.get()
    list_of_text.configure(state="normal")
    list_of_text.delete(1.0, "end")
    raw_width = list_of_text.winfo_width()
    if raw_width > 100:
        list_of_text.configure(tabs=(raw_width - 90, tk.CENTER, raw_width - 35, tk.CENTER))

    base_path = config.folder_path if selected_date == "Все" else date_to_show(date_combobox)
    if not base_path or not os.path.exists(base_path):
        list_of_text.configure(state="disabled")
        return

    all_files = []
    if selected_date == "Все":
        for root, dirs, files in os.walk(base_path):
            for f in files:
                if f.endswith(".txt"): all_files.append(os.path.join(root, f))
    else:
        for f in os.listdir(base_path):
            if f.endswith(".txt"): all_files.append(os.path.join(base_path, f))

    all_files.sort(key=lambda x: os.path.getctime(x))

    counter = 1
    for file_path in all_files:
        try:
            with open(file_path, "r", encoding='utf-8') as f:
                content = f.read().strip()
                if content.startswith(('http://', 'https://', 'www.')):
                    append_row(list_of_text, content, counter, file_path)
                    counter += 1
        except:
            continue

    list_of_text.configure(state="disabled")
    list_of_text.see("end")


def show_text(list_of_text, date_combobox):
    directory = date_to_show(date_combobox)
    list_of_text.configure(state="normal")
    list_of_text.delete(1.0, END)
    if not directory or not os.path.exists(directory): return
    raw_width = list_of_text.winfo_width()
    if raw_width > 100:
        list_of_text.configure(tabs=(raw_width - 90, tk.CENTER, raw_width - 35, tk.CENTER))
    counter = 1
    for entry in os.scandir(directory):
        if entry.is_file() and entry.name.endswith(".txt"):
            try:
                with open(entry.path, "r", encoding='utf-8') as file:
                    content = file.read().strip()
                if not content.startswith(('http://', 'https://', 'www.')):
                    append_row(list_of_text, content, counter, entry.path)
                    counter += 1
            except:
                continue
    list_of_text.configure(state="disabled")


def show_images(list_of_text, date_combobox):
    list_of_text.configure(state="normal")
    list_of_text.delete(1.0, "end")
    config.image_references.clear()
    raw_width = list_of_text.winfo_width()
    if raw_width > 100:
        list_of_text.configure(tabs=(raw_width - 90, tk.CENTER, raw_width - 35, tk.CENTER))
    selected_date = date_combobox.get()
    counter = 1
    image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp')
    files_to_process = []
    if selected_date == "Все":
        base_path = config.folder_path
        if base_path and os.path.exists(base_path):
            for root, dirs, files in os.walk(base_path):
                for file in files:
                    if file.lower().endswith(image_extensions):
                        files_to_process.append(os.path.join(root, file))
    else:
        directory = date_to_show(date_combobox)
        if directory and os.path.exists(directory):
            for entry in os.scandir(directory):
                if entry.is_file() and entry.name.lower().endswith(image_extensions):
                    files_to_process.append(entry.path)
    for img_path in files_to_process:
        try:
            pil_img = Image.open(img_path)
            pil_img.thumbnail((350, 350))
            tk_img = ImageTk.PhotoImage(pil_img)
            config.image_references.append(tk_img)
            append_image_row(list_of_text, os.path.basename(img_path), tk_img, counter, img_path)
            counter += 1
        except:
            continue
    list_of_text.configure(state="disabled")


def show_pinned(list_of_text, date_combobox):
    list_of_text.configure(state="normal")
    list_of_text.delete(1.0, "end")
    config.image_references.clear()
    settings_path = config.settings_path
    try:
        with open(settings_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            pinned_files = data.get("pinned_files", [])
    except:
        return
    if not pinned_files:
        list_of_text.insert("end", "Список избранного пуст\n")
        list_of_text.configure(state="disabled")
        return
    counter = 1
    image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp')
    for file_path in pinned_files:
        if not os.path.exists(file_path): continue
        if file_path.lower().endswith(image_extensions):
            try:
                pil_img = Image.open(file_path)
                pil_img.thumbnail((350, 350))
                tk_img = ImageTk.PhotoImage(pil_img)
                config.image_references.append(tk_img)
                append_image_row(list_of_text, os.path.basename(file_path), tk_img, counter, file_path)
                counter += 1
            except:
                continue
        elif file_path.endswith(".txt"):
            try:
                with open(file_path, "r", encoding='utf-8') as f:
                    content = f.read().strip()
                append_row(list_of_text, content, counter, file_path)
                counter += 1
            except:
                continue
    list_of_text.configure(state="disabled")


def date_filter():
    paths = config.folder_path
    if not paths and os.path.exists(config.settings_path):
        try:
            with open(config.settings_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                paths = data.get("folder_path")
        except:
            pass
    if paths and os.path.exists(paths):
        try:
            dates = [d for d in os.listdir(paths) if os.path.isdir(os.path.join(paths, d))]
            dates.sort(reverse=True)
            dates.append('Все')
            return dates
        except:
            pass
    return ["Все"]


def create_json():
    path = config.settings_path
    if not os.path.exists(path):
        data = {
            'auto_delete': {"period": 0, "start_date": datetime.now().isoformat()},
            'bg_color': '#ffffff',
            'folder_path': None,
            'pinned_files': []
        }
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)