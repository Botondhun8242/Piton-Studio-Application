"""
ClickWave v1.0.0 - Professional Auto Clicker
Created by Piton Studio
BLACK & WHITE ONLY - NO BLUE/GRAY AUTO COLORS

⚡ ULTRA FAST EDITION ⚡
Modified for 100+ CPS capability:
- Minimum interval: 0ms (was 1ms)
- Precision timing with time.perf_counter()
- Compensated click execution time
- pyautogui.PAUSE = 0 for no delay
- Now capable of 100+ CPS with 0ms interval!
"""

import customtkinter as ctk
import pyautogui
import keyboard
import threading
import time
import random
import subprocess
import platform
from typing import Optional
from collections import deque

if platform.system().lower() == 'windows':
    CREATE_NO_WINDOW = 0x08000000
    subprocess.CREATE_NO_WINDOW = CREATE_NO_WINDOW

pyautogui.FAILSAFE = True
# ULTRA FAST MODE - Remove pause delay
pyautogui.PAUSE = 0  # No pause between actions for 100+ CPS

T = {
    "HU": {"next": "EN", "creator": "Készítette: Piton Studio", "time_interval": "Időintervallum", "fixed_interval": "Fix intervallum", "random_interval": "Véletlen intervallum", "click_options": "Kattintás beállítások", "button": "Gomb", "left": "Bal", "right": "Jobb", "middle": "Középső", "type": "Típus", "single": "Egyszeres", "double": "Dupla", "triple": "Tripla", "repeat": "Ismétlés", "until_stopped": "Leállításig", "fixed_count": "Fix szám", "times": "Alkalom", "click_position": "Kattintás pozíció", "current_location": "Aktuális pozíció", "fixed_position": "Fix pozíció", "get": "Lekér", "start": "INDÍT", "stop": "ÁLLJ", "change_hotkey": "Gyorsbillentyű módosítása", "settings": "Beállítások", "always_on_top": "Mindig felül", "close": "Bezár", "enter_hotkey": "Új gyorsbillentyű:", "sec": "mp"},
    "EN": {"next": "RU", "creator": "Created by Piton Studio", "time_interval": "Time Interval", "fixed_interval": "Fixed Interval", "random_interval": "Random Interval", "click_options": "Click Options", "button": "Button", "left": "Left", "right": "Right", "middle": "Middle", "type": "Type", "single": "Single", "double": "Double", "triple": "Triple", "repeat": "Repeat", "until_stopped": "Until Stopped", "fixed_count": "Fixed Count", "times": "Times", "click_position": "Click Position", "current_location": "Current Location", "fixed_position": "Fixed Position", "get": "Get", "start": "START", "stop": "STOP", "change_hotkey": "Change Hotkey", "settings": "Settings", "always_on_top": "Always on top", "close": "Close", "enter_hotkey": "Enter new hotkey:", "sec": "sec"},
    "RU": {"next": "DE", "creator": "Создано: Piton Studio", "time_interval": "Интервал времени", "fixed_interval": "Фиксированный интервал", "random_interval": "Случайный интервал", "click_options": "Настройки клика", "button": "Кнопка", "left": "Левая", "right": "Правая", "middle": "Средняя", "type": "Тип", "single": "Одиночный", "double": "Двойной", "triple": "Тройной", "repeat": "Повтор", "until_stopped": "До остановки", "fixed_count": "Фиксированное число", "times": "Раз", "click_position": "Позиция клика", "current_location": "Текущая позиция", "fixed_position": "Фиксированная позиция", "get": "Получить", "start": "СТАРТ", "stop": "СТОП", "change_hotkey": "Изменить горячую клавишу", "settings": "Настройки", "always_on_top": "Всегда сверху", "close": "Закрыть", "enter_hotkey": "Введите новую клавишу:", "sec": "сек"},
    "DE": {"next": "FR", "creator": "Erstellt von: Piton Studio", "time_interval": "Zeitintervall", "fixed_interval": "Festes Intervall", "random_interval": "Zufälliges Intervall", "click_options": "Klick-Optionen", "button": "Taste", "left": "Links", "right": "Rechts", "middle": "Mitte", "type": "Typ", "single": "Einfach", "double": "Doppelt", "triple": "Dreifach", "repeat": "Wiederholen", "until_stopped": "Bis gestoppt", "fixed_count": "Feste Anzahl", "times": "Mal", "click_position": "Klick-Position", "current_location": "Aktuelle Position", "fixed_position": "Feste Position", "get": "Abrufen", "start": "START", "stop": "STOPP", "change_hotkey": "Tastenkombination ändern", "settings": "Einstellungen", "always_on_top": "Immer im Vordergrund", "close": "Schließen", "enter_hotkey": "Neue Tastenkombination eingeben:", "sec": "Sek"},
    "FR": {"next": "HU", "creator": "Créé par: Piton Studio", "time_interval": "Intervalle de temps", "fixed_interval": "Intervalle fixe", "random_interval": "Intervalle aléatoire", "click_options": "Options de clic", "button": "Bouton", "left": "Gauche", "right": "Droit", "middle": "Milieu", "type": "Type", "single": "Simple", "double": "Double", "triple": "Triple", "repeat": "Répéter", "until_stopped": "Jusqu'à l'arrêt", "fixed_count": "Nombre fixe", "times": "Fois", "click_position": "Position du clic", "current_location": "Position actuelle", "fixed_position": "Position fixe", "get": "Obtenir", "start": "DÉMARRER", "stop": "ARRÊTER", "change_hotkey": "Changer le raccourci", "settings": "Paramètres", "always_on_top": "Toujours au premier plan", "close": "Fermer", "enter_hotkey": "Entrer nouveau raccourci:", "sec": "sec"}
}


class SegmentedControl(ctk.CTkFrame):
    """EXACT ORIGINAL COLORS - B&W only"""
    def __init__(self, parent, values, command=None):
        super().__init__(parent, 
            fg_color=("#f5f5f5", "#0a0a0a"),  # Light: light gray, Dark: BLACK
            corner_radius=8, border_width=1, 
            border_color=("#cccccc", "#333333"))
        
        self.values = values
        self.command = command
        self.buttons = []
        self.selected = None
        
        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=3, pady=3)
        
        for value in values:
            btn = ctk.CTkButton(inner, text=value, font=("Arial", 12),
                fg_color="transparent", 
                text_color=("#666666", "#999999"),  # Light: dark gray, Dark: light gray
                hover_color=("#e0e0e0", "#1a1a1a"),
                corner_radius=5, height=28, border_width=0,
                command=lambda v=value: self.select(v))
            btn.pack(side="left", fill="both", expand=True, padx=2)
            self.buttons.append(btn)
            btn.bind("<Enter>", lambda e, b=btn: self.on_enter(b))
            btn.bind("<Leave>", lambda e, b=btn: self.on_leave(b))
    
    def on_enter(self, btn):
        if btn.cget("fg_color") == "transparent":
            btn.configure(text_color=("#000000", "#ffffff"))
    
    def on_leave(self, btn):
        if btn.cget("fg_color") == "transparent":
            btn.configure(text_color=("#666666", "#999999"))
    
    def select(self, value):
        self.selected = value
        for i, btn in enumerate(self.buttons):
            if self.values[i] == value:
                btn.configure(
                    fg_color=("#d0d0d0", "#ffffff"),  # Light: light, Dark: WHITE
                    text_color=("#000000", "#000000"),  # Always BLACK text
                    hover_color=("#c0c0c0", "#e0e0e0"))
            else:
                btn.configure(
                    fg_color="transparent", 
                    text_color=("#666666", "#999999"), 
                    hover_color=("#e0e0e0", "#1a1a1a"))
        if self.command:
            self.command(value)
    
    def get(self):
        return self.selected
    
    def set(self, value):
        self.select(value)


class ClickWave(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("ClickWave v1.0.0")
        self.geometry("750x720")
        self.minsize(600, 500)
        self.resizable(True, True)
        
        ctk.set_appearance_mode("dark")
        
        self.lang = "HU"
        self.is_clicking = False
        self.click_thread: Optional[threading.Thread] = None
        self.hotkey = "F6"
        self.use_current_location = True
        self.fps, self.ping, self.cps = 0, 0, 0
        self.click_times = deque(maxlen=60)
        self.widgets = {}
        
        self.create_ui()
        self.setup_hotkey()
        threading.Thread(target=self.update_fps, daemon=True).start()
        threading.Thread(target=self.update_ping, daemon=True).start()
        threading.Thread(target=self.update_cps, daemon=True).start()
        
    def t(self, k):
        return T[self.lang].get(k, k)
    
    def create_ui(self):
        scroll = ctk.CTkScrollableFrame(self, 
            fg_color=("#f5f5f5", "#0a0a0a"),  # Light/Dark backgrounds
            scrollbar_button_color=("#999999", "#333333"), 
            scrollbar_button_hover_color=("#777777", "#555555"))
        scroll.pack(fill="both", expand=True, padx=30, pady=30)
        main = scroll
        
        header = ctk.CTkFrame(main, fg_color="transparent")
        header.pack(fill="x", pady=(0, 40))
        
        left = ctk.CTkFrame(header, fg_color="transparent")
        left.pack(side="left")
        
        title_row = ctk.CTkFrame(left, fg_color="transparent")
        title_row.pack(anchor="w")
        
        ctk.CTkLabel(title_row, text="CLICKWAVE", font=("Arial", 32, "bold"), 
            text_color=("#000000", "#ffffff")).pack(side="left")
        
        stats = ctk.CTkFrame(title_row, fg_color="transparent")
        stats.pack(side="left", padx=(15, 0))
        self.widgets["fps"] = ctk.CTkLabel(stats, text="FPS: 0", font=("Arial", 11, "bold"), text_color="#4CAF50")
        self.widgets["fps"].pack(anchor="w", pady=1)
        self.widgets["ping"] = ctk.CTkLabel(stats, text="Ping: 0ms", font=("Arial", 11, "bold"), text_color="#2196F3")
        self.widgets["ping"].pack(anchor="w", pady=1)
        self.widgets["cps"] = ctk.CTkLabel(stats, text="CPS: 0", font=("Arial", 11, "bold"), text_color="#9E9E9E")
        self.widgets["cps"].pack(anchor="w", pady=1)
        
        self.widgets["creator"] = ctk.CTkLabel(left, text=self.t("creator"), font=("Arial", 10), text_color="gray")
        self.widgets["creator"].pack(anchor="w", pady=(2, 0))
        ctk.CTkLabel(left, text="v1.0.0", font=("Arial", 11), text_color="gray").pack(anchor="w")
        
        right = ctk.CTkFrame(header, fg_color="transparent")
        right.pack(side="right")
        
        self.widgets["lang_btn"] = ctk.CTkButton(right, text=self.lang, width=50, height=40, 
            font=("Arial", 14, "bold"), 
            fg_color=("#e0e0e0", "#1a1a1a"),  # Light: gray, Dark: dark gray
            text_color=("#000000", "#ffffff"),  # Light: black, Dark: white
            hover_color=("#d0d0d0", "#2a2a2a"), 
            corner_radius=20, border_width=1, 
            border_color=("#cccccc", "#333333"),
            command=self.toggle_lang)
        self.widgets["lang_btn"].pack(side="left", padx=(0, 10))
        
        self.theme_btn = ctk.CTkButton(right, text="🌙", width=40, height=40, font=("Arial", 18),
            fg_color=("#e0e0e0", "#1a1a1a"),
            hover_color=("#d0d0d0", "#2a2a2a"),
            corner_radius=20, border_width=1, 
            border_color=("#cccccc", "#333333"), 
            command=self.toggle_theme)
        self.theme_btn.pack(side="left", padx=(0, 10))
        
        self.status = ctk.CTkLabel(right, text="●", font=("Arial", 20), 
            text_color=("#666666", "#ffffff"))
        self.status.pack(side="left")
        
        time_panel = self.create_panel(main, "time_interval")
        self.interval_mode = ctk.StringVar(value="fixed")
        
        row1 = ctk.CTkFrame(time_panel, fg_color="transparent")
        row1.pack(fill="x", pady=5)
        self.widgets["fixed_radio"] = ctk.CTkRadioButton(row1, text=self.t("fixed_interval"), 
            variable=self.interval_mode, value="fixed", font=("Arial", 13),
            text_color=("#000000", "#ffffff"),  # EXPLICIT colors
            fg_color=("#000000", "#ffffff"),
            hover_color=("#666666", "#cccccc"),
            border_color=("#000000", "#ffffff"),
            border_width_checked=5, border_width_unchecked=2)
        self.widgets["fixed_radio"].pack(side="left")
        self.widgets["fixed_radio"].select()
        
        inputs1 = ctk.CTkFrame(row1, fg_color="transparent")
        inputs1.pack(side="right")
        self.hours = self.create_input(inputs1, "H", "0", 50)
        self.mins = self.create_input(inputs1, "M", "0", 50)
        self.secs = self.create_input(inputs1, "S", "0", 50)
        self.millis = self.create_input(inputs1, "MS", "100", 60)
        
        row2 = ctk.CTkFrame(time_panel, fg_color="transparent")
        row2.pack(fill="x", pady=(10, 5))
        self.widgets["random_radio"] = ctk.CTkRadioButton(row2, text=self.t("random_interval"),
            variable=self.interval_mode, value="random", font=("Arial", 13),
            text_color=("#000000", "#ffffff"),
            fg_color=("#000000", "#ffffff"),
            hover_color=("#666666", "#cccccc"),
            border_color=("#000000", "#ffffff"),
            border_width_checked=5, border_width_unchecked=2)
        self.widgets["random_radio"].pack(side="left")
        
        inputs2 = ctk.CTkFrame(row2, fg_color="transparent")
        inputs2.pack(side="right")
        self.rand_min = self.create_input(inputs2, "Min", "0.1", 65)
        ctk.CTkLabel(inputs2, text="-", font=("Arial", 14), 
            text_color=("#000000", "#ffffff")).pack(side="left", padx=3)
        self.rand_max = self.create_input(inputs2, "Max", "0.5", 65)
        self.widgets["sec_label"] = ctk.CTkLabel(inputs2, text=self.t("sec"), font=("Arial", 11), text_color="gray")
        self.widgets["sec_label"].pack(side="left", padx=(3, 0))
        
        click_panel = self.create_panel(main, "click_options")
        row3 = ctk.CTkFrame(click_panel, fg_color="transparent")
        row3.pack(fill="x", pady=5)
        
        btn_col = ctk.CTkFrame(row3, fg_color="transparent")
        btn_col.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.widgets["button_label"] = ctk.CTkLabel(btn_col, text=self.t("button"), font=("Arial", 11), text_color="gray")
        self.widgets["button_label"].pack(anchor="w")
        self.mouse_btn = SegmentedControl(btn_col, [self.t("left"), self.t("right"), self.t("middle")])
        self.mouse_btn.set(self.t("left"))
        self.mouse_btn.pack(fill="x", pady=(3, 0))
        
        type_col = ctk.CTkFrame(row3, fg_color="transparent")
        type_col.pack(side="left", fill="x", expand=True, padx=(8, 0))
        self.widgets["type_label"] = ctk.CTkLabel(type_col, text=self.t("type"), font=("Arial", 11), text_color="gray")
        self.widgets["type_label"].pack(anchor="w")
        self.click_type = SegmentedControl(type_col, [self.t("single"), self.t("double"), self.t("triple")])
        self.click_type.set(self.t("single"))
        self.click_type.pack(fill="x", pady=(3, 0))
        
        repeat_panel = self.create_panel(main, "repeat")
        self.repeat_mode = ctk.StringVar(value="stopped")
        
        row4 = ctk.CTkFrame(repeat_panel, fg_color="transparent")
        row4.pack(fill="x", pady=5)
        self.widgets["stopped_radio"] = ctk.CTkRadioButton(row4, text=self.t("until_stopped"),
            variable=self.repeat_mode, value="stopped", font=("Arial", 13),
            text_color=("#000000", "#ffffff"),
            fg_color=("#000000", "#ffffff"),
            hover_color=("#666666", "#cccccc"),
            border_color=("#000000", "#ffffff"),
            border_width_checked=5, border_width_unchecked=2)
        self.widgets["stopped_radio"].pack(side="left")
        self.widgets["stopped_radio"].select()
        
        row5 = ctk.CTkFrame(repeat_panel, fg_color="transparent")
        row5.pack(fill="x", pady=(10, 5))
        self.widgets["count_radio"] = ctk.CTkRadioButton(row5, text=self.t("fixed_count"),
            variable=self.repeat_mode, value="count", font=("Arial", 13),
            text_color=("#000000", "#ffffff"),
            fg_color=("#000000", "#ffffff"),
            hover_color=("#666666", "#cccccc"),
            border_color=("#000000", "#ffffff"),
            border_width_checked=5, border_width_unchecked=2)
        self.widgets["count_radio"].pack(side="left")
        self.repeat_count = self.create_input(row5, self.t("times"), "10", 70, "right")
        
        pos_panel = self.create_panel(main, "click_position")
        self.pos_mode = ctk.StringVar(value="current")
        
        row6 = ctk.CTkFrame(pos_panel, fg_color="transparent")
        row6.pack(fill="x", pady=5)
        self.widgets["current_radio"] = ctk.CTkRadioButton(row6, text=self.t("current_location"),
            variable=self.pos_mode, value="current", font=("Arial", 13),
            text_color=("#000000", "#ffffff"),
            fg_color=("#000000", "#ffffff"),
            hover_color=("#666666", "#cccccc"),
            border_color=("#000000", "#ffffff"),
            border_width_checked=5, border_width_unchecked=2)
        self.widgets["current_radio"].pack(side="left")
        self.widgets["current_radio"].select()
        
        row7 = ctk.CTkFrame(pos_panel, fg_color="transparent")
        row7.pack(fill="x", pady=(10, 5))
        self.widgets["fixed_radio_pos"] = ctk.CTkRadioButton(row7, text=self.t("fixed_position"),
            variable=self.pos_mode, value="fixed", font=("Arial", 13),
            text_color=("#000000", "#ffffff"),
            fg_color=("#000000", "#ffffff"),
            hover_color=("#666666", "#cccccc"),
            border_color=("#000000", "#ffffff"),
            border_width_checked=5, border_width_unchecked=2)
        self.widgets["fixed_radio_pos"].pack(side="left")
        
        pos_inputs = ctk.CTkFrame(row7, fg_color="transparent")
        pos_inputs.pack(side="right")
        self.widgets["get_btn"] = ctk.CTkButton(pos_inputs, text=self.t("get"), font=("Arial", 11, "bold"),
            fg_color=("#d0d0d0", "#ffffff"),  # Light: gray, Dark: WHITE
            text_color=("#000000", "#000000"),  # Always BLACK
            hover_color=("#c0c0c0", "#e0e0e0"),
            corner_radius=18, width=80, height=28, command=self.get_position)
        self.widgets["get_btn"].pack(side="left", padx=(0, 10))
        self.x_pos = self.create_input(pos_inputs, "X", "0", 65)
        self.y_pos = self.create_input(pos_inputs, "Y", "0", 65)
        
        self.main_btn = ctk.CTkButton(main, text=f"{self.t('start')}  ({self.hotkey})",
            font=("Arial", 16, "bold"), 
            fg_color=("#d0d0d0", "#ffffff"),  # Light: gray, Dark: WHITE
            text_color=("#000000", "#000000"),  # Always BLACK
            hover_color=("#c0c0c0", "#e0e0e0"),
            corner_radius=22, height=55, command=self.toggle)
        self.main_btn.pack(fill="x", pady=(25, 12))
        
        bottom = ctk.CTkFrame(main, fg_color="transparent")
        bottom.pack(fill="x")
        self.widgets["hotkey_btn"] = ctk.CTkButton(bottom, text=self.t("change_hotkey"),
            font=("Arial", 12), 
            fg_color=("#e0e0e0", "#1a1a1a"),  # Light: gray, Dark: dark gray
            text_color=("#000000", "#ffffff"),  # Light: black, Dark: white
            hover_color=("#d0d0d0", "#2a2a2a"),
            corner_radius=18, height=42, border_width=1, 
            border_color=("#cccccc", "#333333"),
            command=self.change_hotkey)
        self.widgets["hotkey_btn"].pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.widgets["settings_btn"] = ctk.CTkButton(bottom, text=self.t("settings"),
            font=("Arial", 12), 
            fg_color=("#e0e0e0", "#1a1a1a"),
            text_color=("#000000", "#ffffff"),
            hover_color=("#d0d0d0", "#2a2a2a"),
            corner_radius=18, height=42, border_width=1, 
            border_color=("#cccccc", "#333333"),
            command=self.settings)
        self.widgets["settings_btn"].pack(side="left", fill="x", expand=True, padx=(6, 0))
    
    def create_panel(self, parent, title_key):
        panel = ctk.CTkFrame(parent, 
            fg_color=("#ffffff", "#1a1a1a"),  # Light: white, Dark: dark gray
            corner_radius=12, border_width=1, 
            border_color=("#cccccc", "#333333"))
        panel.pack(fill="x", pady=(0, 15))
        
        title_frame = ctk.CTkFrame(panel, fg_color="transparent")
        title_frame.pack(fill="x", padx=18, pady=(12, 8))
        
        panel_title = ctk.CTkLabel(title_frame, text=self.t(title_key), font=("Arial", 14, "bold"),
            text_color=("#000000", "#ffffff"))
        panel_title.pack(anchor="w")
        self.widgets[f"panel_{title_key}"] = panel_title
        
        sep = ctk.CTkFrame(panel, 
            fg_color=("#cccccc", "#333333"), 
            height=1)
        sep.pack(fill="x", padx=18, pady=(0, 12))
        
        content = ctk.CTkFrame(panel, fg_color="transparent")
        content.pack(fill="x", padx=18, pady=(0, 12))
        return content
    
    def create_input(self, parent, label, value, width, side="left"):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(side=side, padx=4)
        ctk.CTkLabel(frame, text=label, font=("Arial", 10), text_color="gray").pack()
        entry = ctk.CTkEntry(frame, width=width, height=28, font=("Courier", 12),
            fg_color=("#ffffff", "#0a0a0a"),  # Light: white, Dark: black
            text_color=("#000000", "#ffffff"),  # Light: black, Dark: white
            border_color=("#cccccc", "#333333"),
            border_width=1, corner_radius=6, justify="center")
        entry.insert(0, value)
        entry.pack()
        return entry
    
    def toggle_lang(self):
        self.lang = T[self.lang]["next"]
        self.widgets["lang_btn"].configure(text=self.lang)
        self.update_lang()
    
    def update_lang(self):
        self.widgets["creator"].configure(text=self.t("creator"))
        self.widgets["panel_time_interval"].configure(text=self.t("time_interval"))
        self.widgets["fixed_radio"].configure(text=self.t("fixed_interval"))
        self.widgets["random_radio"].configure(text=self.t("random_interval"))
        self.widgets["sec_label"].configure(text=self.t("sec"))
        self.widgets["panel_click_options"].configure(text=self.t("click_options"))
        self.widgets["button_label"].configure(text=self.t("button"))
        self.widgets["type_label"].configure(text=self.t("type"))
        self.widgets["panel_repeat"].configure(text=self.t("repeat"))
        self.widgets["stopped_radio"].configure(text=self.t("until_stopped"))
        self.widgets["count_radio"].configure(text=self.t("fixed_count"))
        self.widgets["panel_click_position"].configure(text=self.t("click_position"))
        self.widgets["current_radio"].configure(text=self.t("current_location"))
        self.widgets["fixed_radio_pos"].configure(text=self.t("fixed_position"))
        self.widgets["get_btn"].configure(text=self.t("get"))
        new_mouse = [self.t("left"), self.t("right"), self.t("middle")]
        self.mouse_btn.values = new_mouse
        for i, btn in enumerate(self.mouse_btn.buttons):
            btn.configure(text=new_mouse[i])
        if not self.mouse_btn.get():
            self.mouse_btn.select(new_mouse[0])
        new_click = [self.t("single"), self.t("double"), self.t("triple")]
        self.click_type.values = new_click
        for i, btn in enumerate(self.click_type.buttons):
            btn.configure(text=new_click[i])
        if not self.click_type.get():
            self.click_type.select(new_click[0])
        btn_text = self.t("stop") if self.is_clicking else self.t("start")
        self.main_btn.configure(text=f"{btn_text}  ({self.hotkey})")
        self.widgets["hotkey_btn"].configure(text=self.t("change_hotkey"))
        self.widgets["settings_btn"].configure(text=self.t("settings"))
        self.repeat_count.master.winfo_children()[0].configure(text=self.t("times"))
    
    def toggle_theme(self):
        current = ctk.get_appearance_mode()
        if current == "Dark":
            ctk.set_appearance_mode("Light")
            self.theme_btn.configure(text="☀️")
        else:
            ctk.set_appearance_mode("Dark")
            self.theme_btn.configure(text="🌙")
    
    def get_position(self):
        def countdown():
            for i in range(3, 0, -1):
                self.widgets["get_btn"].configure(text=str(i))
                time.sleep(1)
            x, y = pyautogui.position()
            self.x_pos.delete(0, "end")
            self.x_pos.insert(0, str(x))
            self.y_pos.delete(0, "end")
            self.y_pos.insert(0, str(y))
            self.widgets["get_btn"].configure(text=self.t("get"))
        threading.Thread(target=countdown, daemon=True).start()
    
    def get_interval(self):
        if self.interval_mode.get() == "random":
            return random.uniform(float(self.rand_min.get()), float(self.rand_max.get()))
        h = int(self.hours.get() or 0)
        m = int(self.mins.get() or 0)
        s = int(self.secs.get() or 0)
        ms = int(self.millis.get() or 0)
        # ULTRA FAST: 0ms minimum for 100+ CPS capability
        return max(h * 3600 + m * 60 + s + ms / 1000, 0)
    
    def perform_click(self):
        button_map = {self.t("left"): "left", self.t("right"): "right", self.t("middle"): "middle"}
        clicks = {self.t("single"): 1, self.t("double"): 2, self.t("triple"): 3}
        btn = button_map[self.mouse_btn.get()]
        count = clicks[self.click_type.get()]
        self.click_times.append(time.time())
        self.use_current_location = self.pos_mode.get() == "current"
        if self.use_current_location:
            pyautogui.click(button=btn, clicks=count)
        else:
            x, y = int(self.x_pos.get()), int(self.y_pos.get())
            pyautogui.click(x, y, button=btn, clicks=count)
    
    def click_loop(self):
        total = 0
        max_clicks = int(self.repeat_count.get() or 0) if self.repeat_mode.get() == "count" else -1
        while self.is_clicking:
            try:
                # PRECISION TIMING for ultra-fast clicking
                interval = self.get_interval()
                start = time.perf_counter()
                
                self.perform_click()
                
                if max_clicks > 0:
                    total += 1
                    if total >= max_clicks:
                        self.after(0, self.stop)
                        break
                
                # Compensate for click execution time
                elapsed = time.perf_counter() - start
                sleep_time = max(0, interval - elapsed)
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    
            except Exception as e:
                print(f"Error: {e}")
                self.after(0, self.stop)
                break
    
    def toggle(self):
        self.stop() if self.is_clicking else self.start()
    
    def start(self):
        if not self.is_clicking:
            self.is_clicking = True
            self.click_thread = threading.Thread(target=self.click_loop, daemon=True)
            self.click_thread.start()
            self.main_btn.configure(text=f"{self.t('stop')}  ({self.hotkey})",
                fg_color=("#f5f5f5", "#000000"),  # Light: light gray, Dark: black
                text_color=("#000000", "#ffffff"),  # Light: black, Dark: white
                hover_color=("#e5e5e5", "#1a1a1a"),
                border_width=2,
                border_color=("#000000", "#ffffff"))
            self.status.configure(text_color="#00ff00")
    
    def stop(self):
        self.is_clicking = False
        self.click_times.clear()
        self.main_btn.configure(text=f"{self.t('start')}  ({self.hotkey})",
            fg_color=("#d0d0d0", "#ffffff"),
            text_color=("#000000", "#000000"),
            hover_color=("#c0c0c0", "#e0e0e0"), 
            border_width=0)
        self.status.configure(text_color=("#666666", "#ffffff"))
    
    def update_fps(self):
        frame_count = 0
        start_time = time.time()
        while True:
            try:
                frame_count += 1
                elapsed = time.time() - start_time
                if elapsed >= 1.0:
                    self.fps = int(frame_count / elapsed)
                    self.widgets["fps"].configure(text=f"FPS: {self.fps}")
                    frame_count = 0
                    start_time = time.time()
                time.sleep(0.016)
            except:
                break
    
    def update_ping(self):
        while True:
            try:
                param = '-n' if platform.system().lower() == 'windows' else '-c'
                start = time.time()
                kwargs = {'stdout': subprocess.PIPE, 'stderr': subprocess.PIPE, 'timeout': 2}
                if platform.system().lower() == 'windows':
                    kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
                subprocess.run(['ping', param, '1', '8.8.8.8'], **kwargs)
                self.ping = int((time.time() - start) * 1000)
                color = "#4CAF50" if self.ping < 50 else "#8BC34A" if self.ping < 100 else "#FFC107" if self.ping < 150 else "#FF5722"
                self.widgets["ping"].configure(text=f"Ping: {self.ping}ms", text_color=color)
                time.sleep(3)
            except:
                self.ping = 999
                try:
                    self.widgets["ping"].configure(text=f"Ping: {self.ping}ms", text_color="#F44336")
                except:
                    pass
                time.sleep(3)
    
    def update_cps(self):
        while True:
            try:
                current = time.time()
                while self.click_times and current - self.click_times[0] > 1.0:
                    self.click_times.popleft()
                self.cps = len(self.click_times)
                if self.cps == 0:
                    color = "#9E9E9E"
                elif self.cps < 5:
                    color = "#4CAF50"
                elif self.cps < 10:
                    color = "#FFC107"
                elif self.cps < 20:
                    color = "#FF9800"
                else:
                    color = "#FF5722"
                self.widgets["cps"].configure(text=f"CPS: {self.cps}", text_color=color)
                time.sleep(0.1)
            except:
                break
    
    def setup_hotkey(self):
        try:
            keyboard.add_hotkey(self.hotkey.lower(), self.toggle)
        except:
            pass
    
    def change_hotkey(self):
        dialog = ctk.CTkInputDialog(text=self.t("enter_hotkey"), title=self.t("change_hotkey"))
        new = dialog.get_input()
        if new:
            try:
                keyboard.remove_hotkey(self.hotkey.lower())
            except:
                pass
            self.hotkey = new
            keyboard.add_hotkey(new.lower(), self.toggle)
            text = f"{self.t('start')}  ({self.hotkey})" if not self.is_clicking else f"{self.t('stop')}  ({self.hotkey})"
            self.main_btn.configure(text=text)
    
    def settings(self):
        win = ctk.CTkToplevel(self)
        win.title(self.t("settings"))
        win.geometry("350x250")
        win.resizable(False, False)
        
        frame = ctk.CTkFrame(win, corner_radius=12,
            fg_color=("#ffffff", "#1a1a1a"))
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(frame, text=self.t("settings"), font=("Arial", 20, "bold"),
            text_color=("#000000", "#ffffff")).pack(pady=(15, 25))
        
        top_var = ctk.BooleanVar(value=self.attributes('-topmost'))
        
        def toggle_topmost():
            self.attributes('-topmost', top_var.get())
        
        ctk.CTkCheckBox(frame, text=self.t("always_on_top"), 
            variable=top_var, command=toggle_topmost,
            font=("Arial", 13),
            text_color=("#000000", "#ffffff"),
            fg_color=("#000000", "#ffffff"),
            hover_color=("#666666", "#cccccc"),
            border_color=("#000000", "#ffffff")).pack(pady=12)
        
        ctk.CTkButton(frame, text=self.t("close"), command=win.destroy, font=("Arial", 12),
            fg_color=("#d0d0d0", "#ffffff"),
            text_color=("#000000", "#000000"),
            hover_color=("#c0c0c0", "#e0e0e0"),
            corner_radius=18, height=38, width=100).pack(pady=(20, 0))
    
    def close(self):
        self.is_clicking = False
        try:
            keyboard.unhook_all()
        except:
            pass
        self.destroy()


if __name__ == "__main__":
    app = ClickWave()
    app.protocol("WM_DELETE_WINDOW", app.close)
    app.mainloop()
