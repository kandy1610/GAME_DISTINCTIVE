# screens/main_game.py
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageSequence, ImageDraw
import json
import os
from core.helpers import IMG_DIR, JSON_PATH

class MainGame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="white")
        
        self._icon_images = []
        self.gif_frames = []
        self.gif_index = 0
        self.images = []
        self.display_to_original_mapping = {}
        self.is_ranking_visible = False  # Trạng thái hiển thị bảng xếp hạng
        
        self.create_layout()

    def create_layout(self):
        # Giữ nguyên khung ảnh GIF bên trái với nền đen
        self.left_frame = tk.Frame(self, bg="black", width=300, height=700)
        self.left_frame.pack(side="left", fill="y")
        self.left_frame.pack_propagate(False)

        self.gif_label = tk.Label(self.left_frame, bg="black")
        self.gif_label.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        # Đổi overlay frame thành trắng có viền
        self.overlay_frame = tk.Frame(self.left_frame, bg="white", highlightthickness=1, 
                                    highlightbackground="#e0e0e0", bd=1, relief="solid")
        self.overlay_frame.place(relx=0.5, rely=0.1, anchor="n")

        # Đổi màu chữ sang đen cho phù hợp với nền trắng
        self.user_label = tk.Label(self.overlay_frame, text="",
                                fg="black", bg="white", font=("Arial", 16, "bold"))
        self.user_label.pack(pady=10)

        self.level_label = tk.Label(self.overlay_frame, text="",
                                fg="#1e88e5", bg="white", font=("Arial", 12))  # Màu xanh dương
        self.level_label.pack(pady=5)

        self.stats_label = tk.Label(self.overlay_frame, text="",
                                fg="black", bg="white", font=("Arial", 12))
        self.stats_label.pack(pady=5)

        self.logout_button = tk.Button(
            self.overlay_frame,
            text="Logout",
            font=("Arial", 10),
            bg="#f44336",
            fg="white",
            bd=0,
            command=self.logout
        )
        self.logout_button.pack(pady=10)

        # Đổi bảng xếp hạng thành trắng có viền
        self.ranking_frame = tk.Frame(self.left_frame, bg="white", bd=1, 
                                    relief="solid", highlightbackground="#e0e0e0")
        self.ranking_frame.place(relx=0.5, rely=0.45, anchor="n", width=250, height=240)

        # Tiêu đề bảng xếp hạng - đổi màu chữ
        ranking_title = tk.Label(
            self.ranking_frame,
            text="🏆 BẢNG XẾP HẠNG",
            fg="#ff9800",  # Màu cam
            bg="white",
            font=("Arial", 12, "bold")
        )
        ranking_title.pack(pady=5)

        # Đổi background canvas sang trắng
        self.ranking_canvas = tk.Canvas(
            self.ranking_frame,
            bg="white",
            highlightthickness=0,
            height=190
        )
        self.ranking_canvas.pack(fill="both", expand=True, padx=5, pady=5)

        # Tạo scrollbar cho bảng xếp hạng
        ranking_scrollbar = ttk.Scrollbar(
            self.ranking_frame,
            orient="vertical",
            command=self.ranking_canvas.yview
        )
        ranking_scrollbar.pack(side="right", fill="y")

        self.ranking_canvas.configure(yscrollcommand=ranking_scrollbar.set)

        # Frame chứa nội dung bảng xếp hạng - đổi sang nền trắng
        self.ranking_content = tk.Frame(self.ranking_canvas, bg="white")
        self.ranking_canvas_window = self.ranking_canvas.create_window((0, 0), window=self.ranking_content, anchor="nw")

        # Thêm sự kiện cuộn chuột cho canvas
        self.ranking_canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.ranking_content.bind("<MouseWheel>", self._on_mousewheel)

        # Cập nhật scrollregion khi nội dung thay đổi
        def configure_canvas(event):
            self.ranking_canvas.configure(scrollregion=self.ranking_canvas.bbox("all"))
            # Giữ cho chiều rộng của ranking_content bằng với canvas
            self.ranking_canvas.itemconfig(self.ranking_canvas_window, width=self.ranking_canvas.winfo_width())
        
        self.ranking_content.bind("<Configure>", configure_canvas)

        # Tạo nút hình tròn cho ranking và settings
        self.create_circular_buttons()

        self.right_frame = tk.Frame(self, bg="white")
        self.right_frame.pack(side="right", fill="both", expand=True)

    def create_circular_icon(self, icon_path, size=30):
        try:
            # Mở ảnh và chuyển đổi sang RGBA
            icon = Image.open(icon_path).convert("RGBA")
            
            # Resize ảnh thành hình vuông
            icon = icon.resize((size, size), Image.Resampling.LANCZOS)
            
            # TRẢ VỀ ẢNH VUÔNG BÌNH THƯỜNG - KHÔNG BO TRÒN
            return ImageTk.PhotoImage(icon)
        except Exception as e:
            print(f"Không thể tạo icon từ {icon_path}: {e}")
            return None

    def create_circular_buttons(self):
        button_size = 50  # Kích thước nút
        
        # Tạo nút ranking hình VUÔNG
        self.ranking_button_canvas = tk.Canvas(
            self.left_frame, 
            width=button_size, 
            height=button_size, 
            bg="black",
            highlightthickness=0
        )
        self.ranking_button_canvas.place(relx=0.3, rely=0.9, anchor="sw")
        
        # Vẽ nút ranking hình VUÔNG - SỬA create_oval THÀNH create_rectangle
        self.ranking_button_canvas.create_rectangle(
            2, 2, button_size-2, button_size-2,
            fill="#4caf50",
            outline="#388e3c",
            width=2
        )
        
        # Tạo và hiển thị icon ranking
        ranking_icon_path = os.path.join(IMG_DIR, "icons8-award-96.png")
        ranking_icon = self.create_circular_icon(ranking_icon_path, 30)
        
        if ranking_icon:
            self.ranking_icon_tk = ranking_icon
            self.ranking_button_canvas.create_image(
                button_size//2, 
                button_size//2,
                image=self.ranking_icon_tk
            )
        else:
            # Fallback: sử dụng text
            self.ranking_button_canvas.create_text(
                button_size//2, 
                button_size//2,
                text="🏆",
                font=("Arial", 16),
                fill="white"
            )
        
        # Thêm sự kiện click
        self.ranking_button_canvas.bind("<Button-1>", lambda e: self.toggle_ranking())
        self.ranking_button_canvas.bind("<Enter>", lambda e: self.ranking_button_canvas.config(cursor="hand2"))
        self.ranking_button_canvas.bind("<Leave>", lambda e: self.ranking_button_canvas.config(cursor=""))

        # Tạo nút settings hình VUÔNG
        self.settings_button_canvas = tk.Canvas(
            self.left_frame, 
            width=button_size, 
            height=button_size, 
            bg="black",
            highlightthickness=0
        )
        self.settings_button_canvas.place(relx=0.1, rely=0.9, anchor="sw")
        
        # Vẽ nút settings hình VUÔNG - SỬA create_oval THÀNH create_rectangle
        self.settings_button_canvas.create_rectangle(
            2, 2, button_size-2, button_size-2,
            fill="#2196f3",
            outline="#1976d2",
            width=2
        )
        
        # Tạo và hiển thị icon settings
        settings_icon_path = os.path.join(IMG_DIR, "icons8-setting-94.png")
        settings_icon = self.create_circular_icon(settings_icon_path, 30)
        
        if settings_icon:
            self.settings_icon_tk = settings_icon
            self.settings_button_canvas.create_image(
                button_size//2, 
                button_size//2,
                image=self.settings_icon_tk
            )
        else:
            # Fallback: sử dụng text
            self.settings_button_canvas.create_text(
                button_size//2, 
                button_size//2,
                text="⚙️",
                font=("Arial", 16),
                fill="white"
            )
        
        # Thêm sự kiện click
        self.settings_button_canvas.bind("<Button-1>", lambda e: self.controller.toggle_music())
        self.settings_button_canvas.bind("<Enter>", lambda e: self.settings_button_canvas.config(cursor="hand2"))
        self.settings_button_canvas.bind("<Leave>", lambda e: self.settings_button_canvas.config(cursor=""))

    def _on_mousewheel(self, event):
        """Xử lý sự kiện cuộn chuột cho bảng xếp hạng"""
        self.ranking_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def toggle_ranking(self):
        """Chuyển đổi trạng thái ẩn/hiện của bảng xếp hạng"""
        if self.is_ranking_visible:
            self.ranking_frame.place_forget()  # Ẩn bảng xếp hạng
            self.is_ranking_visible = False
        else:
            self.ranking_frame.place(relx=0.5, rely=0.45, anchor="n", width=250, height=240)  # Hiện bảng xếp hạng
            self.is_ranking_visible = True

    def logout(self):
        self.controller.current_user = None
        self.controller.show_frame("LoginScreen")

    def show_full_ranking(self):
        """Show full ranking board with player statistics"""
        ranking_window = tk.Toplevel(self)
        ranking_window.title("Bảng Xếp Hạng Đầy Đủ")
        ranking_window.geometry("800x600")
        ranking_window.configure(bg="white")
        ranking_window.resizable(False, False)
        
        # Center the window
        ranking_window.transient(self)
        ranking_window.grab_set()
        
        # Title
        title_label = tk.Label(
            ranking_window,
            text="BẢNG XẾP HẠNG ĐẦY ĐỦ",
            font=("Arial", 24, "bold"),
            fg="#2c3e50",
            bg="white"
        )
        title_label.pack(pady=20)
        
        # Create frame for table
        table_frame = tk.Frame(ranking_window, bg="white")
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Create treeview for ranking table
        columns = ("rank", "player", "level", "time")
        tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=15,
            style="Custom.Treeview"
        )
        
        # Define headings
        tree.heading("rank", text="STT")
        tree.heading("player", text="Tên Người Chơi")
        tree.heading("level", text="Level Cao Nhất")
        tree.heading("time", text="Thời Gian Hoàn Thành")
        
        # Define columns
        tree.column("rank", width=80, anchor="center")
        tree.column("player", width=200, anchor="center")
        tree.column("level", width=150, anchor="center")
        tree.column("time", width=200, anchor="center")
        
        # Create scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack tree and scrollbar
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Get ranking data
        ranking_data = self.get_ranking_data()
        
        # Insert data into treeview
        for i, (username, highest_level, completion_time) in enumerate(ranking_data, 1):
            time_str = self.format_time(completion_time) if completion_time > 0 else "Chưa hoàn thành"
            tree.insert("", "end", values=(i, username, f"Level {highest_level}", time_str))
        
        # Style the treeview
        style = ttk.Style()
        style.configure("Custom.Treeview", 
                    font=("Arial", 12),
                    rowheight=30,
                    background="white",
                    fieldbackground="white")
        style.configure("Custom.Treeview.Heading",
                    font=("Arial", 12, "bold"),
                    background="#3498db",
                    foreground="white")
        
        # Close button
        close_button = tk.Button(
            ranking_window,
            text="Đóng",
            font=("Arial", 12, "bold"),
            bg="#e74c3c",
            fg="white",
            width=15,
            height=1,
            command=ranking_window.destroy
        )
        close_button.pack(pady=20)

    def update_mini_ranking(self):
        """Cập nhật bảng xếp hạng nhỏ"""
        # Xóa nội dung cũ
        for widget in self.ranking_content.winfo_children():
            widget.destroy()

        # Lấy dữ liệu xếp hạng
        ranking_data = self.get_ranking_data()
        
        # Tạo header
        header_frame = tk.Frame(self.ranking_content, bg="white")
        header_frame.pack(fill="x", pady=(0, 5))
        
        # Đổi màu chữ header
        tk.Label(header_frame, text="#", fg="#ff9800", bg="white", 
                font=("Arial", 9, "bold"), width=3).pack(side="left")
        tk.Label(header_frame, text="Tên", fg="#ff9800", bg="white", 
                font=("Arial", 9, "bold"), width=8).pack(side="left")
        tk.Label(header_frame, text="Level", fg="#ff9800", bg="white", 
                font=("Arial", 9, "bold"), width=6).pack(side="left")
        tk.Label(header_frame, text="Thời gian", fg="#ff9800", bg="white", 
                font=("Arial", 9, "bold"), width=8).pack(side="left")

        # CHỈ HIỂN THỊ TOP 6 NGƯỜI CHƠI
        display_count = min(6, len(ranking_data))
        for i in range(display_count):
            username, highest_level, completion_time = ranking_data[i]
            player_frame = tk.Frame(self.ranking_content, bg="white")
            player_frame.pack(fill="x", pady=2)

            # STT
            rank_color = "#ffd700" if i == 0 else "#c0c0c0" if i == 1 else "#cd7f32" if i == 2 else "#333333"
            tk.Label(player_frame, text=str(i + 1), fg=rank_color, bg="white", 
                    font=("Arial", 8, "bold"), width=3).pack(side="left")
            
            # Tên người chơi (rút gọn nếu quá dài)
            display_name = username if len(username) <= 6 else username[:5] + "…"
            name_color = "#ffd700" if i == 0 else "#c0c0c0" if i == 1 else "#cd7f32" if i == 2 else "#333333"
            tk.Label(player_frame, text=display_name, fg=name_color, bg="white", 
                    font=("Arial", 8, "bold"), width=8, anchor="w").pack(side="left")
            
            # Level cao nhất
            level_text = f"Lv {highest_level}" if highest_level > 0 else "Lv 0"
            level_color = "#2196f3"
            tk.Label(player_frame, text=level_text, fg=level_color, bg="white", 
                    font=("Arial", 8), width=6).pack(side="left")
            
            # Thời gian
            time_text = self.format_time(completion_time) if completion_time > 0 else "--:--"
            time_color = "#4caf50"
            tk.Label(player_frame, text=time_text, fg=time_color, bg="white", 
                    font=("Arial", 8), width=8).pack(side="left")

        # HIỂN THỊ "..." CHO VỊ TRÍ THỨ 7 TRỞ ĐI
        if len(ranking_data) > 6:
            player_frame = tk.Frame(self.ranking_content, bg="white")
            player_frame.pack(fill="x", pady=2)

            # STT với dấu "..."
            tk.Label(player_frame, text="7.", fg="#333333", bg="white", 
                    font=("Arial", 8, "bold"), width=3).pack(side="left")
            
            # Tên với dấu "..."
            tk.Label(player_frame, text="...", fg="#333333", bg="white", 
                    font=("Arial", 8, "bold"), width=8, anchor="w").pack(side="left")
            
            # Level với dấu "..."
            tk.Label(player_frame, text="...", fg="#333333", bg="white", 
                    font=("Arial", 8), width=6).pack(side="left")
            
            # Thời gian với dấu "..."
            tk.Label(player_frame, text="...", fg="#333333", bg="white", 
                    font=("Arial", 8), width=8).pack(side="left")

        # Nếu không có người chơi nào
        if not ranking_data:
            tk.Label(self.ranking_content, text="Chưa có dữ liệu", 
                    fg="#666666", bg="white", font=("Arial", 10)).pack(pady=10)

        # Cập nhật canvas
        self.ranking_content.update_idletasks()
        self.ranking_canvas.configure(scrollregion=self.ranking_canvas.bbox("all"))

    def get_ranking_data(self):
        """Get ranking data from users.json and sort by highest level and best time of that level"""
        try:
            # Get users.json path (assuming it's in the same directory as data.json)
            users_json_path = os.path.join(os.path.dirname(JSON_PATH), "users.json")
            
            with open(users_json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            users = data.get("users", [])
            
            # Prepare ranking data
            ranking_data = []
            for user in users:
                username = user.get("username", "")
                completed_levels = user.get("completed_levels", [])
                best_times = user.get("best_times", {})
                
                # Calculate highest completed level
                highest_level = max(completed_levels) if completed_levels else 0
                
                # Get best time for the highest level
                best_time = 0
                if highest_level > 0:
                    # Tìm thời gian tốt nhất của level cao nhất
                    best_time = best_times.get(str(highest_level), 0)
                    
                ranking_data.append((username, highest_level, best_time))
            
            # Sort by highest level (descending) and best time (ascending)
            ranking_data.sort(key=lambda x: (-x[1], x[2]))
            
            return ranking_data
        
        except Exception as e:
            print(f"Lỗi khi đọc dữ liệu xếp hạng: {e}")
            return []

    def format_time(self, seconds):
        if seconds <= 0:
            return "--:--"
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"

    def update_user_info(self):
        if self.controller.current_user:
            user = self.controller.current_user
            self.user_label.config(text=user["username"])
            
            # Hiển thị level tiếp theo cần chơi (display ID)
            next_level = user.get("current_level", 1)
            self.level_label.config(text=f"Level {next_level}")
            
            # Tính số level đã mở khóa
            games_played = user.get("stats", {}).get("games_played", 0)
            
            # Tính accuracy (tỷ lệ phần trăm điểm đã tìm được)
            completed_levels = user.get("completed_levels", [])  # Giờ đây completed_levels lưu display ID
            total_differences_found = 0
            total_differences_all = 0
            
            # Tính tổng số điểm khác biệt đã tìm được và tổng số điểm trong tất cả các level
            for display_id, img_data in enumerate(self.images, 1):
                differences = img_data.get("differences", [])
                total_differences_all += len(differences)
                
                # Nếu level đã hoàn thành (theo display ID), thêm số điểm đã tìm được
                if display_id in completed_levels:
                    total_differences_found += len(differences)
            
            # Tính phần trăm accuracy
            accuracy = (total_differences_found / total_differences_all * 100) if total_differences_all > 0 else 0
            
            self.stats_label.config(
                text=f"Games: {games_played} | Accuracy: {accuracy:.1f}%")

    def on_show(self):
        self.load_background_gif()
        self.load_level_icons()
        self.update_user_info()
        self.update_mini_ranking()  # Cập nhật bảng xếp hạng nhỏ
        self.animate_gif()

    def load_background_gif(self):
        self.gif_frames = []
        try:
            gif_path = os.path.join(IMG_DIR, "ramen-and-rain.gif")
            gif = Image.open(gif_path)
            for frame in ImageSequence.Iterator(gif):
                frame = frame.resize((300, 700))
                photo = ImageTk.PhotoImage(frame)
                self.gif_frames.append(photo)
                self.controller._global_images.append(photo)
        except Exception as e:
            print("Lỗi load background GIF:", e)

    def animate_gif(self):
        if self.gif_frames:
            frame = self.gif_frames[self.gif_index]
            self.gif_label.configure(image=frame)
            self.gif_index = (self.gif_index + 1) % len(self.gif_frames)
            self.after(100, self.animate_gif)

    def load_level_icons(self):
        for widget in self.right_frame.winfo_children():
            widget.destroy()

        if not os.path.exists(JSON_PATH):
            print(f"❌ File JSON không tồn tại: {JSON_PATH}")
            messagebox.showerror("Lỗi", f"Không tìm thấy file data.json tại:\n{JSON_PATH}")
            return

        try:
            with open(JSON_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.images = data.get("images", [])
            
            # Sử dụng DifficultyAnalyzer mới
            from core.difficulty_analyzer import DifficultyAnalyzer
            analyzer = DifficultyAnalyzer(JSON_PATH)
            difficulty_analysis = analyzer.analyze_all_levels()
            
            # Gán độ khó cho từng level
            for img_data in self.images:
                level_id = img_data.get("id")
                if level_id in difficulty_analysis:
                    analysis = difficulty_analysis[level_id]
                    img_data["difficulty_score"] = analysis['total_score']
                    img_data["difficulty_level"] = analysis['level']
                    img_data["difficulty_factors"] = analysis['factors']
                else:
                    img_data["difficulty_score"] = 0
                    img_data["difficulty_level"] = "CHƯA XÁC ĐỊNH"

            # Sắp xếp theo độ khó tăng dần
            self.images.sort(key=lambda x: x.get("difficulty_score", 0))
            
            # Tạo mapping từ display ID sang original ID
            self.display_to_original_mapping = {}
            for i, img_data in enumerate(self.images, 1):
                original_id = img_data.get("id")
                self.display_to_original_mapping[i] = original_id
            
            # Lưu mapping vào controller để pygame_screen sử dụng
            self.controller.display_to_original_mapping = self.display_to_original_mapping
            self.controller.images_by_display_id = self.images
            
            print(f"✅ Đã tải {len(self.images)} level từ JSON")
            print(f"✅ Display to Original mapping: {self.display_to_original_mapping}")
            
            # In báo cáo độ khó ra console
            report = analyzer.generate_difficulty_report()
            print("\n" + "="*50)
            print("BÁO CÁO ĐỘ KHÓ CÁC LEVEL:")
            print("="*50)
            for img_data in self.images:
                level_id = img_data.get("id")
                difficulty_level = img_data.get("difficulty_level", "N/A")
                difficulty_score = img_data.get("difficulty_score", 0)
                print(f"Level {level_id}: {difficulty_level} (Điểm: {difficulty_score})")
            
        except Exception as e:
            print(f"❌ Lỗi đọc file JSON: {e}")
            messagebox.showerror("Lỗi", f"Lỗi đọc file JSON:\n{e}")
            return

        if not os.path.exists(IMG_DIR):
            print(f"❌ Thư mục ảnh không tồn tại: {IMG_DIR}")
            messagebox.showerror("Lỗi", f"Không tìm thấy thư mục ảnh:\n{IMG_DIR}")
            return

        self.create_scrollable_levels()

    def get_difficulty_color(self, level: str) -> str:
        """Trả về màu sắc tương ứng với độ khó"""
        colors = {
            "DỄ": "green",
            "TRUNG BÌNH": "orange", 
            "KHÓ": "red",
            "RẤT KHÓ": "purple"
        }
        return colors.get(level, "black")

    def create_scrollable_levels(self):
        main_frame = tk.Frame(self.right_frame, bg="white")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        canvas = tk.Canvas(main_frame, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Thêm sự kiện cuộn chuột cho canvas chứa level
        canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))
        scrollable_frame.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        row, col = 0, 0
        levels_loaded = 0

        # Lấy thông tin người dùng hiện tại
        user = self.controller.current_user
        completed_levels = user.get("completed_levels", [])
        current_level = user.get("current_level", 1)

        for display_id, img_data in enumerate(self.images, 1):
            original_id = self.display_to_original_mapping[display_id]
            left_path = os.path.join(IMG_DIR, img_data.get("left_path", "").replace("image/", ""))

            # - current_level là level TIẾP THEO cần chơi
            is_unlocked = (display_id == 1) or (display_id <= current_level)

            print(f"🔍 Display ID: {display_id}, Original ID: {original_id}, Unlocked: {is_unlocked}")

            if not os.path.exists(left_path):
                print(f"⚠️ File ảnh không tồn tại: {left_path}")
                img = Image.new("RGB", (150, 150), (200, 200, 200))
                draw = ImageDraw.Draw(img)
                draw.text((75, 75), f"Level {display_id}", fill=(0, 0, 0), anchor="mm")
                
                # Nếu level bị khóa, làm mờ ảnh
                if not is_unlocked:
                    img = Image.new("RGB", (150, 150), (100, 100, 100))
                    draw = ImageDraw.Draw(img)
                    draw.text((75, 75), f"Level {display_id}", fill=(50, 50, 50), anchor="mm")
            else:
                try:
                    img = Image.open(left_path).resize((150, 150)).convert("RGBA")
                    
                    # Nếu level bị khóa, làm mờ ảnh
                    if not is_unlocked:
                        # Tạo một bản sao mờ của ảnh
                        img = img.convert("L")  # Chuyển sang ảnh xám
                        img = img.convert("RGBA")
                except Exception as e:
                    print(f"⚠️ Lỗi load ảnh {left_path}: {e}")
                    img = Image.new("RGB", (150, 150), (200, 200, 200))
                    draw = ImageDraw.Draw(img)
                    draw.text((75, 75), "Lỗi", fill=(255, 0, 0), anchor="mm")

            try:
                # KHÔI PHỤC MASK HÌNH TRÒN
                mask = Image.new("L", (150, 150), 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0, 150, 150), fill=255)
                img.putalpha(mask)

                border = Image.new("RGBA", (156, 156), (255, 255, 255, 255))
                border.paste(img, (3, 3), img)
                img = border

                tk_img = ImageTk.PhotoImage(img)
                self._icon_images.append(tk_img)

                if is_unlocked:
                    btn = tk.Button(
                        scrollable_frame,
                        image=tk_img,
                        bd=0,
                        bg="white",
                        activebackground="white",
                        relief="flat",
                        command=lambda disp_id=display_id: self.start_level(disp_id)
                    )
                else:
                    btn = tk.Button(
                        scrollable_frame,
                        image=tk_img,
                        bd=0,
                        bg="white",
                        activebackground="white",
                        relief="flat",
                        state="disabled"
                    )

                btn.image = tk_img
                btn.grid(row=row, column=col, padx=20, pady=20)

                # Thêm biểu tượng khóa cho level chưa mở
                if not is_unlocked:
                    lock_label = tk.Label(scrollable_frame, text="🔒", 
                                        bg="white", font=("Arial", 20))
                    lock_label.grid(row=row, column=col, sticky="ne", padx=5, pady=5)

                level_label = tk.Label(scrollable_frame, text=f"Level {display_id}",
                                    bg="white", font=("Arial", 12, "bold"))
                level_label.grid(row=row+1, column=col, pady=(0, 5))

                # Thêm label hiển thị độ khó
                difficulty_text = f"Độ khó: {img_data.get('difficulty_level', 'N/A')}"
                difficulty_label = tk.Label(
                    scrollable_frame, 
                    text=difficulty_text,
                    bg="white", 
                    font=("Arial", 9),
                    fg=self.get_difficulty_color(img_data.get('difficulty_level', ''))
                )
                difficulty_label.grid(row=row+2, column=col, pady=(0, 20))

                col += 1
                if col == 4:
                    col = 0
                    row += 3

                levels_loaded += 1

            except Exception as e:
                print(f"⚠️ Lỗi tạo icon level {display_id}: {e}")

        print(f"✅ Đã tải thành công {levels_loaded} level")

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def start_level(self, display_id):
        print(f"🎮 Bắt đầu level {display_id}")
        original_id = self.display_to_original_mapping.get(display_id, display_id)
        self.controller.frames["PyGameScreen"].start_level(original_id, display_id) 