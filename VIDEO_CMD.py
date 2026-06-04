import sys, os, shutil, tempfile, cv2, yt_dlp, ctypes, time
from PIL import Image

# Функция для принудительного разворота окна на весь экран
def set_fullscreen():
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    ctypes.windll.user32.ShowWindow(hwnd, 3) # 3 = SW_MAXIMIZE
    # Активируем поддержку ANSI-цветов (чтобы не было "кракозябр")
    ctypes.windll.kernel32.SetConsoleMode(ctypes.windll.kernel32.GetStdHandle(-11), 7)

def play_video(url):
    # Разворачиваем окно сразу перед запуском
    set_fullscreen()
    
    temp_file = os.path.join(tempfile.gettempdir(), "video_cmd.mp4")
    
    print(f"\n>>> Загрузка: {url}")
    ydl_opts = {'format': 'best', 'outtmpl': temp_file, 'quiet': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    cap = cv2.VideoCapture(temp_file)
    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    frame_duration = 1.0 / fps

    # Получаем реальные размеры терминала
    cols, lines = shutil.get_terminal_size()
    W, H = cols, lines - 1

    print("\n>>> Воспроизведение... (Нажмите Ctrl+C для выхода)")
    
    try:
        while cap.isOpened():
            start_time = time.time()
            ret, frame = cap.read()
            if not ret: break
            
            # Конвертируем кадр в ASCII-цвета
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).resize((W, H)).convert("RGB")
            pixels = img.load()
            
            # Собираем кадр в одну строку для мгновенной отрисовки
            output = ["\033[H"]
            for y in range(H):
                row = []
                for x in range(W):
                    r, g, b = pixels[x, y]
                    row.append(f"\033[38;2;{r};{g};{b}m@")
                output.append("".join(row) + "\n")
            
            sys.stdout.write("".join(output))
            sys.stdout.flush()
            
            # Синхронизация FPS (чтобы видео не "летело")
            elapsed = time.time() - start_time
            if elapsed < frame_duration:
                time.sleep(frame_duration - elapsed)
                
    finally:
        cap.release()
        if os.path.exists(temp_file): os.remove(temp_file)

if __name__ == "__main__":
    print("=== VIDEO CMD FULLSCREEN ===")
    url = input("Введите ссылку: ").strip()
    play_video(url)