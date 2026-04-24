import os.path
import shutil
import tkinter as tk
from tkinter import ttk
from tkinter import *
import customtkinter
import config
import filters
import monitoring_clipboard
from monitoring_clipboard import start_monitoring
import tkinter.filedialog as fd
from settings import setting
import customtkinter as ctk
import json
from datetime import datetime, timedelta
import tkinter.messagebox as mg
from datetime import datetime,date

def save_auto_delete_settings(period):
    file_path = os.path.join(config.root_folder, 'settings.json')
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                settings = json.load(f)
        else:
            settings = {}
        settings["auto_delete"] = {
            "period": period,
            "start_date": datetime.now().isoformat()}

        with open(file_path, 'w') as f:
            json.dump(settings, f, indent = 4)
        print(f"Установлено автоудаление: {period}")
        mg.showinfo("Автоудаление", f"Установлено автоудаление: {period}")
    except Exception as e:
        print(f"Ошибка сохранения настроек: {e}")


def delete_all():
    delete_path = config.folder_path
    settings_path = os.path.join(config.root_folder, 'settings.json')

    pinned_files = []
    try:
        if os.path.exists(settings_path):
            with open(settings_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                pinned_files = data.get("pinned_files", [])
    except:
        pass

    try:
        for root, dirs, files in os.walk(delete_path, topdown=False):
            for file in files:
                file_path = os.path.join(root, file)
                if file_path not in pinned_files:
                    os.remove(file_path)

            for folder in dirs:
                folder_path = os.path.join(root, folder)
                if not os.listdir(folder_path):
                    os.rmdir(folder_path)

        monitoring_clipboard.create_folder_for_days()
    except Exception as e:
        mg.showinfo("Автоудаление", f"Ошибка: {e}")

def check_auto_delete():
    file_path = os.path.join(config.root_folder, 'settings.json')
    if not os.path.exists(file_path):
        return False

    try:
        with open(file_path, 'r') as f:
            settings = json.load(f)

        auto = settings.get("auto_delete")
        if not auto:
            return False

        period = auto.get("period")
        start_date = datetime.fromisoformat(auto.get("start_date"))
        now = datetime.now()

        need_delete = False

        if period == "Сейчас":
            need_delete = True
        elif period == "Неделя":
            need_delete = now >= start_date + timedelta(weeks=1)
        elif period == "Месяц":
            need_delete = now >= start_date + timedelta(days=30)
        elif period == "Год":
            need_delete = now >= start_date + timedelta(days=365)

        if need_delete:
            delete_all()
            monitoring_clipboard.create_folder_for_days()
            update_combobox_date()
            if period == "Сейчас":
                auto["period"] = 0
            else:
                auto["start_date"] = now.isoformat()
                mg.showinfo("Автоудаление", f"Данные очищены. Новый отсчёт: {period}")

            settings["auto_delete"] = auto
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)

            selected_sort(combobox.get())
            return True

        return False
    except Exception as e:
        print(f"Ошибка проверки автоудаления: {e}")
        return False


def auto_delete_callback(period):
    save_auto_delete_settings(period)
    if period == "Сейчас":
        save_auto_delete_settings(0)
        delete_all()
        mg.showinfo("Автоудаление", "Все данные удалены")
        update_combobox_date()
        selected_sort(combobox.get())
    else: print(f"Настройки сохранены: удаление через {period.lower()}")


def stop_command():
    if config.monitoring:
        config.monitoring = False
        stop_button.configure(text="Запуск")
        print("Программа приостаовлена")
    else:
        config.monitoring = True
        stop_button.configure(text="Стоп")
        update_combobox_date()
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
        update_combobox_date()
        selected_sort("Все")

def update_combobox_date():
    try:
        new_dates = filters.date_filter()
        current_value = date_combobox.get()
        date_combobox.configure(values=new_dates)
        if current_value in new_dates:
            date_combobox.set(current_value)
        else:
            date_combobox.set("Все")
    except Exception as e:
        print(f"Ошибка обновления комбобокса: {e}")

def date_to_show():
    curr_date = date_combobox.get()
    if curr_date != "Все":
        return os.path.join(config.folder_path, date_combobox.get())

def search_content(search, base_path):
    if not base_path or not os.path.exists(base_path):
        return []
    found_notes = []
    for root, dirs, files in os.walk(base_path):
        for file_name in files:
            if file_name.endswith(".txt"):
                file_path = os.path.join(root, file_name)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if search.lower() in content.lower():
                            found_notes.append((file_path, content))
                except:
                    continue
    return found_notes


def run_search():
    found_notes = []
    app.focus_set()
    query = word_filter.get().strip()

    if not query:
        selected_sort(combobox.get())
        return
    selected_date = date_combobox.get()
    if selected_date == "Все":
        path = config.folder_path
    else:
        path = os.path.join(config.folder_path, selected_date)

    if not os.path.exists(path):
        print(f"Ошибка: Путь {path} не существует")
        return

    results = search_content(query, path)

    list_of_text.configure(state="normal")
    list_of_text.delete(1.0, "end")
    list_of_text.tag_configure("highlight", background=config.background_color)

    if not results:
        list_of_text.insert("end", f"Ничего не найдено по запросу: {query}")
    else:
        list_of_text.insert("end", f"Результаты поиска ({len(results)}):\n" + "-" * 90 + "\n\n")
        for i, (file_path, res) in enumerate(results, 1):
            start_pos = list_of_text.index("end-1c")
            filters.append_row(list_of_text, res, i, file_path)
            end_pos = list_of_text.index("end-1c")

            current_search_pos = start_pos
            while True:
                current_search_pos = list_of_text.search(query, current_search_pos, stopindex=end_pos, nocase=True)
                if not current_search_pos:
                    break
                highlight_end = f"{current_search_pos}+{len(query)}c"
                list_of_text.tag_add("highlight", current_search_pos, highlight_end)
                current_search_pos = highlight_end

def save_folder():
    file_path = os.path.join(config.root_folder, 'settings.json')
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                settings = json.load(f)
        else:
            settings = {}
        settings['folder_path'] = config.folder_path
        with open(file_path, 'w') as f:
            json.dump(settings, f)
        update_combobox_date()
    except Exception as e:
        print(f"Ошибка: {e}")

def load_folder():
    file_path = os.path.join(config.root_folder, 'settings.json')
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                settings = json.load(f)
                temp_folder = settings.get('folder_path')
                if temp_folder and os.path.exists(temp_folder):
                    config.folder_path = temp_folder
                    config.folder_to_save = os.path.dirname(temp_folder)
        else: print("Папка с файлом не найдена")
    except Exception as e:
        print(f"Ошибка {e}")

choices = {
        "Все": lambda: filters.formated_text(list_of_text, date_combobox),
        "Ссылки": lambda: filters.show_links(list_of_text, date_combobox),
        "Текст": lambda: filters.show_text(list_of_text, date_combobox),
        "Изображения": lambda: filters.show_images(list_of_text, date_combobox),
        "Закрепленные": lambda: filters.show_pinned(list_of_text, date_combobox)}

def load_color():
    file_path = os.path.join(config.root_folder, 'settings.json')
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                data = json.load(f)
                config.background_color = data.get('bg_color')
                if config.background_color and 'main_wind' in globals() and main_wind:
                    app.configure(bg=config.background_color)
                    update_button_colors(main_wind)
    except Exception as e:
        print(f"Ошибка {e}")


def selected_sort(choice):
    if choice in choices:
        list_of_text.configure(state="normal")
        list_of_text.delete(1.0, END)
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
                               dropdown_text_color = wind_object.lighten_color(-0.3), text_color= wind_object.lighten_color(-0.5)),
            date_combobox.configure(fg_color=light_color, border_color=dark_color,
                               button_color=dark_color, button_hover_color=wind_object.lighten_color(-0.5),
                               dropdown_fg_color=wind_object.lighten_color(0.2), dropdown_hover_color=light_color,
                               dropdown_text_color=wind_object.lighten_color(-0.3), text_color= wind_object.lighten_color(-0.5))
            list_of_text.configure(bg=wind_object.lighten_color(0.2),fg=wind_object.lighten_color(-0.4),insertbackground=wind_object.lighten_color(-0.4))
            name.configure(bg = config.background_color, fg = wind_object.lighten_color(-0.5))
            word_filter.configure(fg_color=light_color, placeholder_text_color =wind_object.lighten_color(-0.5),
                                  border_color=dark_color)
            find_words_btn.configure(fg_color=dark_color, hover_color= wind_object.lighten_color(-0.3)),
            data.configure(fg_color = config.background_color, text_color= wind_object.lighten_color(-0.5)),
            type_label.configure(fg_color=config.background_color, text_color= wind_object.lighten_color(-0.5))
            search_label.configure(fg_color=config.background_color),
            input_frame.configure(fg_color=config.background_color),
            type_frame.configure(fg_color=config.background_color),
            date_frame.configure(fg_color=config.background_color),
            search_frame.configure(fg_color=config.background_color)
            text_scrollbar.configure(fg_color=light_color,bg_color=light_color,
                                     button_color=dark_color,button_hover_color=wind_object.lighten_color(-0.3)
            )
            text_container.configure(fg_color=light_color,border_color=wind_object.lighten_color(-0.3),)

def setup():
    global app, list_of_text, word_filter, date_combobox, combobox, stop_button, \
        clipboard_thread, open_folder_btn, name, main_wind, find_words_btn, data, type_label, search_label, input_frame, \
        type_frame, date_frame, search_frame, text_scrollbar, text_container
    app = tk.Tk()
    app.title("Буфер обмена")
    app.geometry("650x650")
    main_wind = setting(app)
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

    combobox_frame = ctk.CTkFrame(app, fg_color="transparent")
    combobox_frame.pack(padx=10, fill='x', pady=5)

    type_frame = ctk.CTkFrame(combobox_frame, fg_color="transparent")
    type_frame.pack(side="left", padx=5)

    type_label = ctk.CTkLabel(type_frame, text="Типы данных", font=('Comic Sans MS', 13), anchor="w")
    type_label.pack(fill='x')
    combobox = ctk.CTkComboBox(type_frame, values=list(choices.keys()), command=selected_sort,
                               font=('Comic Sans MS', 15), dropdown_font=('Comic Sans MS', 13), state="readonly",
                               width=150)
    combobox.pack()
    combobox.set("Все")

    date_frame = ctk.CTkFrame(combobox_frame, fg_color="transparent")
    date_frame.pack(side="left", padx=5)

    data = ctk.CTkLabel(date_frame, text="Дата", font=('Comic Sans MS', 13), anchor="w")
    data.pack(fill='x')
    date_combobox = ctk.CTkComboBox(date_frame, values=filters.date_filter(),
                                    font=('Comic Sans MS', 15), dropdown_font=('Comic Sans MS', 13), state="readonly",
                                    width=150, command=lambda choice: selected_sort(combobox.get()))
    date_combobox.pack()

    today_date = str(date.today())
    date_combobox.set(today_date)
    if today_date in filters.date_filter():
        date_combobox.set(today_date)
    else:
        date_combobox.set("Все")

    search_frame = ctk.CTkFrame(combobox_frame, fg_color="transparent")
    search_frame.pack(side="left", padx=5)
    search_label = ctk.CTkLabel(search_frame, text="", font=('Comic Sans MS', 13))
    search_label.pack(fill='x')
    input_frame = ctk.CTkFrame(search_frame, fg_color="transparent")
    input_frame.pack()

    word_filter = ctk.CTkEntry(input_frame, width=250, height=30, placeholder_text= "Поиск",
                               font=('Comic Sans MS', 13))
    word_filter.pack(side='left', padx=(0, 5))

    find_words_btn = ctk.CTkButton(input_frame, text="🔍", height=30, width=30,
                                   font=('Comic Sans MS', 13), command=run_search)
    find_words_btn.pack()
    load_folder()


    open_folder_btn = customtkinter.CTkButton(
        master=app,
        fg_color='grey',
        text_color='black',
        text=config.folder_path if config.folder_path else "Выберите папку для сохранения",
        command=open_file,
        font=('Comic Sans MS', 15),
        hover_color='dark grey',
        corner_radius=10,
    )
    open_folder_btn.pack(pady=10, side='bottom')
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
    stop_button.pack(pady=10, side = 'bottom')

    text_container = ctk.CTkFrame(master=app,
        corner_radius=20,
        border_width=2,
        fg_color="#ffffff"
    )
    text_container.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

    list_of_text = tk.Text(
        master=text_container,
        wrap=tk.WORD,
        font=('Comic Sans MS', 11),
        state="normal",
        relief="flat",
        highlightthickness=0,
        padx=15, pady=10)

    text_scrollbar = ctk.CTkScrollbar(master=text_container, command=list_of_text.yview)
    list_of_text.configure(yscrollcommand=text_scrollbar.set)
    text_scrollbar.pack(side="right", fill="y", padx=(0, 9), pady=5)
    list_of_text.pack(side="left", fill="both", expand=True, padx=9, pady=5)


    def disable_editing(event):
        if event.state & 0x4 and event.keysym.lower() == 'c':
            copy_text()
            return "break"
        if event.keysym not in ('c', 'C', 'Insert', 'Control_L', 'Control_R'):
            return "break"

    def show_context_menu(event):
        context_menu.tk_popup(event.x_root, event.y_root)

    def copy_text():
        try:
            selected = list_of_text.selection_get()
            app.clipboard_clear()
            app.clipboard_append(selected)
        except:
            pass


    context_menu = tk.Menu(app, tearoff=0)
    context_menu.add_command(label="Копировать", command=copy_text)

    list_of_text.bind("<Key>", disable_editing)
    list_of_text.bind("<Button-3>", show_context_menu)


    check_auto_delete()

    main_menu = Menu()
    file_menu = Menu()
    settings_menu = Menu()

    file_menu.add_command(label = "Цветовая тема", command= main_wind.color_choose)
    settings_menu.add_command(label="Удалить сейчас", command=lambda: auto_delete_callback("Сейчас"))
    settings_menu.add_separator()
    settings_menu.add_command(label="Неделя", command=lambda: auto_delete_callback("Неделя"))
    settings_menu.add_command(label="Месяц", command=lambda: auto_delete_callback("Месяц"))
    settings_menu.add_command(label="Год", command=lambda: auto_delete_callback("Год"))
    file_menu.add_cascade(label="Настройки автоудаления", menu = settings_menu)

    file_menu.add_separator()
    file_menu.add_command(label="Выход", command= main_wind.quit_app)
    main_menu.add_cascade(label = "Настройки", menu=file_menu)
    app.config(menu= main_menu)

    if config.background_color:
        load_color()

    selected_sort("Все")
    clipboard_thread = start_monitoring(app, selected_sort, combobox)
    app.protocol("WM_DELETE_WINDOW", close_command)

def run_app():
    setup()
    load_folder()
    filters.create_json()
    monitoring_clipboard.create_folder_for_days()
    app.mainloop()