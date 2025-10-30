# core/helpers.py
import os
import pygame
import json
from PIL import Image, ImageTk, ImageSequence, ImageDraw

# ================= Configuration =================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_DIR = os.path.join(BASE_DIR, "img")
JSON_PATH = os.path.join(BASE_DIR, "data/data.json")
USERS_PATH = os.path.join(BASE_DIR, "data/users.json")

# ================= PyGame Configuration =================
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700
HALF_W = WINDOW_WIDTH // 2
FPS = 60

def get_roboto_font(size):
    try:
        ROBOTO_FONT_PATH = os.path.join(BASE_DIR, "font/Roboto/static/Roboto-Medium.ttf")
        return pygame.font.Font(ROBOTO_FONT_PATH, size)
    except:
        try:
            return pygame.font.SysFont("arial", size)
        except:
            return pygame.font.Font(None, size)

def load_game_data_from_json(json_path=JSON_PATH, game_id=1):
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for img in data["images"]:
            if img["id"] == game_id:
                left = img["left_path"]
                right = img["right_path"]
                left_path = os.path.join(IMG_DIR, left.replace("image/", ""))
                right_path = os.path.join(IMG_DIR, right.replace("image/", ""))
                diffs = [(d["x"], d["y"], d["w"], d["h"]) for d in img["differences"]]
                return left_path, right_path, diffs
        raise ValueError(f"Không tìm thấy ảnh với id {game_id}")
    except Exception as e:
        print(f"Lỗi load game data: {e}")
        raise

def safe_load_image(path, size):
    try:
        if not os.path.exists(path):
            print(f"⚠️ File ảnh không tồn tại: {path}")
            raise FileNotFoundError(f"File không tồn tại: {path}")
        img = pygame.image.load(path)
        return pygame.transform.scale(img, size)
    except Exception as e:
        print(f"⚠️ Lỗi load ảnh {path}: {e}")
        surf = pygame.Surface(size)
        surf.fill((50, 50, 50))
        font = get_roboto_font(36)
        text_surface = font.render("Ảnh lỗi!", True, (255, 0, 0))
        text_rect = text_surface.get_rect(center=(size[0]//2, size[1]//2))
        surf.blit(text_surface, text_rect)
        return surf

# core/helpers.py - Cập nhật hàm center_window
def center_window(window, width, height):
    """Center a window on the screen with given width and height."""
    window.update_idletasks()
    
    # Lấy kích thước màn hình
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    # Tính toán vị trí
    x = (screen_width - width) // 2
    y = max(50, (screen_height - height) // 4)  # Đẩy lên cao hơn 1 chút
    
    # Đặt vị trí và kích thước
    window.geometry(f"{width}x{height}+{x}+{y}")