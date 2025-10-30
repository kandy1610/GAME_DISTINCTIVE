# main.py
from app import GameApp
import sys
sys.stdout.reconfigure(encoding='utf-8')

if __name__ == "__main__":
    app = GameApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Đảm bảo cửa sổ được căn giữa hoàn hảo
    app.after(200, lambda: app.final_center() if hasattr(app, 'final_center') else None)
    
    app.mainloop()