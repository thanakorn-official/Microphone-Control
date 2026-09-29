import tkinter as tk
from tkinter import ttk
import threading
import json
import os
import sys
import ctypes
from ctypes import wintypes
import winreg
import comtypes
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume, EDataFlow, DEVICE_STATE
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw, ImageTk

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE = os.path.join(BASE_DIR, "mic_config.json")
LANG_FILE = os.path.join(BASE_DIR, "languages.json")
FONT_FAMILY = "Leelawadee UI"
APP_REGISTRY_NAME = "MicMuteController"
STARTUP_REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"

MUTEX_NAME = "Local\\MicMuteController_SingleInstance_Mutex"
EVENT_NAME = "Local\\MicMuteController_RestoreWindow_Event"
ERROR_ALREADY_EXISTS = 183
EVENT_MODIFY_STATE = 0x0002

WM_HOTKEY = 0x0312
WM_QUIT = 0x0012
MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008
MOD_NOREPEAT = 0x4000
HOTKEY_ID = 1

VK_MAP = {
    "f1": 0x70, "f2": 0x71, "f3": 0x72, "f4": 0x73, "f5": 0x74, "f6": 0x75,
    "f7": 0x76, "f8": 0x77, "f9": 0x78, "f10": 0x79, "f11": 0x7A, "f12": 0x7B,
    "space": 0x20, "tab": 0x09, "capslock": 0x14, "pause": 0x13,
    "insert": 0x2D, "delete": 0x2E, "home": 0x24, "end": 0x23,
    "prior": 0x21, "next": 0x22, "num_lock": 0x90, "scroll_lock": 0x91,
    "multiply": 0x6A, "add": 0x6B, "subtract": 0x6D, "divide": 0x6F,
    "grave": 0xC0, "minus": 0xBD, "equal": 0xBB, "backslash": 0xDC,
    "bracketleft": 0xDB, "bracketright": 0xDD, "semicolon": 0xBA,
    "apostrophe": 0xDE, "comma": 0xBC, "period": 0xBE, "slash": 0xBF
}

DEFAULT_TRANSLATIONS = {
    "th": {
        "lang_name": "ไทย (Thai)",
        "window_title": "Mic Mute Controller",
        "lang_label": "ภาษา:",
        "mic_label": "ไมโครโฟนที่ใช้งาน (อัปเดตอัตโนมัติ):",
        "status_checking": "สถานะ: กำลังตรวจสอบ...",
        "status_no_mic": "ไม่พบไมโครโฟนในระบบ",
        "status_muted": "สถานะ: ปิดไมค์ (MUTED)",
        "status_active": "สถานะ: เปิดไมค์ (ACTIVE)",
        "hk_frame": " ตั้งค่าปุ่มคีย์ลัด (Hotkey) ",
        "hk_btn_normal": "ปุ่มปัจจุบัน: [ {hotkey} ]  (คลิกเพื่อเปลี่ยน)",
        "hk_btn_record": "กำลังรอรับปุ่ม... กดปุ่มในหน้าต่างนี้ได้เลย (Esc = ยกเลิก)",
        "toggle_btn": "สลับ เปิด / ปิด ไมค์",
        "osd_chk": "แสดงหน้าต่างลอยแจ้งเตือนด้านล่างจอ (Floating OSD)",
        "close_to_tray_chk": "พับเก็บลง System Tray เมื่อกดปุ่มปิด (X)",
        "startup_chk": "เปิดโปรแกรมอัตโนมัติเมื่อเปิดเครื่อง (Run on Startup)",
        "osd_on": "เปิดไมค์ (MIC ACTIVE)",
        "osd_off": "ปิดไมค์ (MIC MUTED)",
        "unknown_mic": "ไม่ทราบชื่อไมค์",
        "tray_open": "เปิดหน้าต่างโปรแกรม",
        "tray_quit": "ปิดโปรแกรม",
        "tray_no_mic": "ไม่พบไมโครโฟนในระบบ",
        "tray_muted_prefix": "[ปิดไมค์]",
        "tray_active_prefix": "[เปิดไมค์]"
    },
    "en": {
        "lang_name": "English",
        "window_title": "Mic Mute Controller",
        "lang_label": "Language:",
        "mic_label": "Microphone (Auto-Update):",
        "status_checking": "Status: Checking...",
        "status_no_mic": "No Microphone Detected",
        "status_muted": "Status: Mic Muted (MUTED)",
        "status_active": "Status: Mic Active (ACTIVE)",
        "hk_frame": " Hotkey Settings ",
        "hk_btn_normal": "Current Key: [ {hotkey} ]  (Click to change)",
        "hk_btn_record": "Listening... Press key combination now (Esc = Cancel)",
        "toggle_btn": "Toggle Mic Mute / Unmute",
        "osd_chk": "Show bottom floating overlay (Floating OSD)",
        "close_to_tray_chk": "Minimize to System Tray when clicking Close (X)",
        "startup_chk": "Run automatically on Windows startup",
        "osd_on": "MIC ACTIVE",
        "osd_off": "MIC MUTED",
        "unknown_mic": "Unknown Microphone",
        "tray_open": "Open Window",
        "tray_quit": "Exit",
        "tray_no_mic": "No Microphone Detected",
        "tray_muted_prefix": "[MUTED]",
        "tray_active_prefix": "[ACTIVE]"
    }
}


class CustomTrayIcon(pystray.Icon):
    def __init__(self, *args, on_left_click=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.on_left_click = on_left_click

    def __call__(self):
        if self.on_left_click:
            self.on_left_click()


class MicControllerApp:
    # --- Initialization & Instance Listener ---
    def __init__(self, root, mutex_handle=None):
        self.root = root
        self.mutex_handle = mutex_handle
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.on_window_close)

        self.devices = []
        self.device_names = []
        self.selected_mic_name = None
        self.current_volume_interface = None
        self.current_hotkey = "ctrl+alt+m"
        self.show_osd = True
        self.close_to_tray = True
        self.current_lang = "th"
        self.translations = {}
        self.lang_codes = []
        self.hotkey_thread_id = None
        self.is_recording = False
        self.pressed_mods = set()
        self.is_running = True
        self.osd_hide_timer = None

        self.icon_active = self.create_mic_icon(muted=False, size=64)
        self.icon_muted = self.create_mic_icon(muted=True, size=64)
        self.icon_nomic = self.create_mic_icon(muted=True, no_mic=True, size=64)

        self.tk_icon_active = ImageTk.PhotoImage(self.icon_active)
        self.tk_icon_muted = ImageTk.PhotoImage(self.icon_muted)
        self.tk_osd_active = ImageTk.PhotoImage(self.create_mic_icon(muted=False, size=36))
        self.tk_osd_muted = ImageTk.PhotoImage(self.create_mic_icon(muted=True, size=36))

        self.root.iconphoto(False, self.tk_icon_active)

        self.load_languages()
        self.load_config()

        comtypes.CoInitialize()
        self.setup_ui()
        self.setup_osd_window()
        self.setup_tray()
        self.apply_language()
        self.refresh_microphones()

        self.restore_event = ctypes.windll.kernel32.CreateEventW(None, False, False, EVENT_NAME)
        threading.Thread(target=self._listen_for_second_instance, daemon=True).start()

        self.root.after(100, lambda: self.register_hotkey(self.current_hotkey))
        self.auto_check_loop()

        if "--startup" in sys.argv:
            self.root.withdraw()

    def _listen_for_second_instance(self):
        kernel32 = ctypes.windll.kernel32
        while self.is_running and self.restore_event:
            res = kernel32.WaitForSingleObject(self.restore_event, 500)
            if res == 0:
                self.show_window()

    # --- Configuration & Language Management ---
    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.current_hotkey = data.get("hotkey", "ctrl+alt+m")
                    self.selected_mic_name = data.get("mic_name", None)
                    self.show_osd = data.get("show_osd", True)
                    self.close_to_tray = data.get("close_to_tray", True)
                    saved_lang = data.get("language", "th")
                    if saved_lang in self.translations:
                        self.current_lang = saved_lang
            except Exception:
                pass

    def save_config(self):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump({
                    "hotkey": self.current_hotkey,
                    "mic_name": self.selected_mic_name,
                    "show_osd": self.show_osd,
                    "close_to_tray": self.close_to_tray,
                    "language": self.current_lang
                }, f, ensure_ascii=False, indent=4)
        except Exception:
            pass

    def load_languages(self):
        needs_save = False
        if not os.path.exists(LANG_FILE):
            self.translations = DEFAULT_TRANSLATIONS.copy()
            needs_save = True
        else:
            try:
                with open(LANG_FILE, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    if isinstance(loaded, dict) and len(loaded) > 0:
                        self.translations = loaded
                        for lang_code, default_dict in DEFAULT_TRANSLATIONS.items():
                            if lang_code in self.translations:
                                for k, v in default_dict.items():
                                    if k not in self.translations[lang_code]:
                                        self.translations[lang_code][k] = v
                                        needs_save = True
                    else:
                        self.translations = DEFAULT_TRANSLATIONS.copy()
                        needs_save = True
            except Exception:
                self.translations = DEFAULT_TRANSLATIONS.copy()

        if needs_save:
            try:
                with open(LANG_FILE, "w", encoding="utf-8") as f:
                    json.dump(self.translations, f, ensure_ascii=False, indent=4)
            except Exception:
                pass

        self.lang_codes = list(self.translations.keys())
        if self.current_lang not in self.translations:
            self.current_lang = self.lang_codes[0] if self.lang_codes else "th"

    def refresh_language_dropdown(self):
        self.load_languages()
        lang_names = [
            self.translations[code].get("lang_name", code.upper())
            for code in self.lang_codes
        ]
        self.lang_combo["values"] = lang_names
        if self.current_lang in self.lang_codes:
            self.lang_combo.current(self.lang_codes.index(self.current_lang))

    def on_language_selected(self, event=None):
        idx = self.lang_combo.current()
        if 0 <= idx < len(self.lang_codes):
            self.current_lang = self.lang_codes[idx]
            self.save_config()
            self.apply_language()

    def apply_language(self):
        self.root.title(self.t("window_title"))
        self.lang_lbl.config(text=self.t("lang_label"))
        self.mic_lbl.config(text=self.t("mic_label"))
        self.hk_frame.config(text=self.t("hk_frame"))

        if self.is_recording:
            self.hotkey_btn.config(text=self.t("hk_btn_record"))
        else:
            self.hotkey_btn.config(text=self.t("hk_btn_normal").format(hotkey=self.current_hotkey.upper()))

        self.toggle_btn.config(text=self.t("toggle_btn"))
        self.osd_chk.config(text=self.t("osd_chk"))
        self.close_to_tray_chk.config(text=self.t("close_to_tray_chk"))
        self.startup_chk.config(text=self.t("startup_chk"))

        if hasattr(self, 'tray_icon') and self.tray_icon:
            try:
                self.tray_icon.menu = self.build_tray_menu()
                self.tray_icon.update_menu()
            except Exception:
                pass

        if not self.device_names:
            self.status_label.config(text=self.t("status_no_mic"), fg="gray")
            self.update_tray_visuals(muted=True, no_mic=True)
        else:
            self.update_status_display()

    def t(self, key):
        lang_dict = self.translations.get(self.current_lang, {})
        if key in lang_dict:
            return lang_dict[key]
        fallback = DEFAULT_TRANSLATIONS.get(self.current_lang, DEFAULT_TRANSLATIONS["th"])
        return fallback.get(key, DEFAULT_TRANSLATIONS["th"].get(key, key))

    # --- UI & Visuals Setup ---
    def create_mic_icon(self, muted=False, no_mic=False, size=64):
        scale = 4
        canvas_size = size * scale
        img = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        if no_mic:
            bg_color = (108, 117, 125, 255)
        elif muted:
            bg_color = (220, 53, 69, 255)
        else:
            bg_color = (40, 167, 69, 255)

        pad = 2 * scale
        draw.ellipse([pad, pad, canvas_size - pad, canvas_size - pad], fill=bg_color)

        white = (255, 255, 255, 255)
        s = canvas_size / 64.0
        draw.rounded_rectangle([int(24*s), int(13*s), int(40*s), int(35*s)], radius=int(8*s), fill=white)
        draw.arc([int(18*s), int(20*s), int(46*s), int(44*s)], start=0, end=180, fill=white, width=int(4*s))
        draw.line([int(32*s), int(44*s), int(32*s), int(51*s)], fill=white, width=int(4*s))
        draw.line([int(23*s), int(51*s), int(41*s), int(51*s)], fill=white, width=int(4*s))

        if muted:
            draw.line([int(14*s), int(14*s), int(50*s), int(50*s)], fill=bg_color, width=int(8*s))
            draw.line([int(14*s), int(14*s), int(50*s), int(50*s)], fill=white, width=int(4*s))

        return img.resize((size, size), Image.Resampling.LANCZOS)

    def setup_ui(self):
        style = ttk.Style()
        style.configure("TCombobox", font=(FONT_FAMILY, 10))
        style.configure("TButton", font=(FONT_FAMILY, 10), padding=5)
        style.configure("TCheckbutton", font=(FONT_FAMILY, 10))
        self.root.option_add('*TCombobox*Listbox.font', (FONT_FAMILY, 10))

        main_frame = tk.Frame(self.root, padx=18, pady=14)
        main_frame.pack(fill="both", expand=True)

        top_bar = tk.Frame(main_frame)
        top_bar.pack(fill="x", pady=(0, 6))

        self.mic_lbl = tk.Label(
            top_bar,
            text=self.t("mic_label"),
            font=(FONT_FAMILY, 10, "bold")
        )
        self.mic_lbl.pack(side="left", anchor="s")

        lang_frame = tk.Frame(top_bar)
        lang_frame.pack(side="right")

        self.lang_lbl = tk.Label(lang_frame, text=self.t("lang_label"), font=(FONT_FAMILY, 9))
        self.lang_lbl.pack(side="left", padx=(0, 4))

        lang_names = [
            self.translations[code].get("lang_name", code.upper())
            for code in self.lang_codes
        ]

        self.lang_combo = ttk.Combobox(
            lang_frame,
            values=lang_names,
            state="readonly",
            width=13,
            font=(FONT_FAMILY, 9),
            postcommand=self.refresh_language_dropdown
        )
        if self.current_lang in self.lang_codes:
            self.lang_combo.current(self.lang_codes.index(self.current_lang))
        else:
            self.lang_combo.current(0)
        self.lang_combo.pack(side="left")
        self.lang_combo.bind("<<ComboboxSelected>>", self.on_language_selected)

        self.mic_combo = ttk.Combobox(
            main_frame,
            state="readonly",
            width=44,
            font=(FONT_FAMILY, 10),
            postcommand=self.refresh_microphones
        )
        self.mic_combo.pack(fill="x", pady=(0, 12))
        self.mic_combo.bind("<<ComboboxSelected>>", self.on_mic_selected)

        self.status_label = tk.Label(
            main_frame,
            text=self.t("status_checking"),
            font=(FONT_FAMILY, 13, "bold")
        )
        self.status_label.pack(pady=(0, 10))

        self.hk_frame = tk.LabelFrame(
            main_frame,
            text=self.t("hk_frame"),
            font=(FONT_FAMILY, 9)
        )
        self.hk_frame.pack(fill="x", pady=(0, 12))

        self.hotkey_btn = tk.Button(
            self.hk_frame,
            text=self.t("hk_btn_normal").format(hotkey=self.current_hotkey.upper()),
            font=(FONT_FAMILY, 10, "bold"),
            bg="#f4f4f4",
            relief="groove",
            pady=6,
            cursor="hand2",
            command=self.start_recording_hotkey
        )
        self.hotkey_btn.pack(fill="x", padx=12, pady=10)

        self.toggle_btn = ttk.Button(
            main_frame,
            text=self.t("toggle_btn"),
            command=self.toggle_mute
        )
        self.toggle_btn.pack(fill="x", pady=(0, 10))

        self.show_osd_var = tk.BooleanVar(value=self.show_osd)
        self.osd_chk = ttk.Checkbutton(
            main_frame,
            text=self.t("osd_chk"),
            variable=self.show_osd_var,
            command=self.on_osd_toggle_changed
        )
        self.osd_chk.pack(anchor="w", pady=(0, 4))

        self.close_to_tray_var = tk.BooleanVar(value=self.close_to_tray)
        self.close_to_tray_chk = ttk.Checkbutton(
            main_frame,
            text=self.t("close_to_tray_chk"),
            variable=self.close_to_tray_var,
            command=self.on_close_to_tray_changed
        )
        self.close_to_tray_chk.pack(anchor="w", pady=(0, 4))

        self.startup_var = tk.BooleanVar(value=self.check_startup_status())
        self.startup_chk = ttk.Checkbutton(
            main_frame,
            text=self.t("startup_chk"),
            variable=self.startup_var,
            command=self.toggle_startup
        )
        self.startup_chk.pack(anchor="w")

    # --- Floating OSD Overlay ---
    def setup_osd_window(self):
        self.osd_win = tk.Toplevel(self.root)
        self.osd_win.withdraw()
        self.osd_win.overrideredirect(True)
        self.osd_win.attributes("-topmost", True)
        self.osd_win.attributes("-alpha", 0.72)

        osd_bg = "#18181c"
        self.osd_inner = tk.Frame(self.osd_win, bg=osd_bg, bd=0, highlightthickness=0, padx=16, pady=10)
        self.osd_inner.pack(fill="both", expand=True)

        self.osd_icon_lbl = tk.Label(self.osd_inner, bg=osd_bg, bd=0, image=self.tk_osd_active)
        self.osd_icon_lbl.pack(side="left", padx=(0, 12))

        text_frame = tk.Frame(self.osd_inner, bg=osd_bg, bd=0)
        text_frame.pack(side="left")

        self.osd_status_lbl = tk.Label(
            text_frame,
            text=self.t("osd_on"),
            font=(FONT_FAMILY, 11, "bold"),
            fg="#51cf66",
            bg=osd_bg,
            anchor="w"
        )
        self.osd_status_lbl.pack(anchor="w")

        self.osd_mic_lbl = tk.Label(
            text_frame,
            text="",
            font=(FONT_FAMILY, 8),
            fg="#d0d0d0",
            bg=osd_bg,
            anchor="w"
        )
        self.osd_mic_lbl.pack(anchor="w")

        self.osd_win.update_idletasks()
        self._apply_click_through(self.osd_win)

    def _apply_click_through(self, window):
        try:
            hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
            if not hwnd:
                hwnd = window.winfo_id()
            GWL_EXSTYLE = -20
            WS_EX_LAYERED = 0x00080000
            WS_EX_TRANSPARENT = 0x00000020
            WS_EX_TOOLWINDOW = 0x00000080
            WS_EX_NOACTIVATE = 0x08000000
            style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            style = style | WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOOLWINDOW | WS_EX_NOACTIVATE
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
        except Exception:
            pass

    def show_osd_popup(self, muted):
        if not self.show_osd_var.get():
            return

        if self.osd_hide_timer:
            self.root.after_cancel(self.osd_hide_timer)
            self.osd_hide_timer = None

        mic_display = self.selected_mic_name or self.t("unknown_mic")
        if len(mic_display) > 38:
            mic_display = mic_display[:35] + "..."

        if muted:
            self.osd_icon_lbl.config(image=self.tk_osd_muted)
            self.osd_status_lbl.config(text=self.t("osd_off"), fg="#ff6b6b")
        else:
            self.osd_icon_lbl.config(image=self.tk_osd_active)
            self.osd_status_lbl.config(text=self.t("osd_on"), fg="#51cf66")

        self.osd_mic_lbl.config(text=mic_display)

        self.osd_win.update_idletasks()
        win_w = self.osd_win.winfo_reqwidth()
        win_h = self.osd_win.winfo_reqheight()
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        pos_x = (screen_w - win_w) // 2
        pos_y = screen_h - win_h - 85
        self.osd_win.geometry(f"{win_w}x{win_h}+{pos_x}+{pos_y}")

        self.osd_win.deiconify()
        self.osd_win.lift()
        self.osd_win.attributes("-topmost", True)
        self._apply_click_through(self.osd_win)

        self.osd_hide_timer = self.root.after(1500, self.osd_win.withdraw)

    def on_osd_toggle_changed(self):
        self.show_osd = self.show_osd_var.get()
        self.save_config()
        if not self.show_osd and hasattr(self, 'osd_win'):
            self.osd_win.withdraw()

    # --- Microphone & Audio Control ---
    def refresh_microphones(self):
        if not self.is_running:
            return
        try:
            enumerator = AudioUtilities.GetDeviceEnumerator()
            collection = enumerator.EnumAudioEndpoints(EDataFlow.eCapture.value, DEVICE_STATE.ACTIVE.value)

            new_devices = []
            new_names = []

            for i in range(collection.GetCount()):
                dev = collection.Item(i)
                wrapper = AudioUtilities.CreateDevice(dev)
                if wrapper:
                    new_devices.append(dev)
                    new_names.append(wrapper.FriendlyName)

            if new_names != self.device_names:
                self.devices = new_devices
                self.device_names = new_names
                self.mic_combo['values'] = self.device_names

                if not self.device_names:
                    self.mic_combo.set('')
                    self.current_volume_interface = None
                    self.status_label.config(text=self.t("status_no_mic"), fg="gray")
                    self.update_tray_visuals(muted=True, no_mic=True)
                else:
                    if self.selected_mic_name in self.device_names:
                        idx = self.device_names.index(self.selected_mic_name)
                    else:
                        idx = 0
                    self.mic_combo.current(idx)
                    self.bind_mic_interface(idx)
        except Exception:
            pass

    def on_mic_selected(self, event=None):
        idx = self.mic_combo.current()
        self.bind_mic_interface(idx)
        self.save_config()

    def bind_mic_interface(self, idx):
        if 0 <= idx < len(self.devices):
            dev = self.devices[idx]
            self.selected_mic_name = self.device_names[idx]
            interface = dev.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            self.current_volume_interface = comtypes.cast(interface, comtypes.POINTER(IAudioEndpointVolume))
            self.update_status_display()

    def update_status_display(self):
        if not self.current_volume_interface:
            return
        try:
            is_muted = bool(self.current_volume_interface.GetMute())
            if is_muted:
                self.status_label.config(text=self.t("status_muted"), fg="#d9534f")
            else:
                self.status_label.config(text=self.t("status_active"), fg="#28a745")
            self.update_tray_visuals(muted=is_muted, no_mic=False)
        except Exception:
            self.refresh_microphones()

    def auto_check_loop(self):
        if not self.is_running:
            return
        self.refresh_microphones()
        self.update_status_display()
        self.root.after(2000, self.auto_check_loop)

    def toggle_mute(self):
        if self.is_recording:
            return
        self.root.after(0, self._execute_toggle_mute)

    def _execute_toggle_mute(self):
        if self.is_recording or not self.current_volume_interface:
            return
        try:
            current_state = self.current_volume_interface.GetMute()
            new_state = 0 if current_state else 1
            self.current_volume_interface.SetMute(new_state, None)
            self.update_status_display()
            self.show_osd_popup(muted=bool(new_state))
        except Exception:
            self.refresh_microphones()

    # --- Hotkey Management ---
    def parse_hotkey_string(self, hotkey_str):
        parts = [p.strip().lower() for p in hotkey_str.split("+") if p.strip()]
        mods = MOD_NOREPEAT
        vk = 0
        for p in parts:
            if p in ("ctrl", "control"):
                mods |= MOD_CONTROL
            elif p in ("alt", "menu"):
                mods |= MOD_ALT
            elif p == "shift":
                mods |= MOD_SHIFT
            elif p in ("win", "windows"):
                mods |= MOD_WIN
            elif p in VK_MAP:
                vk = VK_MAP[p]
            elif len(p) == 1 and p.isalnum():
                vk = ord(p.upper())
        return mods, vk

    def clear_hotkey(self):
        if self.hotkey_thread_id is not None:
            try:
                ctypes.windll.user32.PostThreadMessageW(self.hotkey_thread_id, WM_QUIT, 0, 0)
            except Exception:
                pass
            self.hotkey_thread_id = None

    def register_hotkey(self, hotkey_str):
        self.clear_hotkey()
        mods, vk = self.parse_hotkey_string(hotkey_str)
        if vk == 0:
            return
        threading.Thread(target=self._hotkey_listener_loop, args=(mods, vk), daemon=True).start()

    def _hotkey_listener_loop(self, mods, vk):
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        self.hotkey_thread_id = kernel32.GetCurrentThreadId()

        if not user32.RegisterHotKey(None, HOTKEY_ID, mods, vk):
            return

        msg = wintypes.MSG()
        try:
            while self.is_running and user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
                if msg.message == WM_HOTKEY and msg.wParam == HOTKEY_ID:
                    self.toggle_mute()
                elif msg.message == WM_QUIT:
                    break
        finally:
            user32.UnregisterHotKey(None, HOTKEY_ID)

    def start_recording_hotkey(self):
        if self.is_recording:
            return

        self.is_recording = True
        self.pressed_mods.clear()
        self.clear_hotkey()

        self.hotkey_btn.config(
            text=self.t("hk_btn_record"),
            bg="#fff3cd",
            fg="#856404"
        )

        self.root.bind("<KeyPress>", self._on_tk_key_press)
        self.root.bind("<KeyRelease>", self._on_tk_key_release)
        self.root.focus_force()

    def _on_tk_key_press(self, event):
        if not self.is_recording:
            return

        keysym = event.keysym.lower()
        if keysym == "escape":
            self.finish_recording_hotkey(None)
            return

        if keysym in ("control_l", "control_r"):
            self.pressed_mods.add("ctrl")
            return
        elif keysym in ("alt_l", "alt_r"):
            self.pressed_mods.add("alt")
            return
        elif keysym in ("shift_l", "shift_r"):
            self.pressed_mods.add("shift")
            return
        elif keysym in ("win_l", "win_r", "super_l", "super_r"):
            self.pressed_mods.add("win")
            return

        key_name = None
        if keysym in VK_MAP:
            key_name = keysym
        elif len(keysym) == 1 and keysym.isalnum():
            key_name = keysym

        if key_name:
            ordered_mods = [m for m in ("ctrl", "alt", "shift", "win") if m in self.pressed_mods]
            ordered_mods.append(key_name)
            new_hk = "+".join(ordered_mods)
            self.finish_recording_hotkey(new_hk)

    def _on_tk_key_release(self, event):
        if not self.is_recording:
            return
        keysym = event.keysym.lower()
        if keysym in ("control_l", "control_r"):
            self.pressed_mods.discard("ctrl")
        elif keysym in ("alt_l", "alt_r"):
            self.pressed_mods.discard("alt")
        elif keysym in ("shift_l", "shift_r"):
            self.pressed_mods.discard("shift")
        elif keysym in ("win_l", "win_r", "super_l", "super_r"):
            self.pressed_mods.discard("win")

    def finish_recording_hotkey(self, new_hk):
        self.is_recording = False
        self.root.unbind("<KeyPress>")
        self.root.unbind("<KeyRelease>")

        if new_hk:
            self.current_hotkey = new_hk.lower()
            self.save_config()

        self.register_hotkey(self.current_hotkey)
        self.hotkey_btn.config(
            text=self.t("hk_btn_normal").format(hotkey=self.current_hotkey.upper()),
            bg="#f4f4f4",
            fg="black"
        )

    # --- System Tray & Windows Startup ---
    def build_tray_menu(self):
        return pystray.Menu(
            item(self.t("tray_open"), self.show_window),
            pystray.Menu.SEPARATOR,
            item(self.t("tray_quit"), self.quit_app)
        )

    def setup_tray(self):
        self.tray_icon = CustomTrayIcon(
            "MicMuteController",
            self.icon_active,
            self.t("status_checking"),
            self.build_tray_menu(),
            on_left_click=self.toggle_mute
        )
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def update_tray_visuals(self, muted=False, no_mic=False):
        if not hasattr(self, 'tray_icon') or not self.tray_icon:
            return
        try:
            if no_mic:
                self.tray_icon.icon = self.icon_nomic
                self.tray_icon.title = self.t("tray_no_mic")
            elif muted:
                self.tray_icon.icon = self.icon_muted
                self.root.iconphoto(False, self.tk_icon_muted)
                tooltip = f"{self.t('tray_muted_prefix')} {self.selected_mic_name}"
                self.tray_icon.title = tooltip[:120]
            else:
                self.tray_icon.icon = self.icon_active
                self.root.iconphoto(False, self.tk_icon_active)
                tooltip = f"{self.t('tray_active_prefix')} {self.selected_mic_name}"
                self.tray_icon.title = tooltip[:120]
        except Exception:
            pass

    def check_startup_status(self):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, STARTUP_REG_PATH, 0, winreg.KEY_READ)
            winreg.QueryValueEx(key, APP_REGISTRY_NAME)
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            return False
        except Exception:
            return False

    def toggle_startup(self):
        enable = self.startup_var.get()
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, STARTUP_REG_PATH, 0, winreg.KEY_SET_VALUE)
            if enable:
                if getattr(sys, 'frozen', False):
                    cmd = f'"{sys.executable}" --startup'
                else:
                    cmd = f'"{sys.executable}" "{os.path.abspath(__file__)}" --startup'
                winreg.SetValueEx(key, APP_REGISTRY_NAME, 0, winreg.REG_SZ, cmd)
            else:
                try:
                    winreg.DeleteValue(key, APP_REGISTRY_NAME)
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)
        except Exception:
            pass

    # --- Window Lifecycle & Exit ---
    def on_close_to_tray_changed(self):
        self.close_to_tray = self.close_to_tray_var.get()
        self.save_config()

    def on_window_close(self):
        if self.close_to_tray_var.get():
            self.hide_window()
        else:
            self.quit_app()

    def show_window(self, icon=None, item=None):
        self.root.after(0, self._restore_window)

    def _restore_window(self):
        self.root.deiconify()
        self.root.state("normal")
        self.root.lift()
        self.root.focus_force()

    def hide_window(self):
        self.root.withdraw()

    def quit_app(self, icon=None, item=None):
        self.is_running = False
        self.clear_hotkey()
        try:
            if getattr(self, 'restore_event', None):
                ctypes.windll.kernel32.CloseHandle(self.restore_event)
                self.restore_event = None
        except Exception:
            pass
        try:
            if self.mutex_handle:
                ctypes.windll.kernel32.CloseHandle(self.mutex_handle)
                self.mutex_handle = None
        except Exception:
            pass
        try:
            if self.tray_icon:
                self.tray_icon.stop()
        except Exception:
            pass
        self.root.after(0, self.root.destroy)


# --- Application Entry Point ---
if __name__ == "__main__":
    kernel32 = ctypes.windll.kernel32
    mutex = kernel32.CreateMutexW(None, False, MUTEX_NAME)
    if kernel32.GetLastError() == ERROR_ALREADY_EXISTS:
        evt = kernel32.OpenEventW(EVENT_MODIFY_STATE, False, EVENT_NAME)
        if evt:
            kernel32.SetEvent(evt)
            kernel32.CloseHandle(evt)
        if mutex:
            kernel32.CloseHandle(mutex)
        sys.exit(0)

    root = tk.Tk()
    app = MicControllerApp(root, mutex_handle=mutex)
    root.mainloop()