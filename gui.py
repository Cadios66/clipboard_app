import os.path
import tkinter as tk
from tkinter import ttk
from tkinter import *
import customtkinter
import config
from monitoring_clipboard import start_monitoring
from filters import formated_text, show_links, show_text, show_images
import tkinter.filedialog as fd
from settings import setting
import customtkinter as ctk

def stop_command():
    if config.monitoring:
        config.monitoring = False
        stop_button.configure(text="Запуск")
        print("Программа приостаовлена")
    else:
        config.monitoring = True
        stop_button.configure(text="Стоп")
        print("Программа запущена")

def close_command():
    config.stop = True
    app.destroy()

def open_file():
    selected_folder = fd.askdirectory(title="Выберите папку для сохранения", initialdir="/")
    if selected_folder:
        config.folder_to_save = selected_folder
        config.folder_path = os.path.join(selected_folder, "copytext_app")
        open_folder_btn.configure(text=str(config.folder_path))
        save_folder()

def save_folder():
    file_path = os.path.join(config.root_folder, 'folder_choice.txt')
    try:
        with open(file_path, 'w') as file:
            file.write(config.folder_path)
    except Exception as e:
        print(f"Ошибка: {e}")
def load_folder():
    file_path = os.path.join(config.root_folder, 'folder_choice.txt')
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                temp_folder = file.read()
                if temp_folder and os.path.exists(temp_folder):
                    config.folder_path = temp_folder
                    config.folder_to_save = os.path.dirname(temp_folder)
        else: print("Папка с файлом не найдена")
    except Exception as e:
        print(f"Ошибка {e}")

choices = {
        "Все": lambda: formated_text(list_of_text), "Ссылки": lambda: show_links(list_of_text),
        "Текст": lambda: show_text(list_of_text),"Изображения": lambda: show_images(list_of_text)}

def load_color():
    file_path = os.path.join(config.root_folder, 'color_theme_choice.txt')
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                temp_color = file.read()
                if temp_color:
                    config.background_color = temp_color
                    app.configure(bg=config.background_color)
                    update_button_colors(main_wind)
                    print(config.background_color)
        else:
            print("Папка с файлом не найдена")
    except Exception as e:
        print(f"Ошибка {e}")


def selected_sort(choice):
    if choice in choices:
        choices[choice]()

def update_button_colors(wind_object):
    if config.background_color and wind_object:
        light_color = wind_object.lighten_color(0.2)
        dark_color = wind_object.lighten_color(-0.2)
        if stop_button:
            stop_button.configure(fg_color=dark_color,
                                  hover_color = wind_object.lighten_color(-0.3), text_color=wind_object.lighten_color(-0.5))
            open_folder_btn.configure(fg_color=dark_color,
                                      hover_color= wind_object.lighten_color(-0.3), text_color= wind_object.lighten_color(-0.5))
            combobox.configure(fg_color=light_color, border_color = dark_color,
                               button_color = dark_color, button_hover_color = wind_object.lighten_color(-0.3),
                               dropdown_fg_color = wind_object.lighten_color(0.2), dropdown_hover_color = light_color,
                               dropdown_text_color = wind_object.lighten_color(-0.3))
            list_of_text.configure(fg_color = wind_object.lighten_color(0.2), border_color=dark_color,
            text_color = wind_object.lighten_color(-0.4))
            name.configure(bg = config.background_color, fg = wind_object.lighten_color(-0.3))
def setup():
    global app, list_of_text, combobox, stop_button, clipboard_thread, open_folder_btn, name, main_wind
    app = tk.Tk()
    app.title("Копировальщик текста")
    app.geometry("650x650")
    load_color()

    app.update_idletasks()
    s = app.geometry()
    s = s.split('+')
    s = s[0].split('x')
    width_root = int(s[0])
    height_root = int(s[1])
    w = app.winfo_screenwidth()
    h = app.winfo_screenheight()
    app.geometry(f'+{w // 2 - width_root // 2}+{h // 2 - height_root // 2}')

    app.resizable(False, False)
    name = tk.Label(app, text = "Это программа для сохранения ваших скопированных данных",
             font = ('Comic Sans MS', 12), fg = 'black')
    name.pack()
    list_of_text = customtkinter.CTkTextbox(
        master=app,
        width=80,
        corner_radius=30,
        height=15,
        wrap=tk.WORD,
        font=('Comic Sans MS', 15),
        state="disabled",
        border_width=2,
        fg_color='white'
    )
    list_of_text.pack(pady=10, padx=10, fill = tk.BOTH, expand=True)

    combobox = ctk.CTkComboBox(app, values = list(choices.keys()),command=selected_sort,
                               font = ('Comic Sans MS', 15), dropdown_font = ('Comic Sans MS', 13))
    combobox.pack(pady=20)
    combobox.set("Все")

    stop_button = customtkinter.CTkButton(
        master=app,
        text="Стоп",
        command=stop_command,
        width=120,
        height=35,
        fg_color='grey',
        corner_radius=10,
        font=('Comic Sans MS', 18),
        border_color='black',
        hover_color='dark grey',
        text_color='black'
    )
    stop_button.pack(pady=10)
    load_folder()

    main_wind = setting(app)


    open_folder_btn = customtkinter.CTkButton(
        master=app,
        fg_color='grey',
        text_color='black',
        text=config.folder_path if config.folder_path else "Выберите папку для сохранения",
        command=open_file,
        font=('Comic Sans MS', 15),
        hover_color = 'dark grey',
        corner_radius = 10,
    )
    open_folder_btn.pack(pady=10)


    main_menu = Menu()
    file_menu = Menu()
    file_menu.add_command(label = "Color theme", command= main_wind.color_choose)
    file_menu.add_command(label="Delete all")
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command= main_wind.quit_app)
    main_menu.add_cascade(label = "Settings", menu=file_menu)
    app.config(menu= main_menu)

    if config.background_color:
        load_color()

    clipboard_thread = start_monitoring(app, selected_sort, combobox)
    app.protocol("WM_DELETE_WINDOW", close_command)

def run_app():
    setup()
    app.mainloop()