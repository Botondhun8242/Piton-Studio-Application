import tkinter as tk
from tkinter import messagebox
import time
import threading
import sqlite3
import hashlib
import random
import datetime
import os
import winsound

# --- KONFIGURÁCIÓ ---
DB_NAME = "piton_v62_global.db"
VERSION = "v6.2-Global"

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

# NYELVEK (6 Nyelv!)
LANGS = {
    "HU": {"start": "INDÍTÁS", "login": "Belépés", "rem": "Maradjak belépve", "best": "REKORD:", "hist": "ELŐZMÉNYEK"},
    "EN": {"start": "START", "login": "Login", "rem": "Keep me logged in", "best": "BEST:", "hist": "HISTORY"},
    "DE": {"start": "START", "login": "Anmelden", "rem": "Angemeldet bleiben", "best": "REKORD:", "hist": "VERLAUF"},
    "FR": {"start": "DÉMARRER", "login": "Connexion", "rem": "Rester connecté", "best": "RECORD:", "hist": "HISTOIRE"},
    "RU": {"start": "СТАРТ", "login": "Вход", "rem": "Запомнить меня", "best": "РЕКОРД:", "hist": "ИСТОРИЯ"},
    "CN": {"start": "开始", "login": "登录", "rem": "保持登录", "best": "最佳:", "hist": "历史记录"}
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
        self.active_btn = None
        self.lang = "HU"
        self.sound = True
        
        # Rekord követés
        self.session_best = 0.0
        
        # KPS Anti-Hold
        self.pressed_keys = set()
        self.stats_data = []

        # FPS / Ping
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
        self.refresh_stats()
        self.anim_loop()

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
        
        # --- 1. HEADER ---
        # Cím (Fent)
        self.canvas.create_text(w/2, 50, text="CPS PRO", fill=c['acc'], font=("Verdana", 42, "bold"))
        
        # REKORD (Cím alatt)
        best_txt = f"{t['best']} {self.session_best}"
        self.canvas.create_text(w/2, 90, text=best_txt, fill=c['sub'], font=("Arial", 14, "bold"))
        
        # Gombok (Bal fent) - Nyelv, Téma, Hang
        sets = [self.lang, ("☀" if self.theme_key=="dark" else "☾"), ("🔊" if self.sound else "🔇")]
        for i, s in enumerate(sets):
            x = 20 + i*80
            self.r_rect(x, 20, x+70, 70, 15, fill=c['surf'], outline=c['border'])
            self.canvas.create_text(x+35, 45, text=s, fill=c['txt'], font=("Arial", 14, "bold"))

        # Kilépés & User (Jobb fent)
        self.r_rect(w-80, 20, w-20, 70, 15, fill=c['err'])
        self.canvas.create_text(w-50, 45, text="✕", fill="white", font=("Arial", 20, "bold"))
        
        u_txt = self.user if self.user else t['login']
        # User gomb szélesebb, hogy a nevek kiférjenek
        self.r_rect(w-320, 20, w-100, 70, 15, fill=c['surf'], outline=c['border'])
        self.canvas.create_text(w-210, 45, text=f"👤 {u_txt}", fill=c['txt'], font=("Arial", 11, "bold"))

        # --- 2. OLDALSÁVOK ---
        # Módok (Bal)
        modes = ["1s", "5s", "10s", "60s", "KPS", "CTRL"]
        for i, m in enumerate(modes):
            active = (self.mode == m or (m == "CTRL" and self.mode == "CONTROLLER"))
            col = c['acc'] if active else c['border']
            txt_col = c['txt'] if active else c['sub']
            self.r_rect(30, 160 + i*80, 160, 230 + i*80, 15, fill=c['surf'], outline=col, width=2 if active else 1)
            self.canvas.create_text(95, 195 + i*80, text=m, fill=txt_col, font=("Arial", 16, "bold"))

        # History (Jobb)
        self.canvas.create_text(w-150, 140, text=t['hist'], fill=c['sub'], font=("Arial", 12, "bold"))
        if self.stats_data:
            for i, r in enumerate(self.stats_data):
                self.r_rect(w-280, 160 + i*55, w-20, 210 + i*55, 10, fill=c['surf'])
                self.canvas.create_text(w-150, 185 + i*55, text=f"{r[0]}  |  {r[1]}", fill=c['txt'], font=("Consolas", 12))

        # --- 3. KÖZÉP ---
        cx, cy = w/2, h/2
        if self.mode == "CONTROLLER":
            self.draw_ctrl(cx, cy, c)
        else:
            live_cps = self.calc_live_cps()
            is_fire = (live_cps >= 12 and self.mode != "KPS")
            main_col = c['fire'] if is_fire else c['acc']
            
            self.r_rect(cx-250, cy-180, cx+250, cy+180, 40, fill=c['surf'], outline=main_col, width=5 if is_fire else 2)
            
            disp_val = f"{live_cps:.1f}"
            if self.mode == "KPS": disp_val = str(self.total_clicks)
            
            self.canvas.create_text(cx, cy-20, text=disp_val, fill=c['txt'], font=("Verdana", 100, "bold"))
            self.canvas.create_text(cx, cy+80, text="CPS" if self.mode != "KPS" else "KEYS", fill=c['sub'], font=("Arial", 20))
            
            info_txt = t["start"]
            if self.timer_active: info_txt = f"{self.get_remaining_time():.1f}s"
            self.canvas.create_text(cx, cy+130, text=info_txt, fill=main_col, font=("Arial", 14, "bold"))
            
            if is_fire:
                self.canvas.create_text(cx, cy-130, text="🔥 MAX POWER 🔥", fill=c['fire'], font=("Arial", 16, "bold"))

        # --- 4. FOOTER ---
        # Created by (Bal lent)
        self.canvas.create_text(20, h-20, text="Created by Piton Studio", fill=c['sub'], anchor="sw", font=("Arial", 10, "italic"))
        
        # Verzió (Jobb lent)
        self.canvas.create_text(w-20, h-20, text=VERSION, fill=c['sub'], anchor="se", font=("Arial", 10))

        # FPS / Ping (Közép lent)
        self.canvas.create_text(cx, h-40, text=f"FPS: {self.fps}  |  PING: {self.ping}ms", fill=c['sub'], font=("Consolas", 14, "bold"))

    def draw_ctrl(self, cx, cy, c):
        
        self.r_rect(cx-280, cy-140, cx+280, cy+160, 60, fill=c['surf'], outline="#333")
        btns = [("Y",cx+120,cy-20,"i"),("B",cx+170,cy+30,"l"),("A",cx+120,cy+80,"space"),("X",cx+70,cy+30,"j"),
                ("▲",cx-120,cy+30,"up"),("▼",cx-120,cy+90,"down"),("◄",cx-150,cy+60,"left"),("►",cx-90,cy+60,"right"),
                ("LB",cx-150,cy-80,"q"),("RB",cx+150,cy-80,"e"),("≡",cx+40,cy-20,"m"),("⧉",cx-40,cy-20,"n")]
        for txt, x, y, k in btns:
            act = (self.active_btn == k)
            self.canvas.create_oval(x-20,y-20,x+20,y+20, fill=c['acc'] if act else "#222", outline=c['sub'])
            self.canvas.create_text(x,y,text=txt, fill="white", font=("Arial", 10, "bold"))
        # Stickek
        for dx in [-180, 80]:
            dy = cy - 20 if dx < 0 else cy + 80
            self.canvas.create_oval(dx+cx-35,dy-35,dx+cx+35,dy+35, outline=c['sub'], width=2)
            dx_r = random.uniform(-1,1); dy_r = random.uniform(-1,1)
            self.canvas.create_oval(dx+cx-4+dx_r,dy-4+dy_r,dx+cx+4+dx_r,dy+4+dy_r, fill=c['acc'])

    # --- LOGIKA ---
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
        # Felső sáv
        if e.y < 80:
            if w-80 < e.x: self.destroy()
            elif w-320 < e.x < w-100: self.show_login()
            elif 20 < e.x < 90: 
                # NYELV VÁLTÁS (Ciklikus)
                curr_idx = L_KEYS.index(self.lang)
                self.lang = L_KEYS[(curr_idx + 1) % len(L_KEYS)]
            elif 100 < e.x < 170: self.theme_key = "light" if self.theme_key == "dark" else "dark"
            elif 180 < e.x < 250: self.sound = not self.sound
            return
        # Módok
        if e.x < 170:
            modes = ["1s", "5s", "10s", "60s", "KPS", "CTRL"]
            for i, m in enumerate(modes):
                if 160 + i*80 < e.y < 230 + i*80:
                    self.mode = m if m != "CTRL" else "CONTROLLER"
                    self.reset_game()
            return
        # Játék
        if self.mode not in ["KPS", "CONTROLLER"]: self.reg_input()

    def on_key_press(self, e):
        k = e.keysym.lower()
        if self.mode == "CONTROLLER": self.active_btn = k
        elif self.mode == "KPS":
            if k in self.pressed_keys: return
            self.pressed_keys.add(k)
            self.reg_input()

    def on_key_release(self, e):
        k = e.keysym.lower()
        if k in self.pressed_keys: self.pressed_keys.remove(k)
        if self.mode == "CONTROLLER": self.active_btn = None

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
            if self.sound: 
                try: winsound.Beep(1000, 5)
                except: pass

    def timer_thread(self):
        limit = int(self.mode[:-1])
        while time.time() - self.start_time < limit: time.sleep(0.05)
        self.timer_active = False; self.running = False
        final = round(self.total_clicks / limit, 2)
        if final > self.session_best: self.session_best = final
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
            self.db.cursor.execute("SELECT mode, score FROM scores WHERE uid=? ORDER BY date DESC LIMIT 8", (res[0],))
            self.stats_data = self.db.cursor.fetchall()

    def reset_game(self):
        self.running = False; self.timer_active = False; self.clicks = []; self.total_clicks = 0

    def anim_loop(self):
        self.frame_cnt += 1
        if time.time() - self.last_fps_t >= 1.0:
            self.fps = self.frame_cnt; self.frame_cnt = 0; self.last_fps_t = time.time()
            self.ping = random.randint(10, 25)
        self.draw()
        self.after(16, self.anim_loop)

    def show_login(self):
        c = self.get_c()
        t = self.get_t()
        top = tk.Toplevel(self); top.geometry("300x350"); top.configure(bg=c['bg'])
        tk.Label(top, text=t['login'], fg=c['acc'], bg=c['bg'], font=("Arial", 16)).pack(pady=20)
        u_e = tk.Entry(top); u_e.pack(pady=5); p_e = tk.Entry(top, show="*"); p_e.pack(pady=5)
        rem = tk.BooleanVar()
        tk.Checkbutton(top, text=t['rem'], variable=rem, bg=c['bg'], fg=c['txt'], selectcolor="black").pack(pady=10)
        def do():
            u, p = u_e.get(), hashlib.sha256(p_e.get().encode()).hexdigest()
            try: self.db.cursor.execute("INSERT INTO users (user, pwd) VALUES (?,?)", (u, p)); self.db.conn.commit()
            except: pass
            self.db.cursor.execute("SELECT id FROM users WHERE user=? AND pwd=?", (u, p))
            res = self.db.cursor.fetchone()
            if res:
                self.user = u
                if rem.get():
                    tok = hashlib.sha256(str(random.random()).encode()).hexdigest()
                    self.db.cursor.execute("INSERT INTO sessions VALUES (?,?,?)", (tok, res[0], "9999-12-31")); self.db.conn.commit()
                    with open("global.session", "w") as f: f.write(tok)
                self.refresh_stats(); top.destroy()
        tk.Button(top, text="GO", command=do, bg=c['acc'], fg="white", width=10).pack(pady=20)

    def check_session(self):
        if os.path.exists("global.session"):
            with open("global.session") as f: tok = f.read()
            self.db.cursor.execute("SELECT uid FROM sessions WHERE token=?", (tok,))
            res = self.db.cursor.fetchone()
            if res:
                self.db.cursor.execute("SELECT user FROM users WHERE id=?", (res[0],))
                self.user = self.db.cursor.fetchone()[0]

if __name__ == "__main__":
    PitonApp().mainloop()
