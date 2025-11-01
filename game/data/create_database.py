import json
import random
from datetime import datetime, timedelta

# Dữ liệu độ khó từ difficulty_report
difficulty_data = {
    1: {"n_diffs": 7, "difficulty_score": 0.248, "difficulty_level": "DỄ"},
    2: {"n_diffs": 10, "difficulty_score": 0.672, "difficulty_level": "KHÓ"},
    3: {"n_diffs": 3, "difficulty_score": 0.224, "difficulty_level": "DỄ"},
    4: {"n_diffs": 5, "difficulty_score": 0.33, "difficulty_level": "TRUNG BÌNH"},
    5: {"n_diffs": 9, "difficulty_score": 0.521, "difficulty_level": "TRUNG BÌNH"},
    6: {"n_diffs": 9, "difficulty_score": 0.587, "difficulty_level": "KHÓ"},
    7: {"n_diffs": 10, "difficulty_score": 0.786, "difficulty_level": "RẤT KHÓ"},
    8: {"n_diffs": 2, "difficulty_score": 0.357, "difficulty_level": "TRUNG BÌNH"},
    9: {"n_diffs": 2, "difficulty_score": 0.357, "difficulty_level": "TRUNG BÌNH"},
    10: {"n_diffs": 8, "difficulty_score": 0.423, "difficulty_level": "TRUNG BÌNH"},
    11: {"n_diffs": 6, "difficulty_score": 0.389, "difficulty_level": "TRUNG BÌNH"},
    12: {"n_diffs": 4, "difficulty_score": 0.412, "difficulty_level": "TRUNG BÌNH"},
    13: {"n_diffs": 7, "difficulty_score": 0.612, "difficulty_level": "KHÓ"},
    14: {"n_diffs": 5, "difficulty_score": 0.354, "difficulty_level": "TRUNG BÌNH"},
    15: {"n_diffs": 9, "difficulty_score": 0.812, "difficulty_level": "RẤT KHÓ"},
    16: {"n_diffs": 3, "difficulty_score": 0.198, "difficulty_level": "DỄ"},
    17: {"n_diffs": 8, "difficulty_score": 0.724, "difficulty_level": "KHÓ"},
    18: {"n_diffs": 6, "difficulty_score": 0.478, "difficulty_level": "TRUNG BÌNH"},
    19: {"n_diffs": 4, "difficulty_score": 0.372, "difficulty_level": "TRUNG BÌNH"},
    20: {"n_diffs": 10, "difficulty_score": 0.894, "difficulty_level": "RẤT KHÓ"}
}

# Các detailed_factors mẫu cho từng image_id
detailed_factors_templates = {
    1: {"count_factor": 0.7, "size_factor": 0.12, "distribution_factor": 0.808, "edge_factor": 0.0, "visibility_factor": 0.028},
    4: {"count_factor": 0.5, "size_factor": 0.446, "distribution_factor": 0.604, "edge_factor": 0.04, "visibility_factor": 0.055},
    # ... thêm các template khác
}

def generate_detailed_factors(image_id):
    """Tạo detailed_factors dựa trên image_id"""
    base_factors = {
        "count_factor": round(random.uniform(0.1, 1.0), 3),
        "size_factor": round(random.uniform(0.1, 0.9), 3),
        "distribution_factor": round(random.uniform(0.4, 0.9), 3),
        "edge_factor": round(random.uniform(0.0, 0.4), 3),
        "visibility_factor": round(random.uniform(0.02, 0.2), 3)
    }
    return base_factors

def generate_game_session(username, session_id):
    """Tạo một lượt chơi ngẫu nhiên"""
    image_id = random.choice(list(difficulty_data.keys()))
    n_diffs = difficulty_data[image_id]["n_diffs"]
    
    # Thời gian chơi phụ thuộc vào độ khó
    base_time = difficulty_data[image_id]["difficulty_score"] * 60
    elapsed_time = round(random.uniform(base_time * 0.5, base_time * 2.0), 2)
    
    # Số lần click phụ thuộc vào số điểm khác biệt
    clicks_total = n_diffs + random.randint(0, 8)
    correct_clicks = n_diffs
    wrong_clicks = clicks_total - correct_clicks
    
    # Các thông số khác
    hints_used = random.randint(0, 2)
    lives_left = random.randint(0, 3)
    game_state = "win" if lives_left > 0 else "lose"
    
    # Thời gian bắt đầu và kết thúc
    base_time = 1761412689.0 + (session_id * 3600)  # Mỗi session cách nhau 1 giờ
    start_time = base_time + random.uniform(0, 300)
    end_time = start_time + elapsed_time
    
    return {
        "username": username,
        "original_id": image_id,
        "display_id": image_id,
        "start_time": round(start_time, 6),
        "end_time": round(end_time, 6),
        "elapsed_time": elapsed_time,
        "clicks_total": clicks_total,
        "correct_clicks": correct_clicks,
        "wrong_clicks": wrong_clicks,
        "hints_used": hints_used,
        "lives_left": lives_left,
        "game_state": game_state,
        "score": None,
        "features": {
            "image_id": image_id,
            "n_diffs": n_diffs,
            "mean_area": 0,
            "inv_mean": 0,
            "n_norm": round(n_diffs / 10.0, 1),
            "inv_mean_norm": round(random.uniform(0.1, 0.9), 3),
            "difficulty_score": difficulty_data[image_id]["difficulty_score"],
            "difficulty_level": difficulty_data[image_id]["difficulty_level"],
            "detailed_factors": generate_detailed_factors(image_id)
        }
    }

# Tạo dữ liệu gốc
original_data = [
    # ... (giữ nguyên các bản ghi gốc từ file cũ)
    {
        "username": "ChienMinh",
        "original_id": 1,
        "display_id": 1,
        "start_time": 1761412689.2286398,
        "end_time": 1761412728.2804346,
        "elapsed_time": 39.04887509346008,
        "clicks_total": 8,
        "correct_clicks": 6,
        "wrong_clicks": 2,
        "hints_used": 1,
        "lives_left": 1,
        "game_state": "win",
        "score": None,
        "features": {
            "image_id": 1,
            "n_diffs": 7,
            "mean_area": 0,
            "inv_mean": 0,
            "n_norm": 0.7,
            "inv_mean_norm": 0.12,
            "difficulty_score": 0.248,
            "difficulty_level": "DỄ",
            "detailed_factors": {
                "count_factor": 0.7,
                "size_factor": 0.12,
                "distribution_factor": 0.808,
                "edge_factor": 0.0,
                "visibility_factor": 0.028
            }
        }
    },
    # ... (thêm tất cả các bản ghi gốc khác)
]

# Tạo dữ liệu mô phỏng cho 10 người dùng
users = ["User1", "User2", "User3", "User4", "User5", "User6", "User7", "User8", "User9", "User10"]
simulated_data = []

session_id = 100
for user in users:
    # Mỗi người dùng có 25-35 lượt chơi
    num_sessions = random.randint(25, 35)
    for i in range(num_sessions):
        session = generate_game_session(user, session_id)
        simulated_data.append(session)
        session_id += 1

# Kết hợp dữ liệu gốc và dữ liệu mô phỏng
all_data = original_data + simulated_data

# Lưu vào file
with open('play_logs.json', 'w', encoding='utf-8') as f:
    json.dump(all_data, f, indent=2, ensure_ascii=False)

print(f"Đã tạo {len(all_data)} lượt chơi trong play_logs.json")