# screens/pygame_screen.py
import pygame
import tkinter as tk
from tkinter import messagebox
import random
import os
import time
import json
import statistics
from PIL import Image, ImageTk
from core.helpers import (
    WINDOW_WIDTH, WINDOW_HEIGHT, HALF_W, FPS,
    IMG_DIR, JSON_PATH, get_roboto_font, safe_load_image,
    load_game_data_from_json
)

class PyGameScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="black")
        
        self.pygame_frame = tk.Frame(self, bg="black")
        self.pygame_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.canvas = tk.Canvas(self.pygame_frame, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        self.running = False
        self.current_level = 1
        self.game_data_loaded = False
        
        self.boxes = []
        self.found = []
        self.zoom_levels = [1.0, 1.5, 2.0]
        self.zoom_index = 0
        self.cam_x, self.cam_y = 0.0, 0.0
        self.dragging = False
        self.last_mouse = (0, 0)
        self.drag_threshold = 5
        self.mouse_down_pos = (0, 0)
        
        # Thêm các biến mới
        self.lives = 3
        self.max_lives = 3
        self.start_time = 0
        self.elapsed_time = 0
        self.game_state = "playing"  # playing, win, lose
        self.hint_used = False  # Biến theo dõi đã sử dụng gợi ý chưa
        
        # Logging/analytics
        self.clicks_total = 0
        self.correct_clicks = 0
        self.wrong_clicks = 0
        self.hints_used_count = 0
        self.play_logs_path = os.path.join(os.path.dirname(JSON_PATH), "play_logs.json")
        self.difficulty_report_path = os.path.join(os.path.dirname(JSON_PATH), "difficulty_report.csv")
        self.completion_processed = False

        self.canvas.bind("<Button-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.canvas.bind("<Button-3>", self.on_right_click)
        
        pygame.init()
        
    def on_show(self):
        self.start_pygame()
        
    def start_pygame(self):
        self.running = True
        self.game_data_loaded = False
        self.load_game_data()
        self.update_game()
        
    def load_game_data(self):
        try:
            left_path, right_path, self.boxes = load_game_data_from_json(JSON_PATH, self.current_level)
            print(f"🎮 Đang load level {self.current_level}")
            
            self.base_left = safe_load_image(left_path, (HALF_W, WINDOW_HEIGHT))
            self.base_right = safe_load_image(right_path, (HALF_W, WINDOW_HEIGHT))
            self.found = [False] * len(self.boxes)
            
            icon_size = 60
            # Chỉ tải biểu tượng gợi ý (idea) và trái tim
            try:
                self.idea = pygame.transform.scale(pygame.image.load(os.path.join(IMG_DIR, "idea.png")), (icon_size, icon_size))
                # Tạo phiên bản mờ cho nút gợi ý đã sử dụng
                self.idea_faded = self.idea.copy()
                self.idea_faded.set_alpha(128)
            except:
                self.idea = pygame.Surface((icon_size, icon_size))
                self.idea.fill((0, 255, 0))
                self.idea_faded = self.idea.copy()
                self.idea_faded.set_alpha(128)
                
            # Tải hình trái tim
            try:
                self.heart_img = pygame.transform.scale(pygame.image.load(os.path.join(IMG_DIR, "heart.png")), (30, 30))
            except:
                self.heart_img = pygame.Surface((30, 30))
                self.heart_img.fill((255, 0, 0))

            # Tải biểu tượng cho nút
            try:
                self.home_icon = pygame.transform.scale(pygame.image.load(os.path.join(IMG_DIR, "menu.png")), (40, 40))
            except:
                self.home_icon = pygame.Surface((40, 40))
                self.home_icon.fill((0, 0, 0))  # Màu đen cho nút home
                
            try:
                self.replay_icon = pygame.transform.scale(pygame.image.load(os.path.join(IMG_DIR, "replay.png")), (40, 40))
            except:
                self.replay_icon = pygame.Surface((40, 40))
                self.replay_icon.fill((0, 0, 0))  # Màu đen cho nút replay
                
            try:
                self.next_icon = pygame.transform.scale(pygame.image.load(os.path.join(IMG_DIR, "next.png")), (40, 40))
            except:
                self.next_icon = pygame.Surface((40, 40))
                self.next_icon.fill((0, 0, 0))  # Màu đen cho nút next

            # Đặt vị trí cho nút gợi ý
            icon_bottom_margin = 50
            self.rect_hint = self.idea.get_rect(bottomright=(WINDOW_WIDTH - 50, WINDOW_HEIGHT - icon_bottom_margin))

            self.roboto_font = get_roboto_font(36)  # Giảm kích thước font
            self.small_font = get_roboto_font(24)  # Font cho thời gian và trái tim
            
            # Reset các biến khi bắt đầu level mới
            self.lives = self.max_lives
            self.start_time = time.time()
            self.elapsed_time = 0
            self.game_state = "playing"
            self.zoom_index = 0
            self.cam_x, self.cam_y = 0.0, 0.0
            self.hint_used = False  # Reset trạng thái gợi ý
            
            # Reset thống kê lượt chơi cho level này
            self.clicks_total = 0
            self.correct_clicks = 0
            self.wrong_clicks = 0
            self.hints_used_count = 0
            self.completion_processed = False

            self.game_data_loaded = True
            
        except Exception as e:
            print(f"❌ Lỗi khi load game: {e}")
            messagebox.showerror("Lỗi", f"Không thể load level {self.current_level}: {str(e)}")
            self.controller.show_frame("MainGame")
    
    def update_game(self):
        if not self.running or not self.game_data_loaded:
            return
            
        try:
            pygame_surface = pygame.Surface((WINDOW_WIDTH - 20, WINDOW_HEIGHT - 20))
            
            z = self.zoom_levels[self.zoom_index]
            max_x = HALF_W * (z - 1)
            max_y = WINDOW_HEIGHT * (z - 1)
            self.cam_x = max(0, min(self.cam_x, max_x))
            self.cam_y = max(0, min(self.cam_y, max_y))

            lw, lh = int(HALF_W * z), int(WINDOW_HEIGHT * z)
            left_zoom = pygame.transform.smoothscale(self.base_left, (lw, lh))
            right_zoom = pygame.transform.smoothscale(self.base_right, (lw, lh))
            view_rect = pygame.Rect(int(self.cam_x), int(self.cam_y), HALF_W, WINDOW_HEIGHT)

            pygame_surface.fill((0, 0, 0))
            pygame_surface.blit(left_zoom, (0, 0), area=view_rect)
            pygame_surface.blit(right_zoom, (HALF_W, 0), area=view_rect)
            
            pygame.draw.rect(pygame_surface, (0, 0, 0), (HALF_W - 2, 0, 4, WINDOW_HEIGHT))
            border_thickness = 6
            pygame.draw.rect(pygame_surface, (0, 0, 0), (0, 0, WINDOW_WIDTH, WINDOW_HEIGHT), border_thickness)

            # Vẽ thời gian ở góc trên bên trái
            if self.game_state == "playing":
                self.elapsed_time = time.time() - self.start_time
            time_str = time.strftime("%M:%S", time.gmtime(self.elapsed_time))
            time_surface = self.small_font.render(time_str, True, (0, 0, 0))
            pygame_surface.blit(time_surface, (20, 20))

            # Vẽ trái tim ở góc trên bên phải (dịch sang trái 20px)
            for i in range(self.max_lives):
                heart_x = WINDOW_WIDTH - 60 - i * 35
                heart_y = 20
                if i < self.lives:
                    pygame_surface.blit(self.heart_img, (heart_x, heart_y))
                else:
                    faded_heart = self.heart_img.copy()
                    faded_heart.set_alpha(100)
                    pygame_surface.blit(faded_heart, (heart_x, heart_y))

            for i, (x, y, w, h) in enumerate(self.boxes):
                if self.found[i]:
                    cx_world = x + w / 2
                    cy_world = y + h / 2
                    cx = (cx_world - self.cam_x) * z
                    cy = (cy_world - self.cam_y) * z
                    r = int(max(w, h) * 0.6 * z)

                    pygame.draw.circle(pygame_surface, (255, 0, 0), (int(cx), int(cy)), r, 3)
                    pygame.draw.circle(pygame_surface, (255, 0, 0), (int(cx + HALF_W), int(cy)), r, 3)

            dot_radius = 8
            dot_gap = 4
            total_height = len(self.boxes) * (dot_radius * 2 + dot_gap)
            start_y = (WINDOW_HEIGHT - total_height) // 2
            bar_width = 16
            bar_height = total_height + 20
            bar_rect = pygame.Rect(HALF_W - bar_width // 2, start_y - 10, bar_width, bar_height)
            pygame.draw.rect(pygame_surface, (0, 0, 0), bar_rect, border_radius=10)
            for i in range(len(self.boxes)):
                cy = start_y + i * (dot_radius * 2 + dot_gap)
                color_fill = (255, 255, 255) if self.found[i] else (80, 80, 80)
                pygame.draw.circle(pygame_surface, color_fill, (HALF_W, cy), dot_radius - 2)
                pygame.draw.circle(pygame_surface, (0, 0, 0), (HALF_W, cy), dot_radius, 2)

            # Vẽ nút gợi ý (mờ nếu đã sử dụng)
            if self.hint_used:
                pygame_surface.blit(self.idea_faded, self.rect_hint)
            else:
                pygame_surface.blit(self.idea, self.rect_hint)

            # Kiểm tra điều kiện thắng
            if all(self.found) and self.game_state == "playing":
                self.game_state = "win"
                # Cập nhật thông tin người dùng khi hoàn thành level
                if self.controller.current_user and not self.completion_processed:
                    user = self.controller.current_user
                    username = user["username"]
                    completed_levels = user.get("completed_levels", [])
                    current_level = user.get("current_level", 1)
                    
                    # Sử dụng display_id thay vì original_id
                    display_id_to_complete = self.display_id if getattr(self, 'display_id', None) else self.current_level
                    
                    # LOGIC MỚI: MỞ KHÓA LEVEL TIẾP THEO
                    new_current_level = current_level
                    
                    # Nếu level hiện tại chưa được hoàn thành
                    if display_id_to_complete not in completed_levels:
                        completed_levels.append(display_id_to_complete)
                        print(f"✅ Thêm level {display_id_to_complete} vào completed_levels")
                        
                        # QUAN TRỌNG: Mở khóa level tiếp theo
                        # Nếu đây là level hiện tại (level cao nhất đã mở), thì mở level tiếp theo
                        if display_id_to_complete == current_level:
                            new_current_level = current_level + 1
                            print(f"✅ Mở khóa level tiếp theo: {new_current_level}")
                    
                    # Cập nhật thống kê
                    stats = user.get("stats", {})
                    stats["games_played"] = stats.get("games_played", 0) + 1
                    
                    best_times = user.get("best_times", {})
                    level_display_id = getattr(self, 'display_id', None)
                    
                    if level_display_id not in best_times or self.elapsed_time < best_times.get(level_display_id, float('inf')):
                        best_times[level_display_id] = self.elapsed_time
                        
                    # Tạo dữ liệu cập nhật
                    updated_data = {
                        "completed_levels": completed_levels,
                        "current_level": new_current_level,
                        "stats": stats,
                        "best_times": best_times 
                    }
                    
                    # Lưu thông tin người dùng
                    success = self.controller.user_manager.update_user(username, updated_data)
                    
                    if success:
                        # Cập nhật thông tin người dùng trong controller
                        user.update(updated_data)
                        print(f"✅ Đã xử lý level {display_id_to_complete}")
                        print(f"✅ Completed levels sau: {completed_levels}")
                        print(f"✅ Current level mới: {new_current_level}")
                    else:
                        print("❌ Lỗi khi cập nhật thông tin người dùng")
                    
                    # Đánh dấu đã xử lý để tránh cập nhật nhiều lần
                    self.completion_processed = True

                    # Ghi log lượt chơi (win)
                    try:
                        final_state = {"game_state": "win", "score": None}
                        self.save_play_log(final_state)
                    except Exception as e:
                        print("Lỗi khi lưu log sau win:", e)

            # Kiểm tra điều kiện thua
            if self.lives <= 0 and self.game_state == "playing":
                self.game_state = "lose"
                # Ghi log lượt chơi (lose)
                try:
                    final_state = {"game_state": "lose", "score": None}
                    self.save_play_log(final_state)
                except Exception as e:
                    print("Lỗi khi lưu log sau lose:", e)

            # Vẽ bảng kết quả nếu trạng thái không phải là playing
            if self.game_state != "playing":
                self.draw_result_screen(pygame_surface)

            pygame_image = pygame.surfarray.array3d(pygame_surface)
            pygame_image = pygame_image.transpose([1, 0, 2])
            pil_image = Image.fromarray(pygame_image)
            tk_image = ImageTk.PhotoImage(pil_image)
            
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor="nw", image=tk_image)
            self.canvas.image = tk_image
            
        except Exception as e:
            print(f"❌ Lỗi khi cập nhật game: {e}")
        
        self.after(1000 // FPS, self.update_game)

    def draw_result_screen(self, surface):
        # Tạo một overlay mờ
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))

        # Kích thước bảng kết quả (giảm chiều cao 20px)
        panel_width, panel_height = 450, 280  # Giảm từ 300 xuống 280
        panel_x = (WINDOW_WIDTH - panel_width) // 2
        panel_y = (WINDOW_HEIGHT - panel_height) // 2
        
        # Vẽ ảnh nền cho bảng kết quả với bo góc
        try:
            # Tải ảnh nền cho bảng kết quả
            result_bg_path = os.path.join(IMG_DIR, "wood_background.png")
            result_bg = pygame.image.load(result_bg_path).convert_alpha()
            result_bg = pygame.transform.smoothscale(result_bg, (panel_width, panel_height))
            
            # Tạo một surface với bo góc
            rounded_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
            # Vẽ hình chữ nhật bo góc
            pygame.draw.rect(rounded_surface, (255, 255, 255), (0, 0, panel_width, panel_height), border_radius=20)
            # Áp dụng mask bo góc lên ảnh nền
            result_bg.blit(rounded_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            
            # Vẽ ảnh nền đã được bo góc
            surface.blit(result_bg, (panel_x, panel_y))
            
            # Vẽ viền đen cho bảng với bo góc 20px
            panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
            pygame.draw.rect(surface, (0, 0, 0), panel_rect, 3, border_radius=20)
            
        except Exception as e:
            print(f"Không thể tải ảnh nền bảng kết quả: {e}")
            # Fallback: vẽ nền trắng nếu không tải được ảnh
            panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
            pygame.draw.rect(surface, (255, 255, 255), panel_rect, border_radius=20)
            pygame.draw.rect(surface, (0, 0, 0), panel_rect, 3, border_radius=20)

        # Tiêu đề - màu đen
        title = "XIN CHÚC MỪNG!" if self.game_state == "win" else "THUA RỒI!"
        title_surface = self.roboto_font.render(title, True, (0, 0, 0))
        surface.blit(title_surface, (WINDOW_WIDTH // 2 - title_surface.get_width() // 2, panel_y + 40))

        # Thời gian - tạo hình vuông bo góc nền trắng số đen
        time_str = f"TG    {time.strftime('%M:%S', time.gmtime(self.elapsed_time))}"
        time_surface = self.small_font.render(time_str, True, (0, 0, 0))
        
        # Tính kích thước cho khung thời gian
        time_bg_width = time_surface.get_width() + 30
        time_bg_height = time_surface.get_height() + 15
        time_bg_x = WINDOW_WIDTH // 2 - time_bg_width // 2
        time_bg_y = panel_y + 100
        
        # Vẽ khung nền trắng bo góc cho thời gian
        time_bg_rect = pygame.Rect(time_bg_x, time_bg_y, time_bg_width, time_bg_height)
        pygame.draw.rect(surface, (255, 255, 255), time_bg_rect, border_radius=10)
        pygame.draw.rect(surface, (0, 0, 0), time_bg_rect, 2, border_radius=10)
        
        # Vẽ text thời gian lên trên khung
        surface.blit(time_surface, (WINDOW_WIDTH // 2 - time_surface.get_width() // 2, time_bg_y + (time_bg_height - time_surface.get_height()) // 2))

        # Vẽ các nút hình tròn với viền đen và nền trắng
        button_radius = 35
        button_y = panel_y + 210
        button_spacing = 80

        if self.game_state == "win":
            # Tính vị trí để 3 nút nằm giữa
            total_width = 2 * button_radius * 3 + button_spacing * 2
            start_x = WINDOW_WIDTH // 2 - total_width // 2 + button_radius

            # Nút Menu (Home) - hình tròn với viền đen, nền trắng
            home_center = (start_x, button_y)
            pygame.draw.circle(surface, (255, 255, 255), home_center, button_radius)  # Nền trắng
            pygame.draw.circle(surface, (0, 0, 0), home_center, button_radius, 2)  # Viền đen
            surface.blit(self.home_icon, (home_center[0] - self.home_icon.get_width() // 2, home_center[1] - self.home_icon.get_height() // 2))
            self.menu_button_rect = pygame.Rect(home_center[0] - button_radius, home_center[1] - button_radius, button_radius * 2, button_radius * 2)

            # Nút Chơi lại (Replay) - hình tròn với viền đen, nền trắng
            replay_center = (start_x + button_radius * 2 + button_spacing, button_y)
            pygame.draw.circle(surface, (255, 255, 255), replay_center, button_radius)
            pygame.draw.circle(surface, (0, 0, 0), replay_center, button_radius, 2)
            surface.blit(self.replay_icon, (replay_center[0] - self.replay_icon.get_width() // 2, replay_center[1] - self.replay_icon.get_height() // 2))
            self.replay_button_rect = pygame.Rect(replay_center[0] - button_radius, replay_center[1] - button_radius, button_radius * 2, button_radius * 2)

            # Nút Level tiếp theo (Next) - hình tròn với viền đen, nền trắng
            next_center = (start_x + 2 * (button_radius * 2 + button_spacing), button_y)
            pygame.draw.circle(surface, (255, 255, 255), next_center, button_radius)
            pygame.draw.circle(surface, (0, 0, 0), next_center, button_radius, 2)
            surface.blit(self.next_icon, (next_center[0] - self.next_icon.get_width() // 2, next_center[1] - self.next_icon.get_height() // 2))
            self.next_button_rect = pygame.Rect(next_center[0] - button_radius, next_center[1] - button_radius, button_radius * 2, button_radius * 2)

        else:  # lose
            # Tính vị trí để 2 nút nằm giữa
            total_width = 2 * button_radius * 2 + button_spacing
            start_x = WINDOW_WIDTH // 2 - total_width // 2 + button_radius

            # Nút Chơi lại (Replay) - hình tròn với viền đen, nền trắng
            replay_center = (start_x, button_y)
            pygame.draw.circle(surface, (255, 255, 255), replay_center, button_radius)
            pygame.draw.circle(surface, (0, 0, 0), replay_center, button_radius, 2)
            surface.blit(self.replay_icon, (replay_center[0] - self.replay_icon.get_width() // 2, replay_center[1] - self.replay_icon.get_height() // 2))
            self.replay_button_rect = pygame.Rect(replay_center[0] - button_radius, replay_center[1] - button_radius, button_radius * 2, button_radius * 2)

            # Nút Menu (Home) - hình tròn với viền đen, nền trắng
            home_center = (start_x + button_radius * 2 + button_spacing, button_y)
            pygame.draw.circle(surface, (255, 255, 255), home_center, button_radius)
            pygame.draw.circle(surface, (0, 0, 0), home_center, button_radius, 2)
            surface.blit(self.home_icon, (home_center[0] - self.home_icon.get_width() // 2, home_center[1] - self.home_icon.get_height() // 2))
            self.menu_button_rect = pygame.Rect(home_center[0] - button_radius, home_center[1] - button_radius, button_radius * 2, button_radius * 2)
    
    def on_mouse_down(self, event):
        self.mouse_down_pos = (event.x, event.y)
        self.last_mouse = (event.x, event.y)
        self.dragging = False
        
    def on_mouse_move(self, event):
        if not self.dragging and (
            abs(event.x - self.mouse_down_pos[0]) > self.drag_threshold
            or abs(event.y - self.mouse_down_pos[1]) > self.drag_threshold
        ):
            self.dragging = True

        if self.dragging:
            dx, dy = event.x - self.last_mouse[0], event.y - self.last_mouse[1]
            z = self.zoom_levels[self.zoom_index]
            self.cam_x -= dx / z
            self.cam_y -= dy / z

        self.last_mouse = (event.x, event.y)
        
    def on_mouse_up(self, event):
        if not self.dragging:
            mx, my = event.x, event.y
            
            if self.game_state == "playing":
                # Kiểm tra nút gợi ý (chỉ hoạt động nếu chưa sử dụng)
                if (self.rect_hint.x <= mx <= self.rect_hint.x + self.rect_hint.width and 
                    self.rect_hint.y <= my <= self.rect_hint.y + self.rect_hint.height and
                    not self.hint_used):
                    not_found = [i for i, f in enumerate(self.found) if not f]
                    if not_found:
                        self.found[random.choice(not_found)] = True
                        self.hint_used = True  # Đánh dấu đã sử dụng gợi ý
                        self.hints_used_count += 1
                else:
                    # Kiểm tra chọn điểm khác biệt
                    z = self.zoom_levels[self.zoom_index]

                    if mx < HALF_W:
                        world_x = self.cam_x + mx / z
                    else:
                        world_x = self.cam_x + (mx - HALF_W) / z
                    world_y = self.cam_y + my / z

                    found_one = False
                    for i, (x, y, w, h) in enumerate(self.boxes):
                        if not self.found[i]:
                            if x <= world_x <= x + w and y <= world_y <= y + h:
                                self.found[i] = True
                                found_one = True
                                self.correct_clicks += 1
                                break

                    # Luôn tăng tổng click
                    self.clicks_total += 1

                    # Nếu chọn sai thì trừ một mạng
                    if not found_one:
                        self.wrong_clicks += 1
                        self.lives -= 1
                        # Nếu hết mạng thì chuyển sang trạng thái thua
                        if self.lives <= 0:
                            self.game_state = "lose"

            else:  # Trạng thái kết quả
                if self.game_state == "win":
                    if hasattr(self, 'menu_button_rect') and self.menu_button_rect.collidepoint(mx, my):
                        self.running = False
                        self.controller.show_frame("MainGame")
                    elif hasattr(self, 'replay_button_rect') and self.replay_button_rect.collidepoint(mx, my):
                        self.restart_level()
                    elif hasattr(self, 'next_button_rect') and self.next_button_rect.collidepoint(mx, my):
                        self.next_level()
                else:  # lose
                    if hasattr(self, 'replay_button_rect') and self.replay_button_rect.collidepoint(mx, my):
                        self.restart_level()
                    elif hasattr(self, 'menu_button_rect') and self.menu_button_rect.collidepoint(mx, my):
                        self.running = False
                        self.controller.show_frame("MainGame")

        self.dragging = False
        
    def on_right_click(self, event):
        self.cam_x, self.cam_y = 0.0, 0.0

    def restart_level(self):
        # Reset level hiện tại
        self.load_game_data()

    def next_level(self):
        # Chuyển đến level tiếp theo (theo display_id)
        user = self.controller.current_user
        current_display_level = user.get("current_level", 1)
        # Tìm original_id của level tiếp theo
        next_display_id = current_display_level
        if getattr(self, 'display_id', None) == current_display_level - 1:  # Nếu vừa hoàn thành level hiện tại
            next_display_id = current_display_level
        else:
            next_display_id = getattr(self, 'display_id', 0) + 1

        # Tìm original_id tương ứng với next_display_id
        next_original_id = None
        for disp_id, orig_id in self.controller.display_to_original_mapping.items():
            if disp_id == next_display_id:
                next_original_id = orig_id
                break

        if next_original_id is not None:
            self.current_level = next_original_id
            self.display_id = next_display_id
            self.restart_level()
        else:
            # Nếu không có level tiếp theo, quay về menu
            self.running = False
            self.controller.show_frame("MainGame")

    def start_level(self, original_id, display_id=None):
        self.current_level = original_id
        self.display_id = display_id
        
        # Reset completion_processed khi bắt đầu level mới
        self.completion_processed = False
        self.controller.show_frame("PyGameScreen")

    def compute_level_features_and_difficulty(self):
        """Sử dụng DifficultyAnalyzer mới"""
        from core.difficulty_analyzer import DifficultyAnalyzer
        analyzer = DifficultyAnalyzer(JSON_PATH)
        
        # Tìm level hiện tại
        for img in analyzer.images:
            if img.get('id') == self.current_level:
                differences = img.get('differences', [])
                analysis = analyzer.calculate_comprehensive_difficulty(differences)
                
                # Đảm bảo format tương thích với code cũ
                features = {
                    'image_id': self.current_level,
                    'n_diffs': len(differences),
                    'mean_area': 0,  # Có thể tính toán thực tế nếu cần
                    'inv_mean': 0,
                    'n_norm': analysis['factors']['count_factor'],
                    'inv_mean_norm': analysis['factors']['size_factor'],
                    'difficulty_score': analysis['total_score'],
                    'difficulty_level': analysis['level'],
                    'detailed_factors': analysis['factors']
                }
                return features
        
        return {}  # Fallback

    def save_play_log(self, final_state):
        """
        Lưu log lượt chơi hiện tại vào play_logs.json (append)
        final_state: dict chứa thông tin kết quả (win/lose)
        """
        try:
            log_entry = {
                "username": self.controller.current_user.get("username") if self.controller.current_user else None,
                "original_id": self.current_level,
                "display_id": getattr(self, "display_id", None),
                "start_time": self.start_time,
                "end_time": time.time(),
                "elapsed_time": self.elapsed_time,
                "clicks_total": self.clicks_total,
                "correct_clicks": self.correct_clicks,
                "wrong_clicks": self.wrong_clicks,
                "hints_used": self.hints_used_count,
                "lives_left": self.lives,
                "game_state": final_state.get("game_state"),
                "score": final_state.get("score"),
                "features": self.compute_level_features_and_difficulty()
            }

            # Đọc file hiện có, append
            logs = []
            if os.path.exists(self.play_logs_path):
                try:
                    with open(self.play_logs_path, 'r', encoding='utf-8') as f:
                        logs = json.load(f)
                except Exception:
                    logs = []
            logs.append(log_entry)
            with open(self.play_logs_path, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2, ensure_ascii=False)

            # Cập nhật best_times cho người chơi nếu hoàn thành level
            if (self.controller.current_user and 
                final_state.get("game_state") == "win" and 
                hasattr(self, 'display_id')):
                
                user = self.controller.current_user
                username = user["username"]
                display_id = self.display_id
                
                # Lấy best_times hiện tại
                best_times = user.get("best_times", {})
                current_best = best_times.get(str(display_id), float('inf'))
                
                # Cập nhật nếu thời gian hiện tại tốt hơn
                if self.elapsed_time < current_best:
                    best_times[str(display_id)] = self.elapsed_time
                    
                    # Cập nhật thông tin người dùng
                    updated_data = {"best_times": best_times}
                    success = self.controller.user_manager.update_user(username, updated_data)
                    
                    if success:
                        user.update(updated_data)
                        print(f"✅ Đã cập nhật best_time cho level {display_id}: {self.elapsed_time:.2f}s")

            print(f"✅ Play log saved -> {self.play_logs_path}")

        except Exception as e:
            print(f"❌ Lỗi khi lưu play log: {e}")