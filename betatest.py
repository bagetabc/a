import sys, os, shutil, tempfile, time, subprocess, importlib.util, threading
import tkinter as tk
from tkinter import ttk

# Установка библиотек
def setup():
    for mod, pkg in {'cv2': 'opencv-python', 'yt_dlp': 'yt-dlp', 'PIL': 'pillow'}.items():
        if importlib.util.find_spec(mod) is None:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
setup()

import cv2, ctypes
from PIL import Image

control = {"pause": False, "forward": False, "stop": False, "speed": 1.0}

def create_gui():
    root = tk.Tk()
    root.title("Video Control")
    root.geometry("250x300")
    root.configure(bg="#2c3e50") # Темный фон
    root.attributes("-topmost", True)

    style = ttk.Style()
    style.configure("TButton", font=("Arial", 10, "bold"), padding=5)

    tk.Label(root, text="УПРАВЛЕНИЕ", bg="#2c3e50", fg="#ecf0f1").pack(pady=5)

    tk.Button(root, text="▶ / ⏸ Пауза", bg="#3498db", fg="white", command=lambda: control.update({"pause": not control["pause"]})).pack(fill="x", padx=10, pady=2)
    tk.Button(root, text="⏩ +10 сек", bg="#e67e22", fg="white", command=lambda: control.update({"forward": True})).pack(fill="x", padx=10, pady=2)
    
    # Регулировка скорости
    tk.Button(root, text="⚡ Ускорить (x1.5)", bg="#27ae60", fg="white", command=lambda: control.update({"speed": min(control["speed"] + 0.5, 3.0)})).pack(fill="x", padx=10, pady=2)
    tk.Button(root, text="🐢 Замедлить", bg="#9b59b6", fg="white", command=lambda: control.update({"speed": max(control["speed"] - 0.5, 0.5)})).pack(fill="x", padx=10, pady=2)
    
    tk.Button(root, text="❌ Выход", bg="#c0392b", fg="white", command=lambda: control.update({"stop": True})).pack(fill="x", padx=10, pady=20)
    
    root.mainloop()

threading.Thread(target=create_gui, daemon=True).start()

def set_console():
    try:
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        ctypes.windll.user32.ShowWindow(hwnd, 3)
        ctypes.windll.kernel32.SetConsoleMode(ctypes.windll.kernel32.GetStdHandle(-11), 7)
    except: pass

def play_video(url):
    set_console()
    temp_file = os.path.join(tempfile.gettempdir(), "video_cmd.mp4")
    try:
        import yt_dlp
        with yt_dlp.YoutubeDL({'format': 'best', 'outtmpl': temp_file}) as ydl: ydl.download([url])
    except: return

    cap = cv2.VideoCapture(temp_file)
    try:
        while cap.isOpened():
            if control["stop"]: break
            if control["pause"]: time.sleep(0.1); continue
            if control["forward"]:
                cap.set(cv2.CAP_PROP_POS_MSEC, cap.get(cv2.CAP_PROP_POS_MSEC) + 10000)
                control["forward"] = False

            ret, frame = cap.read()
            if not ret: break
            
            # Рендеринг
            W, H = 160, 50 
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).resize((W, H)).convert("RGB")
            pixels = img.load()
            
            # Формируем строку и выводим
            out = "\033[H" + "".join(["".join([f"\033[38;2;{pixels[x, y][0]};{pixels[x, y][1]};{pixels[x, y][2]}m@" for x in range(W)]) + "\n" for y in range(H)])
            sys.stdout.write(out)
            sys.stdout.flush()
            
            time.sleep(0.04 / control["speed"]) # Динамическая скорость
    finally:
        cap.release()
        if os.path.exists(temp_file): os.remove(temp_file)
        os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    while True:
        url = input("Введите ссылку (или 'exit'): ").strip().lower()
        if url == "exit": break
        if url: play_video(url)