# scripts/analyze_difficulty.py
import sys
import os

# Thêm đường dẫn gốc vào sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

try:
    from core.difficulty_analyzer import DifficultyAnalyzer
    from core.helpers import JSON_PATH
except ImportError as e:
    print(f"❌ Lỗi import: {e}")
    print("🔍 Kiểm tra cấu trúc thư mục:")
    print(f"   Current dir: {current_dir}")
    print(f"   Parent dir: {parent_dir}")
    print(f"   sys.path: {sys.path}")
    sys.exit(1)

def main():
    try:
        print("🔍 Đang phân tích độ khó các level...")
        analyzer = DifficultyAnalyzer(JSON_PATH)
        report = analyzer.generate_difficulty_report()
        print(report)
        
        # Lưu ra file
        report_path = os.path.join(parent_dir, "difficulty_analysis_report.txt")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"✅ Đã lưu báo cáo vào: {report_path}")
        
    except Exception as e:
        print(f"❌ Lỗi khi phân tích: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()