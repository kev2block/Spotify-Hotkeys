import customtkinter as ctk
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from pynput import keyboard, mouse
import threading
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw
import sys
import json
import os
import tempfile
import ctypes
import winshell
from win32com.client import Dispatch
import webbrowser
import win32event
import win32api
import winerror

CLIENT_ID = 'SPOTIFY_CLIENT_ID'
CLIENT_SECRET = 'SPOTIFY_CLIENT_SECRET'
REDIRECT_URI = 'http://localhost:8080/callback' # Make sure you use the same REDIRECT_URI in the script and on the Spotify website.

DEFAULT_HOTKEYS = {
    'play_pause_key': '0',
    'skip_key': '9',
    'rewind_key': '8',
    'volume_up_key': '+',
    'volume_down_key': '-'
}

HOTKEYS_FILE = os.path.join(tempfile.gettempdir(), 'hotkeys.json')
AUTOSTART_FILE = 'SpotifyHotkeyApp.lnk'
AUTOSTART_PATH = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup',
                              AUTOSTART_FILE)

SHOW_EVENT_NAME = "Global\\SpotifyHotkeyAppShowEvent"

sp = Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                       client_secret=CLIENT_SECRET,
                                       redirect_uri=REDIRECT_URI,
                                       scope="user-modify-playback-state,user-read-playback-state"))


def get_active_device_id():
    devices = sp.devices()
    if devices['devices']:
        return devices['devices'][0]['id']
    else:
        return None


def play_pause():
    device_id = get_active_device_id()
    if device_id:
        current_playback = sp.current_playback()
        if current_playback and current_playback['is_playing']:
            sp.pause_playback(device_id=device_id)
        else:
            sp.start_playback(device_id=device_id)


def skip_track():
    device_id = get_active_device_id()
    if device_id:
        sp.next_track(device_id=device_id)


def rewind_track():
    device_id = get_active_device_id()
    if device_id:
        sp.previous_track(device_id=device_id)


def volume_up():
    device_id = get_active_device_id()
    if device_id:
        volume = sp.current_playback()['device']['volume_percent']
        sp.volume(volume + 10 if volume <= 90 else 100, device_id=device_id)


def volume_down():
    device_id = get_active_device_id()
    if device_id:
        volume = sp.current_playback()['device']['volume_percent']
        sp.volume(volume - 10 if volume >= 10 else 0, device_id=device_id)


def open_spotify_url(url):
    webbrowser.open(url)


class HotkeyListener:
    def __init__(self, play_pause_key, skip_key, rewind_key, volume_up_key, volume_down_key):
        self.play_pause_key = play_pause_key
        self.skip_key = skip_key
        self.rewind_key = rewind_key
        self.volume_up_key = volume_up_key
        self.volume_down_key = volume_down_key
        self.listener = None
        self.mouse_listener = None

    def on_press(self, key):
        try:
            if hasattr(key, 'char') and key.char == self.play_pause_key:
                threading.Thread(target=play_pause).start()
            elif hasattr(key, 'char') and key.char == self.skip_key:
                threading.Thread(target=skip_track).start()
            elif hasattr(key, 'char') and key.char == self.rewind_key:
                threading.Thread(target=rewind_track).start()
            elif hasattr(key, 'char') and key.char == self.volume_up_key:
                threading.Thread(target=volume_up).start()
            elif hasattr(key, 'char') and key.char == self.volume_down_key:
                threading.Thread(target=volume_down).start()
            elif str(key) == self.play_pause_key:
                threading.Thread(target=play_pause).start()
            elif str(key) == self.skip_key:
                threading.Thread(target=skip_track).start()
            elif str(key) == self.rewind_key:
                threading.Thread(target=rewind_track).start()
            elif str(key) == self.volume_up_key:
                threading.Thread(target=volume_up).start()
            elif str(key) == self.volume_down_key:
                threading.Thread(target=volume_down).start()
        except AttributeError:
            pass

    def on_click(self, x, y, button, pressed):
        if not pressed:
            return
        if str(button) == self.play_pause_key:
            threading.Thread(target=play_pause).start()
        elif str(button) == self.skip_key:
            threading.Thread(target=skip_track).start()
        elif str(button) == self.rewind_key:
            threading.Thread(target=rewind_track).start()
        elif str(button) == self.volume_up_key:
            threading.Thread(target=volume_up).start()
        elif str(button) == self.volume_down_key:
            threading.Thread(target=volume_down).start()

    def start_listener(self):
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.mouse_listener = mouse.Listener(on_click=self.on_click)
        self.listener.start()
        self.mouse_listener.start()


class SpotifyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Spotify Hotkeys")
        self.root.geometry("350x500")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        self.play_pause_key = ctk.StringVar(value='')
        self.skip_key = ctk.StringVar(value='')
        self.rewind_key = ctk.StringVar(value='')
        self.volume_up_key = ctk.StringVar(value='')
        self.volume_down_key = ctk.StringVar(value='')
        self.autostart_var = ctk.BooleanVar(value=self.is_autostart_enabled())

        self.load_hotkeys()

        ctk.CTkLabel(root, text="Spotify Hotkeys", font=("Helvetica", 20, "bold")).pack(pady=20)

        frame = ctk.CTkFrame(root)
        frame.pack(pady=10, padx=20, fill="both", expand=True)

        ctk.CTkLabel(frame, text="Play/Pause Hotkey:", anchor='w').grid(row=0, column=0, padx=10, pady=10)
        play_pause_entry = ctk.CTkEntry(frame, textvariable=self.play_pause_key, width=50, font=("Helvetica", 14),
                                        justify='center')
        play_pause_entry.grid(row=0, column=1, padx=10, pady=10)
        play_pause_entry.bind('<KeyRelease>', self.limit_input)

        ctk.CTkLabel(frame, text="Skip Hotkey:", anchor='w').grid(row=1, column=0, padx=10, pady=10)
        skip_entry = ctk.CTkEntry(frame, textvariable=self.skip_key, width=50, font=("Helvetica", 14), justify='center')
        skip_entry.grid(row=1, column=1, padx=10, pady=10)
        skip_entry.bind('<KeyRelease>', self.limit_input)

        ctk.CTkLabel(frame, text="Rewind Hotkey:", anchor='w').grid(row=2, column=0, padx=10, pady=10)
        rewind_entry = ctk.CTkEntry(frame, textvariable=self.rewind_key, width=50, font=("Helvetica", 14),
                                    justify='center')
        rewind_entry.grid(row=2, column=1, padx=10, pady=10)
        rewind_entry.bind('<KeyRelease>', self.limit_input)

        ctk.CTkLabel(frame, text="Volume Up Hotkey:", anchor='w').grid(row=3, column=0, padx=10, pady=10)
        volume_up_entry = ctk.CTkEntry(frame, textvariable=self.volume_up_key, width=50, font=("Helvetica", 14),
                                       justify='center')
        volume_up_entry.grid(row=3, column=1, padx=10, pady=10)
        volume_up_entry.bind('<KeyRelease>', self.limit_input)

        ctk.CTkLabel(frame, text="Volume Down Hotkey:", anchor='w').grid(row=4, column=0, padx=10, pady=10)
        volume_down_entry = ctk.CTkEntry(frame, textvariable=self.volume_down_key, width=50, font=("Helvetica", 14),
                                         justify='center')
        volume_down_entry.grid(row=4, column=1, padx=10, pady=10)
        volume_down_entry.bind('<KeyRelease>', self.limit_input)

        ctk.CTkCheckBox(root, text="Autostart", variable=self.autostart_var, command=self.toggle_autostart).pack(
            pady=10)
        ctk.CTkButton(root, text="Hide", command=self.hide_window).pack(pady=10)

        self.hotkey_listener = HotkeyListener(
            self.play_pause_key.get(),
            self.skip_key.get(),
            self.rewind_key.get(),
            self.volume_up_key.get(),
            self.volume_down_key.get()
        )
        self.hotkey_listener.start_listener()
        self.play_pause_key.trace_add("write", self.update_hotkeys)
        self.skip_key.trace_add("write", self.update_hotkeys)
        self.rewind_key.trace_add("write", self.update_hotkeys)
        self.volume_up_key.trace_add("write", self.update_hotkeys)
        self.volume_down_key.trace_add("write", self.update_hotkeys)

        self.icon = None
        self.icon_thread = threading.Thread(target=self.create_tray_icon)
        self.icon_thread.daemon = True
        self.icon_thread.start()

        if self.is_autostart_enabled():
            self.hide_window()

        self.show_event = win32event.CreateEvent(None, False, False, SHOW_EVENT_NAME)
        self.check_for_show_event()

    def check_for_show_event(self):
        def poll_event():
            while True:
                win32event.WaitForSingleObject(self.show_event, win32event.INFINITE)
                self.show_window()

        threading.Thread(target=poll_event, daemon=True).start()

    def limit_input(self, event):
        widget = event.widget
        text = widget.get()
        if len(text) > 1:
            widget.delete(0, ctk.END)
            widget.insert(0, text[-1])

    def update_hotkeys(self, *args):
        self.hotkey_listener.play_pause_key = self.play_pause_key.get()
        self.hotkey_listener.skip_key = self.skip_key.get()
        self.hotkey_listener.rewind_key = self.rewind_key.get()
        self.hotkey_listener.volume_up_key = self.volume_up_key.get()
        self.hotkey_listener.volume_down_key = self.volume_down_key.get()
        self.save_hotkeys()

    def is_autostart_enabled(self):
        return os.path.exists(AUTOSTART_PATH)

    def toggle_autostart(self):
        if self.autostart_var.get():
            self.add_to_startup()
        else:
            self.remove_from_startup()

    def add_to_startup(self):
        target = sys.executable
        shortcut = AUTOSTART_PATH
        winshell.CreateShortcut(
            Path=shortcut,
            Target=target,
            Icon=(target, 0),
            Description="Spotify Hotkeys"
        )

    def remove_from_startup(self):
        try:
            os.remove(AUTOSTART_PATH)
        except FileNotFoundError:
            pass

    def hide_window(self):
        self.root.withdraw()
        if self.icon:
            self.icon.visible = True

    def show_window(self, icon=None, item=None):
        self.root.deiconify()
        self.icon.visible = False

    def quit_app(self, icon, item):
        self.icon.stop()
        self.root.destroy()
        sys.exit()

    def create_tray_icon(self):
        image = Image.new('RGB', (64, 64), (0, 128, 0))
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, 64, 64), fill=(0, 128, 0))

        menu = (
            item('Show', self.show_window),
            item('Quit', self.quit_app)
        )

        self.icon = pystray.Icon("Spotify Hotkeys", image, "Spotify Hotkeys", menu)
        self.icon.run()

    def save_hotkeys(self):
        hotkeys = {
            'play_pause_key': self.play_pause_key.get(),
            'skip_key': self.skip_key.get(),
            'rewind_key': self.rewind_key.get(),
            'volume_up_key': self.volume_up_key.get(),
            'volume_down_key': self.volume_down_key.get()
        }
        with open(HOTKEYS_FILE, 'w') as f:
            json.dump(hotkeys, f)

    def load_hotkeys(self):
        if os.path.exists(HOTKEYS_FILE):
            with open(HOTKEYS_FILE, 'r') as f:
                hotkeys = json.load(f)
        else:
            hotkeys = DEFAULT_HOTKEYS

        self.play_pause_key.set(hotkeys.get('play_pause_key', ''))
        self.skip_key.set(hotkeys.get('skip_key', ''))
        self.rewind_key.set(hotkeys.get('rewind_key', ''))
        self.volume_up_key.set(hotkeys.get('volume_up_key', ''))
        self.volume_down_key.set(hotkeys.get('volume_down_key', ''))


if __name__ == "__main__":
    mutex = win32event.CreateMutex(None, False, "SpotifyHotkeyAppMutex")
    if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
        show_event = win32event.OpenEvent(win32event.EVENT_MODIFY_STATE, False, SHOW_EVENT_NAME)
        if show_event:
            win32event.SetEvent(show_event)
        sys.exit(0)

    root = ctk.CTk()
    app = SpotifyApp(root)
    root.mainloop()
