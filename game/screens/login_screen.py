# screens/login_screen.py
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageSequence, ImageDraw
import os
from core.helpers import IMG_DIR, center_window

class LoginScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="black")
        
        self.bg_frames = []
        self.bg_index = 0
        
        self.canvas = tk.Canvas(self, width=1200, height=700, highlightthickness=0, bg="black")
        self.canvas.pack(fill="both", expand=True)
        
        self.bg_image_on_canvas = self.canvas.create_image(0, 0, anchor="nw")
        
        # Form container với background trắng và viền
        self.form_container = tk.Frame(self.canvas, bg="white", bd=2, relief="ridge")
        self.form_container.place(relx=0.5, rely=0.5, anchor="center", width=400, height=450)
        
        self.create_login_form()
        self.create_register_form()
    
    def toggle_password_visibility(self, entry, button):
        """Chuyển đổi hiển thị/ẩn mật khẩu"""
        if entry.cget('show') == '*':
            entry.config(show='')
            button.config(text='🙈')  # Biểu tượng mắt nhắm
        else:
            entry.config(show='*')
            button.config(text='👁️')  # Biểu tượng mắt mở
    
    def create_login_form(self):
        title_label = tk.Label(self.form_container, text="DISTINCTIVE", 
                              fg="#2c3e50", bg="white", font=("Arial", 16, "bold"))
        title_label.pack(pady=25)
        
        subtitle_label = tk.Label(self.form_container, text="ĐĂNG NHẬP", 
                                fg="#3498db", bg="white", font=("Arial", 14, "bold"))
        subtitle_label.pack(pady=(0, 20))
        
        tk.Label(self.form_container, text="Tên đăng nhập:", 
                fg="#2c3e50", bg="white", font=("Arial", 11)).pack(anchor="w", padx=40, pady=(10,5))
        
        # Input với màu nền xám nhạt và viền rõ hơn
        self.username_entry = tk.Entry(self.form_container, font=("Arial", 11), width=25,
                                     bg="#f8f9fa", fg="#2c3e50",  # Nền xám nhạt, chữ đậm
                                     relief="solid", bd=1,  # Viền rõ ràng
                                     highlightthickness=1, highlightcolor="#3498db")  # Màu khi focus
        self.username_entry.pack(padx=40, pady=(0,15), fill="x", ipady=5)  # Thêm padding bên trong
        
        tk.Label(self.form_container, text="Mật khẩu:", 
                fg="#2c3e50", bg="white", font=("Arial", 11)).pack(anchor="w", padx=40, pady=(0,5))
        
        # Frame cho password entry và nút con mắt - SỬA LẠI ĐỂ CĂN GIỮA
        password_frame = tk.Frame(self.form_container, bg="white")
        password_frame.pack(padx=40, pady=(0,20), fill="x")
        
        # Input password với cùng style
        self.password_entry = tk.Entry(password_frame, font=("Arial", 11), width=25, show="*",
                                     bg="#f8f9fa", fg="#2c3e50",
                                     relief="solid", bd=1,
                                     highlightthickness=1, highlightcolor="#3498db")
        self.password_entry.pack(side="left", fill="x", expand=True, ipady=5)
        
        # Nút con mắt để hiển thị/ẩn mật khẩu - SỬA LẠI ĐỂ CĂN GIỮA HOÀN TOÀN
        self.password_eye_btn = tk.Button(password_frame, text="👁️", 
                                         font=("Arial", 12),
                                         bg="#f8f9fa", fg="#2c3e50",
                                         relief="solid", bd=1,
                                         width=3,
                                         command=lambda: self.toggle_password_visibility(self.password_entry, self.password_eye_btn))
        # Sử dụng pack với cùng ipady như entry để đảm bảo cùng chiều cao
        self.password_eye_btn.pack(side="right", padx=(5, 0), ipady=5)
        
        button_frame = tk.Frame(self.form_container, bg="white")
        button_frame.pack(pady=25)
        
        login_btn = tk.Button(button_frame, text="ĐĂNG NHẬP", 
                             font=("Arial", 11, "bold"),
                             bg="#4CAF50", fg="white",
                             width=12, height=1,
                             relief="raised", bd=2,  # Thêm hiệu ứng nổi cho nút
                             command=self.login)
        login_btn.pack(side="left", padx=8)
        
        register_btn = tk.Button(button_frame, text="ĐĂNG KÝ", 
                                font=("Arial", 11, "bold"),
                                bg="#2196F3", fg="white",
                                width=12, height=1,
                                relief="raised", bd=2,
                                command=self.show_register)
        register_btn.pack(side="left", padx=8)
        
        self.status_label = tk.Label(self.form_container, text="", 
                                    fg="#e74c3c", bg="white", font=("Arial", 10))
        self.status_label.pack(pady=10)
        
        # Thêm sự kiện Enter để đăng nhập
        self.username_entry.bind("<Return>", lambda e: self.login())
        self.password_entry.bind("<Return>", lambda e: self.login())
    
    def create_register_form(self):
        self.register_container = tk.Frame(self.canvas, bg="white", bd=2, relief="ridge")
        
        title_label = tk.Label(self.register_container, text="ĐĂNG KÝ TÀI KHOẢN", 
                              fg="#2c3e50", bg="white", font=("Arial", 16, "bold"))
        title_label.pack(pady=25)
        
        tk.Label(self.register_container, text="Tên đăng nhập:", 
                fg="#2c3e50", bg="white", font=("Arial", 11)).pack(anchor="w", padx=40, pady=(10,5))
        
        # Input register với style tương tự
        self.reg_username_entry = tk.Entry(self.register_container, font=("Arial", 11), width=25,
                                         bg="#f8f9fa", fg="#2c3e50",
                                         relief="solid", bd=1,
                                         highlightthickness=1, highlightcolor="#3498db")
        self.reg_username_entry.pack(padx=40, pady=(0,15), fill="x", ipady=5)
        
        tk.Label(self.register_container, text="Mật khẩu:", 
                fg="#2c3e50", bg="white", font=("Arial", 11)).pack(anchor="w", padx=40, pady=(0,5))
        
        # Frame cho password entry và nút con mắt (đăng ký) - SỬA LẠI ĐỂ CĂN GIỮA
        reg_password_frame = tk.Frame(self.register_container, bg="white")
        reg_password_frame.pack(padx=40, pady=(0,15), fill="x")
        
        self.reg_password_entry = tk.Entry(reg_password_frame, font=("Arial", 11), width=25, show="*",
                                         bg="#f8f9fa", fg="#2c3e50",
                                         relief="solid", bd=1,
                                         highlightthickness=1, highlightcolor="#3498db")
        self.reg_password_entry.pack(side="left", fill="x", expand=True, ipady=5)
        
        # Nút con mắt cho password đăng ký - SỬA LẠI ĐỂ CĂN GIỮA HOÀN TOÀN
        self.reg_password_eye_btn = tk.Button(reg_password_frame, text="👁️", 
                                             font=("Arial", 12),
                                             bg="#f8f9fa", fg="#2c3e50",
                                             relief="solid", bd=1,
                                             width=3,
                                             command=lambda: self.toggle_password_visibility(self.reg_password_entry, self.reg_password_eye_btn))
        # Sử dụng pack với cùng ipady như entry để đảm bảo cùng chiều cao
        self.reg_password_eye_btn.pack(side="right", padx=(5, 0), ipady=5)
        
        tk.Label(self.register_container, text="Xác nhận mật khẩu:", 
                fg="#2c3e50", bg="white", font=("Arial", 11)).pack(anchor="w", padx=40, pady=(0,5))
        
        # Frame cho confirm password entry và nút con mắt - SỬA LẠI ĐỂ CĂN GIỮA
        reg_confirm_frame = tk.Frame(self.register_container, bg="white")
        reg_confirm_frame.pack(padx=40, pady=(0,15), fill="x")
        
        self.reg_confirm_entry = tk.Entry(reg_confirm_frame, font=("Arial", 11), width=25, show="*",
                                        bg="#f8f9fa", fg="#2c3e50",
                                        relief="solid", bd=1,
                                        highlightthickness=1, highlightcolor="#3498db")
        self.reg_confirm_entry.pack(side="left", fill="x", expand=True, ipady=5)
        
        # Nút con mắt cho confirm password - SỬA LẠI ĐỂ CĂN GIỮA HOÀN TOÀN
        self.reg_confirm_eye_btn = tk.Button(reg_confirm_frame, text="👁️", 
                                            font=("Arial", 12),
                                            bg="#f8f9fa", fg="#2c3e50",
                                            relief="solid", bd=1,
                                            width=3,
                                            command=lambda: self.toggle_password_visibility(self.reg_confirm_entry, self.reg_confirm_eye_btn))
        # Sử dụng pack với cùng ipady như entry để đảm bảo cùng chiều cao
        self.reg_confirm_eye_btn.pack(side="right", padx=(5, 0), ipady=5)
        
        tk.Label(self.register_container, text="Email (tùy chọn):", 
                fg="#2c3e50", bg="white", font=("Arial", 11)).pack(anchor="w", padx=40, pady=(0,5))
        
        self.reg_email_entry = tk.Entry(self.register_container, font=("Arial", 11), width=25,
                                      bg="#f8f9fa", fg="#2c3e50",
                                      relief="solid", bd=1,
                                      highlightthickness=1, highlightcolor="#3498db")
        self.reg_email_entry.pack(padx=40, pady=(0,20), fill="x", ipady=5)
        
        button_frame = tk.Frame(self.register_container, bg="white")
        button_frame.pack(pady=20)
        
        register_btn = tk.Button(button_frame, text="ĐĂNG KÝ", 
                                font=("Arial", 11, "bold"),
                                bg="#4CAF50", fg="white",
                                width=12, height=1,
                                relief="raised", bd=2,
                                command=self.register)
        register_btn.pack(side="left", padx=8)
        
        back_btn = tk.Button(button_frame, text="QUAY LẠI", 
                            font=("Arial", 11, "bold"),
                            bg="#f44336", fg="white",
                            width=12, height=1,
                            relief="raised", bd=2,
                            command=self.show_login)
        back_btn.pack(side="left", padx=8)
        
        self.reg_status_label = tk.Label(self.register_container, text="", 
                                        fg="#e74c3c", bg="white", font=("Arial", 10))
        self.reg_status_label.pack(pady=10)
        
        # Thêm sự kiện Enter để đăng ký
        self.reg_username_entry.bind("<Return>", lambda e: self.register())
        self.reg_password_entry.bind("<Return>", lambda e: self.register())
        self.reg_confirm_entry.bind("<Return>", lambda e: self.register())
        self.reg_email_entry.bind("<Return>", lambda e: self.register())
    
    def on_show(self):
        self.load_background_gif()
        self.animate_background()
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.status_label.config(text="")
        self.show_login()
        # Focus vào ô username khi hiển thị form đăng nhập
        self.username_entry.focus_set()
    
    def load_background_gif(self):
        self.bg_frames = []
        try:
            bg_gif_path = os.path.join(IMG_DIR, "ramen-and-rain.gif")
            gif = Image.open(bg_gif_path)
            for frame in ImageSequence.Iterator(gif):
                frame = frame.resize((1200, 700), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(frame)
                self.bg_frames.append(photo)
                self.controller._global_images.append(photo)
        except Exception as e:
            print(f"Lỗi load background GIF: {e}")
            # Tạo background đen nếu không load được GIF
            fallback = Image.new("RGB", (1200, 700), "black")
            photo = ImageTk.PhotoImage(fallback)
            self.bg_frames = [photo]
            self.controller._global_images.append(photo)
    
    def animate_background(self):
        if self.bg_frames:
            frame = self.bg_frames[self.bg_index]
            self.canvas.itemconfig(self.bg_image_on_canvas, image=frame)
            self.bg_index = (self.bg_index + 1) % len(self.bg_frames)
            self.after(50, self.animate_background)
    
    def show_login(self):
        self.register_container.place_forget()
        self.form_container.place(relx=0.5, rely=0.5, anchor="center", width=400, height=450)
        # Focus vào ô username
        self.username_entry.focus_set()
    
    def show_register(self):
        self.form_container.place_forget()
        self.register_container.place(relx=0.5, rely=0.5, anchor="center", width=400, height=500)
        self.reg_username_entry.delete(0, tk.END)
        self.reg_password_entry.delete(0, tk.END)
        self.reg_confirm_entry.delete(0, tk.END)
        self.reg_email_entry.delete(0, tk.END)
        self.reg_status_label.config(text="")
        # Focus vào ô username đăng ký
        self.reg_username_entry.focus_set()
    
    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            self.status_label.config(text="Vui lòng điền đầy đủ thông tin")
            return
        
        success, message, user_data = self.controller.user_manager.login_user(username, password)
        
        if success:
            self.controller.current_user = user_data
            self.status_label.config(text="Đăng nhập thành công! Đang tải...", fg="#27ae60")
            self.after(1000, lambda: self.controller.show_frame("LoadingScreen2"))
        else:
            self.status_label.config(text=message, fg="#e74c3c")
    
    def register(self):
        username = self.reg_username_entry.get().strip()
        password = self.reg_password_entry.get()
        confirm_password = self.reg_confirm_entry.get()
        email = self.reg_email_entry.get().strip()
        
        if not username or not password:
            self.reg_status_label.config(text="Vui lòng điền đầy đủ thông tin bắt buộc")
            return
        
        if password != confirm_password:
            self.reg_status_label.config(text="Mật khẩu xác nhận không khớp")
            return
        
        if len(password) < 4:
            self.reg_status_label.config(text="Mật khẩu phải có ít nhất 4 ký tự")
            return
        
        success, message = self.controller.user_manager.register_user(username, password, email)
        
        if success:
            self.reg_status_label.config(text="Đăng ký thành công! Vui lòng đăng nhập.", fg="#27ae60")
            self.after(2000, self.show_login)
        else:
            self.reg_status_label.config(text=message, fg="#e74c3c")