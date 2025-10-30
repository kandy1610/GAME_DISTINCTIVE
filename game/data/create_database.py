# import json

# # Dữ liệu ảnh
# images = [
#     {
#         "id": 1,
#         "left_path": "left_1.png",
#         "right_path": "right_1.png",
#         "differences": [
#             {"x": 35, "y": 20, "w": 100, "h": 80},    # Mây
#             {"x": 180, "y": 50, "w": 300, "h": 120},  # Cá kiếm
#             {"x": 10, "y": 370, "w": 90, "h": 110},   # Cá ngựa
#             {"x": 420, "y": 400, "w": 130, "h": 80},  # Tôm
#             {"x": 240, "y": 400, "w": 135, "h": 110}, # Đầu sứa
#             {"x": 450, "y": 560, "w": 130, "h": 120}, # Cua
#             {"x": 420, "y": 260, "w": 90, "h": 80}    # Vây cá xanh
#         ]
#     }
# ]

# # Gói toàn bộ dữ liệu vào một dict
# data = {"images": images}

# # Ghi ra file JSON
# with open("differences.json", "w", encoding="utf-8") as f:
#     json.dump(data, f, indent=4, ensure_ascii=False)

# print("✅ File differences.json đã được tạo thành công!")


import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Tên file JSON
json_file = "E:\PYTHON\game\data\differences.json"

# Đọc dữ liệu hiện có (nếu có)
try:
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
except FileNotFoundError:
    data = {"images": []}  # nếu file chưa tồn tại

# Tự động đặt ID mới = ID cuối cùng + 1
new_id = len(data["images"]) + 1

# Cặp ảnh mới và danh sách điểm khác biệt
new_image = {
    "id": new_id,
    "left_path": "left_2.png",
    "right_path": "right_2.png",
    "differences": [
        {"x": 150, "y":  50, "w":  70, "h":  60},   # 1. Lá cây phía trên cùng bên trái
        {"x": 300, "y": 110, "w":  70, "h":  60},   # 2. Lá cây ở giữa trên mái vòm
        {"x": 250, "y": 180, "w":  80, "h":  70},   # 3. Mái nhà tam giác màu nâu
        {"x": 170, "y": 280, "w":  80, "h":  60},   # 4. Mái hiên đỏ bên trái
        {"x": 420, "y": 180, "w":  90, "h":  80},   # 5. Cửa sổ trên tháp lớn giữa
        {"x": 550, "y": 220, "w":  80, "h":  80},   # 6. Mái vòm nhỏ phía sau bên phải
        {"x": 150, "y": 440, "w":  90, "h":  70},   # 7. Tranh nhỏ bên trái (dưới cùng)
        {"x": 320, "y": 350, "w":  90, "h":  80},   # 8. Tranh giữa khác
        {"x": 470, "y": 600, "w": 100, "h":  80},   # 9. Giày họa sĩ khác
        {"x": 520, "y": 400, "w":  90, "h": 100}    # 10. Khuôn mặt / tay người đàn ông áo xanh
    ]
}

# Thêm vào danh sách ảnh
data["images"].append(new_image)

# Ghi lại file JSON
with open(json_file, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print("✅ Đã thêm cặp ảnh mới left_2.png / right_2.png vào differences.json thành công.")
