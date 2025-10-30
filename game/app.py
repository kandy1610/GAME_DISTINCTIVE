# app.py
import tkinter as tk
import pygame
import os
from core.helpers import center_window, BASE_DIR
from core.user_manager import UserManager
from screens.login_screen import LoginScreen
from screens.loading_screen import LoadingScreen2
from screens.main_game import MainGame
from screens.pygame_screen import PyGameScreen

class GameApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DISTINCTIVE")
        
        # Lấy kích thước màn hình
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Tính toán vị trí để căn giữa
        window_width = 1200
        window_height = 700
        
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # Đặt vị trí và kích thước cửa sổ - ĐẨY LÊN CAO HƠN 1 CHÚT
        y_offset = max(0, (screen_height - window_height) // 4)  # Đẩy lên 1/4 khoảng cách thừa
        self.geometry(f"{window_width}x{window_height}+{x}+{y_offset}")
        
        self.resizable(False, False)
        
        self.user_manager = UserManager()
        self.current_user = None
        
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        self._global_images = []
        self.frames = {}
        
        for F in (LoginScreen, LoadingScreen2, MainGame, PyGameScreen):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame("LoginScreen")

        pygame.mixer.init()
        self.background_music = os.path.join(BASE_DIR, "gaming-game-minecraft-background-music-387000.mp3")
        self.music_playing = True
        self.play_music()

        # Đảm bảo cửa sổ được căn giữa sau khi hiển thị
        self.after(100, self.final_center)

    def final_center(self):
        """Căn giữa lần cuối sau khi cửa sổ đã hiển thị"""
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = self.winfo_width()
        window_height = self.winfo_height()
        
        x = (screen_width - window_width) // 2
        y = max(50, (screen_height - window_height) // 4)  # Đảm bảo không quá sát đỉnh
        
        self.geometry(f"+{x}+{y}")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
        if hasattr(frame, 'on_show'):
            frame.on_show()
            
    def play_music(self):
        if os.path.exists(self.background_music):
            try:
                pygame.mixer.music.load(self.background_music)
                pygame.mixer.music.play(-1)
            except Exception as e:
                print("Lỗi khi phát nhạc:", e)
        else:
            print("⚠️ File nhạc nền không tồn tại!")
            
    def toggle_music(self):
        if self.music_playing:
            pygame.mixer.music.pause()
            self.music_playing = False
        else:
            pygame.mixer.music.unpause()
            self.music_playing = True
            
    def on_closing(self):
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        self.destroy()

if __name__ == "__main__":
    app = GameApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()