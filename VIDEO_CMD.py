import sys, os, shutil, tempfile, cv2, yt_dlp, ctypes, time, importlib.util, subprocess
from PIL import Image

# 1. Автоматическая установка зависимостей
def check_and_install():
    dependencies = {'cv2': 'opencv-python', 'yt_dlp': 'yt-dlp', 'PIL': 'pillow'}
    for mod, pkg in dependencies.items():
        if importlib.util.find_spec(mod) is None:
            print(f">>> Установка {pkg}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

check_and_install()

# 2. Настройки окна
def set_console_mode():
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    ctypes.windll.user32.ShowWindow(hwnd, 3)
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

def clear_system():
    os.system('cls' if os.name == 'nt' else 'clear')
    temp_file = os.path.join(tempfile.gettempdir(), "video_cmd.mp4")
    if os.path.exists(temp_file):
        try: os.remove(temp_file)
        except: pass
    print(">>> Система очищена.")

# 3. Основной плеер с настройкой скорости
def play_video(url, speed=1.0):
    set_console_mode()
    temp_file = os.path.join(tempfile.gettempdir(), "video_cmd.mp4")
    
    print(f"\n>>> Загрузка: {url}...")
    ydl_opts = {'format': 'best', 'outtmpl': temp_file}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    cap = cv2.VideoCapture(temp_file)
    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    # Ускорение: делим длительность кадра на коэффициент скорости
    frame_duration = (1.0 / fps) / speed

    try:
        while cap.isOpened():
            start_time = time.time()
            ret, frame = cap.read()
            if not ret: break
            
            W, H = shutil.get_terminal_size()
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).resize((W, H - 1)).convert("RGB")
            pixels = img.load()
            
            output = ["\033[H"] 
            for y in range(H - 1):
                row = [f"\033[38;2;{pixels[x, y][0]};{pixels[x, y][1]};{pixels[x, y][2]}m@" for x in range(W)]
                output.append("".join(row) + "\n")
            
            sys.stdout.write("".join(output))
            sys.stdout.flush()
            
            elapsed = time.time() - start_time
            if elapsed < frame_duration:
                time.sleep(frame_duration - elapsed)
    except KeyboardInterrupt:
        print("\n>>> Выход...")
    finally:
        cap.release()
        if os.path.exists(temp_file): os.remove(temp_file)
        os.system('cls' if os.name == 'nt' else 'clear')

# 4. Меню запуска
if __name__ == "__main__":
    while True:
        print("\n=== VIDEO CMD PLAYER ===")
        choice = input("Введите ссылку на видео или 'clear' для очистки: ").strip().lower()
        
        if choice == "clear":
            clear_system()
        elif choice:
            try:
                spd_input = input("Скорость (1.0 = норм, 2.0 = в 2 раза быстрее): ").strip()
                speed = float(spd_input) if spd_input else 1.0
                play_video(choice, speed)
            except ValueError:
                print(">>> Ошибка скорости, использую 1.0")
                play_video(choice, 1.0)
