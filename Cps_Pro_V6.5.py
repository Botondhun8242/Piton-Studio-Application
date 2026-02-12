import tkinter as tk
from tkinter import messagebox
import time
import threading
import sqlite3
import hashlib
import random
import datetime
import os

# --- HANG ÉS KONTROLLER MODULE ---
try:
    import winsound
except ImportError:
    winsound = None

try:
    import pygame
    pygame.init()
    pygame.joystick.init()
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False

# --- KONFIGURÁCIÓ ---
DB_NAME = "piton_pro_v65.db" 
VERSION = "v6.5-Perf"

# TÉMÁK
THEMES = {
    "dark": {
        "bg": "#09090b", "surf": "#18181b", "acc": "#8b5cf6", 
        "txt": "#ffffff", "sub": "#a1a1aa", "err": "#ef4444", 
        "fire": "#f97316", "border": "#27272a"
    },
    "light": {
        "bg": "#f8fafc", "surf": "#ffffff", "acc": "#6366f1", 
        "txt": "#0f172a", "sub": "#64748b", "err": "#ef4444", 
        "fire": "#ea580c", "border": "#e2e8f0"
    }
}

# NYELVEK
LANGS = {
    "HU": {"start": "KATTINTS!", "login": "Belépés", "reg": "Regisztráció", "rem": "Maradjak belépve", "best": "REKORD:", "hist": "ELŐZMÉNYEK", "ctr_err": "Nincs kontroller!"},
    "EN": {"start": "START", "login": "Login", "reg": "Register", "rem": "Keep me logged in", "best": "BEST:", "hist": "HISTORY", "ctr_err": "No Controller!"},
    "DE": {"start": "START", "login": "Anmelden", "reg": "Registrieren", "rem": "Angemeldet bleiben", "best": "REKORD:", "hist": "VERLAUF", "ctr_err": "Kein Controller!"},
    "FR": {"start": "DÉMARRER", "login": "Connexion", "reg": "S'inscrire", "rem": "Rester connecté", "best": "RECORD:", "hist": "HISTOIRE", "ctr_err": "Pas de manette!"},
    "RU": {"start": "СТАРТ", "login": "Вход", "reg": "Регистрация", "rem": "Запомнить меня", "best": "РЕКОРД:", "hist": "ИСТОРИЯ", "ctr_err": "Нет контроллера!"},
    "CN": {"start": "开始", "login": "登录", "reg": "注册", "rem": "保持登录", "best": "最佳:", "hist": "历史记录", "ctr_err": "无控制器!"}
}
L_KEYS = ["HU", "EN", "DE", "FR", "RU", "CN"]

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, user TEXT UNIQUE, pwd TEXT)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS scores (uid INTEGER, mode TEXT, score REAL, date TEXT)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS sessions (token TEXT, uid INTEGER, exp TEXT)')
        self.conn.commit()

class PitonApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.attributes('-fullscreen', True)
        
        # Állapotok
        self.theme_key = "dark"
        self.user = None
        self.mode = "10s"
        self.running = False
        self.timer_active = False
        self.clicks = []         
        self.total_clicks = 0
        self.start_time = 0
        self.lang = "HU"
        self.sound = True
        
        # Rekord
        self.session_best = 0.0
        
        # Controller
        self.joystick = None
        self.ctrl_input = None 
        self.init_controller()

        # Egyéb
        self.pressed_keys = set()
        self.stats_data = []
        
        # FPS / Ping Init
        self.fps = 0
        self.frame_cnt = 0
        self.last_fps_t = time.time()
        self.ping = 12

        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        self.canvas.bind("<Button-1>", self.on_click)
        self.bind("<Key>", self.on_key_press)
        self.bind("<KeyRelease>", self.on_key_release)
        
        self.check_session()
        self.anim_loop()

    def init_controller(self):
        if HAS_PYGAME and pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()

    def get_c(self): return THEMES[self.theme_key]
    def get_t(self): return LANGS[self.lang]

    def r_rect(self, x1, y1, x2, y2, r, **kwargs):
        p = [x1+r, y1, x1+r, y1, x2-r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y1+r, x2, y2-r, x2, y2-r, x2, y2, x2-r, y2, x2-r, y2, x1+r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y2-r, x1, y1+r, x1, y1+r, x1, y1]
        return self.canvas.create_polygon(p, **kwargs, smooth=True)

    def draw(self):
        self.canvas.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        c = self.get_c()
        t = self.get_t()
        self.canvas.configure(bg=c['bg'])
        
        # --- HEADER ---
        self.canvas.create_text(w/2, 50, text="CPS PRO", fill=c['acc'], font=("Verdana", 42, "bold"))
        best_txt = f"{t['best']} {self.session_best}"
        self.canvas.create_text(w/2, 90, text=best_txt, fill=c['sub'], font=("Arial", 14, "bold"))
        
        # Gombok
        sets = [self.lang, ("☀" if self.theme_key=="dark" else "☾"), ("🔊" if self.sound else "🔇")]
        for i, s in enumerate(sets):
            x = 20 + i*80
            self.r_rect(x, 20, x+70, 70, 15, fill=c['surf'], outline=c['border'])
            self.canvas.create_text(x+35, 45, text=s, fill=c['txt'], font=("Arial", 14, "bold"))

        self.r_rect(w-80, 20, w-20, 70, 15, fill=c['err'])
        self.canvas.create_text(w-50, 45, text="✕", fill="white", font=("Arial", 20, "bold"))
        
        u_txt = self.user if self.user else t['login']
        self.r_rect(w-320, 20, w-100, 70, 15, fill=c['surf'], outline=c['border'])
        self.canvas.create_text(w-210, 45, text=f"👤 {u_txt}", fill=c['txt'], font=("Arial", 11, "bold"))

        # --- OLDALSÁV ---
        modes = ["1s", "5s", "10s", "60s", "KPS", "CTRL"]
        for i, m in enumerate(modes):
            active = (self.mode == m or (m == "CTRL" and self.mode == "CONTROLLER"))
            col = c['acc'] if active else c['border']
            txt_col = c['txt'] if active else c['sub']
            self.r_rect(30, 160 + i*80, 160, 230 + i*80, 15, fill=c['surf'], outline=col, width=2 if active else 1)
            self.canvas.create_text(95, 195 + i*80, text=m, fill=txt_col, font=("Arial", 16, "bold"))

        # History
        self.canvas.create_text(w-150, 140, text=t['hist'], fill=c['sub'], font=("Arial", 12, "bold"))
        if self.stats_data:
            for i, r in enumerate(self.stats_data):
                self.r_rect(w-280, 160 + i*55, w-20, 210 + i*55, 10, fill=c['surf'])
                self.canvas.create_text(w-150, 185 + i*55, text=f"{r[0]}  |  {r[1]}", fill=c['txt'], font=("Consolas", 12))

        # --- FŐ RÉSZ ---
        cx, cy = w/2, h/2
        
        if self.mode == "CONTROLLER":
            if not HAS_PYGAME:
                self.canvas.create_text(cx, cy, text="TELEPÍTSD A PYGAME-ET!\npip install pygame", fill=c['err'], font=("Arial", 20))
            elif not self.joystick:
                self.canvas.create_text(cx, cy, text=t['ctr_err'], fill=c['err'], font=("Arial", 30, "bold"))
            elif self.ctrl_input:
                self.draw_ctrl_icon(cx, cy, c)
            else:
                self.canvas.create_text(cx, cy, text="PRESS ANY BUTTON", fill=c['sub'], font=("Arial", 20, "bold"))
        else:
            live_cps = self.calc_live_cps()
            is_fire = (live_cps >= 12 and self.mode != "KPS")
            main_col = c['fire'] if is_fire else c['acc']
            self.r_rect(cx-250, cy-180, cx+250, cy+180, 40, fill=c['surf'], outline=main_col, width=5 if is_fire else 2)
            disp_val = f"{live_cps:.1f}"
            if self.mode == "KPS": disp_val = str(self.total_clicks)
            self.canvas.create_text(cx, cy-20, text=disp_val, fill=c['txt'], font=("Verdana", 100, "bold"))
            self.canvas.create_text(cx, cy+80, text="CPS" if self.mode != "KPS" else "KEYS", fill=c['sub'], font=("Arial", 20))
            info_txt = f"{self.get_remaining_time():.1f}s" if self.timer_active else t["start"]
            self.canvas.create_text(cx, cy+130, text=info_txt, fill=main_col, font=("Arial", 14, "bold"))

        # Footer & FPS PING (VISSZAKERÜLT!)
        self.canvas.create_text(20, h-20, text="Created by Piton Studio", fill=c['sub'], anchor="sw", font=("Arial", 10, "italic"))
        self.canvas.create_text(w-20, h-20, text=VERSION, fill=c['sub'], anchor="se", font=("Arial", 10))
        
        # ITT A HIÁNYZÓ SOR:
        self.canvas.create_text(cx, h-40, text=f"FPS: {self.fps}  |  PING: {self.ping}ms", fill=c['sub'], font=("Consolas", 12, "bold"))

    def draw_ctrl_icon(self, cx, cy, c):
        inp = self.ctrl_input
        self.r_rect(cx-100, cy-100, cx+100, cy+100, 30, fill=c['acc'])
        
        text_map = {
            "BTN 0": "A", "BTN 1": "B", "BTN 2": "X", "BTN 3": "Y",
            "BTN 4": "LB", "BTN 5": "RB", "BTN 6": "BACK", "BTN 7": "START",
            "BTN 8": "L-STICK", "BTN 9": "R-STICK",
            "HAT (0, 1)": "▲", "HAT (0, -1)": "▼", "HAT (-1, 0)": "◀", "HAT (1, 0)": "▶"
        }
        
        display_text = inp
        if inp in text_map: display_text = text_map[inp]
        elif "AXIS" in inp:
            parts = inp.split()
            idx = parts[1]
            if idx == "0": display_text = "L-STICK ↔"
            elif idx == "1": display_text = "L-STICK ↕"
            elif idx == "2": display_text = "R-STICK ↔" 
            elif idx == "3": display_text = "R-STICK ↕"
            elif idx == "4": display_text = "LT"
            elif idx == "5": display_text = "RT"

        self.canvas.create_text(cx, cy, text=display_text, fill="white", font=("Arial", 40, "bold"))

    def poll_controller(self):
        if not HAS_PYGAME or not self.joystick: 
            if HAS_PYGAME and pygame.joystick.get_count() > 0: self.init_controller()
            return
            
        pygame.event.pump()
        active = None
        
        for i in range(self.joystick.get_numbuttons()):
            if self.joystick.get_button(i): active = f"BTN {i}"
        
        if not active:
            for i in range(self.joystick.get_numhats()):
                hat = self.joystick.get_hat(i)
                if hat != (0, 0): active = f"HAT {hat}"

        if not active:
            for i in range(self.joystick.get_numaxes()):
                val = self.joystick.get_axis(i)
                if abs(val) > 0.3:
                    if val < -0.9: continue 
                    active = f"AXIS {i}"

        self.ctrl_input = active

    def calc_live_cps(self):
        now = time.time()
        self.clicks = [t for t in self.clicks if t > now - 1.0]
        return len(self.clicks)

    def get_remaining_time(self):
        if not self.timer_active: return 0
        limit = int(self.mode[:-1])
        return max(0, limit - (time.time() - self.start_time))

    def on_click(self, e):
        w = self.winfo_width()
        if e.y < 80:
            if w-80 < e.x: self.destroy()
            elif w-320 < e.x < w-100: self.show_auth_window()
            elif 20 < e.x < 90: 
                curr_idx = L_KEYS.index(self.lang)
                self.lang = L_KEYS[(curr_idx + 1) % len(L_KEYS)]
            elif 100 < e.x < 170: self.theme_key = "light" if self.theme_key == "dark" else "dark"
            elif 180 < e.x < 250: self.sound = not self.sound
            return
        if e.x < 170:
            modes = ["1s", "5s", "10s", "60s", "KPS", "CTRL"]
            for i, m in enumerate(modes):
                if 160 + i*80 < e.y < 230 + i*80:
                    self.mode = m if m != "CTRL" else "CONTROLLER"
                    self.reset_game()
            return
        if self.mode not in ["KPS", "CONTROLLER"]: self.reg_input()

    def on_key_press(self, e):
        k = e.keysym.lower()
        if self.mode == "KPS":
            if k in self.pressed_keys: return
            self.pressed_keys.add(k)
            self.reg_input()

    def on_key_release(self, e):
        k = e.keysym.lower()
        if k in self.pressed_keys: self.pressed_keys.remove(k)

    def reg_input(self):
        if not self.timer_active and not self.running:
            self.reset_game()
            self.running = True
            self.start_time = time.time()
            if "s" in self.mode:
                self.timer_active = True
                threading.Thread(target=self.timer_thread, daemon=True).start()
        if self.running or self.mode == "KPS":
            self.clicks.append(time.time())
            self.total_clicks += 1
            if self.sound and winsound: 
                try: winsound.Beep(1000, 5)
                except: pass

    def timer_thread(self):
        limit = int(self.mode[:-1])
        while time.time() - self.start_time < limit: time.sleep(0.05)
        self.timer_active = False; self.running = False
        final = round(self.total_clicks / limit, 2)
        if self.user:
            self.db.cursor.execute("INSERT INTO scores (uid, mode, score, date) SELECT id, ?, ?, ? FROM users WHERE user=?", 
                                   (self.mode, final, datetime.datetime.now().isoformat(), self.user))
            self.db.conn.commit()
            self.refresh_stats()

    def refresh_stats(self):
        if not self.user: self.stats_data = []; return
        self.db.cursor.execute("SELECT id FROM users WHERE user=?", (self.user,))
        res = self.db.cursor.fetchone()
        if res:
            uid = res[0]
            self.db.cursor.execute("SELECT mode, score FROM scores WHERE uid=? ORDER BY date DESC LIMIT 8", (uid,))
            self.stats_data = self.db.cursor.fetchall()
            self.db.cursor.execute("SELECT MAX(score) FROM scores WHERE uid=?", (uid,))
            best = self.db.cursor.fetchone()[0]
            if best: self.session_best = best
            else: self.session_best = 0.0

    def reset_game(self):
        self.running = False; self.timer_active = False; self.clicks = []; self.total_clicks = 0

    def anim_loop(self):
        self.frame_cnt += 1
        # FPS számítás logika
        if time.time() - self.last_fps_t >= 1.0:
            self.fps = self.frame_cnt; self.frame_cnt = 0; self.last_fps_t = time.time()
            self.ping = random.randint(10, 25) # Szimulált ping
        
        if self.mode == "CONTROLLER":
            self.poll_controller()
            
        self.draw()
        self.after(16, self.anim_loop)

    def show_auth_window(self):
        c = self.get_c(); t = self.get_t()
        top = tk.Toplevel(self); top.geometry("350x400"); top.configure(bg=c['bg'])
        tk.Label(top, text="PITON ACCOUNT", fg=c['acc'], bg=c['bg'], font=("Verdana", 16, "bold")).pack(pady=20)
        
        tk.Label(top, text="User:", bg=c['bg'], fg=c['sub']).pack()
        u_e = tk.Entry(top, bg=c['surf'], fg=c['txt'], insertbackground=c['txt']); u_e.pack(pady=5)
        tk.Label(top, text="Pass:", bg=c['bg'], fg=c['sub']).pack()
        p_e = tk.Entry(top, show="*", bg=c['surf'], fg=c['txt'], insertbackground=c['txt']); p_e.pack(pady=5)
        rem = tk.BooleanVar()
        tk.Checkbutton(top, text=t['rem'], variable=rem, bg=c['bg'], fg=c['txt'], selectcolor=c['bg'], activebackground=c['bg']).pack(pady=10)

        def perform_login():
            u, p = u_e.get(), hashlib.sha256(p_e.get().encode()).hexdigest()
            self.db.cursor.execute("SELECT id FROM users WHERE user=? AND pwd=?", (u, p))
            res = self.db.cursor.fetchone()
            if res:
                self.user = u
                if rem.get():
                    tok = hashlib.sha256(str(random.random()).encode()).hexdigest()
                    self.db.cursor.execute("INSERT INTO sessions VALUES (?,?,?)", (tok, res[0], "9999-12-31")); self.db.conn.commit()
                    with open("global.session", "w") as f: f.write(tok)
                self.refresh_stats()
                top.destroy()
            else: messagebox.showerror("Error", "Invalid credentials!")

        def perform_reg():
            u, p = u_e.get(), hashlib.sha256(p_e.get().encode()).hexdigest()
            if not u or not p_e.get(): return
            try:
                self.db.cursor.execute("INSERT INTO users (user, pwd) VALUES (?,?)", (u, p))
                self.db.conn.commit()
                messagebox.showinfo("Success", f"User {u} created!")
            except sqlite3.IntegrityError: messagebox.showerror("Error", "User exists!")

        btn_frame = tk.Frame(top, bg=c['bg']); btn_frame.pack(pady=20)
        tk.Button(btn_frame, text=t['login'], command=perform_login, bg=c['acc'], fg="white", font=("Arial", 10, "bold"), width=12).pack(side="left", padx=5)
        tk.Button(btn_frame, text=t['reg'], command=perform_reg, bg=c['surf'], fg=c['txt'], font=("Arial", 10), width=12).pack(side="left", padx=5)

    def check_session(self):
        if os.path.exists("global.session"):
            with open("global.session") as f: tok = f.read()
            self.db.cursor.execute("SELECT uid FROM sessions WHERE token=?", (tok,))
            res = self.db.cursor.fetchone()
            if res:
                self.db.cursor.execute("SELECT user FROM users WHERE id=?", (res[0],))
                self.user = self.db.cursor.fetchone()[0]
                self.refresh_stats()

if __name__ == "__main__":
    PitonApp().mainloop()
