# screens/loading_screen.py
import tkinter as tk
from PIL import Image, ImageTk, ImageSequence, ImageDraw
import os
from core.helpers import IMG_DIR

class LoadingScreen2(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.bg_frames = []
        self.bg_index = 0
        self.spinner_frames = []
        self.spinner_index = 0

        self.canvas = tk.Canvas(self, width=1200, height=700, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.bg_image_on_canvas = self.canvas.create_image(0, 0, anchor="nw")
        self.text_id = self.canvas.create_text(600, 350, text="DISTINCTIVE",
                                              fill="white",
                                              font=("Arial", 60, "bold"),
                                              anchor="center")
        self.spinner_id = self.canvas.create_image(1150, 650, anchor="se")

    def on_show(self):
        self.load_gifs()
        self.animate_background()
        self.animate_spinner()
        self.after(3000, self.open_game)

    def load_gifs(self):
        bg_gif_path = os.path.join(IMG_DIR, "ramen-and-rain.gif")
        self.bg_frames = []
        try:
            gif = Image.open(bg_gif_path)
            for frame in ImageSequence.Iterator(gif):
                frame = frame.resize((1200, 700), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(frame)
                self.bg_frames.append(photo)
                self.controller._global_images.append(photo)
        except Exception as e:
            print(f"Lỗi load background GIF: {e}")
            fallback = Image.new("RGB", (1200, 700), "black")
            photo = ImageTk.PhotoImage(fallback)
            self.bg_frames = [photo]
            self.controller._global_images.append(photo)

        spinner_gif_path = os.path.join(IMG_DIR, "circle-9360_256.gif")
        self.spinner_frames = []
        try:
            gif = Image.open(spinner_gif_path)
            for frame in ImageSequence.Iterator(gif):
                frame = frame.resize((80, 80), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(frame)
                self.spinner_frames.append(photo)
                self.controller._global_images.append(photo)
        except Exception as e:
            print(f"Lỗi load spinner GIF: {e}")
            self.create_fallback_spinner()

    def create_fallback_spinner(self):
        colors = ["white", "lightgray", "gray", "darkgray"]
        for i in range(12):
            img = Image.new("RGBA", (80, 80), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            for j in range(12):
                start_angle = j * 30
                end_angle = start_angle + 15
                color_idx = (i + j) % len(colors)
                draw.pieslice([10, 10, 70, 70], start_angle, end_angle,
                              fill=colors[color_idx], outline=colors[color_idx])
            photo = ImageTk.PhotoImage(img)
            self.spinner_frames.append(photo)
            self.controller._global_images.append(photo)

    def animate_background(self):
        if self.bg_frames:
            frame = self.bg_frames[self.bg_index]
            self.canvas.itemconfig(self.bg_image_on_canvas, image=frame)
            self.bg_index = (self.bg_index + 1) % len(self.bg_frames)
            self.after(50, self.animate_background)

    def animate_spinner(self):
        if self.spinner_frames:
            frame = self.spinner_frames[self.spinner_index]
            self.canvas.itemconfig(self.spinner_id, image=frame)
            self.spinner_index = (self.spinner_index + 1) % len(self.spinner_frames)
            self.after(100, self.animate_spinner)

    def open_game(self):
        self.controller.show_frame("MainGame")