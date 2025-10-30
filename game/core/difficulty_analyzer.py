# core/difficulty_analyzer.py
import json
import statistics
from typing import Dict, List
import os

class DifficultyAnalyzer:
    def __init__(self, json_path: str):
        self.json_path = json_path
        self.image_width = 600
        self.image_height = 700
        self._load_data()
    
    def _load_data(self):
        """Load dữ liệu từ JSON"""
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.images = data.get('images', [])
        except Exception as e:
            print(f"❌ Lỗi load data: {e}")
            self.images = []
    
    def calculate_comprehensive_difficulty(self, differences: List[Dict]) -> Dict:
        """
        Tính toán độ khó toàn diện dựa trên nhiều yếu tố
        """
        if not differences:
            return {
                'total_score': 0,
                'factors': {
                    'count_factor': 0,
                    'size_factor': 0,
                    'distribution_factor': 0,
                    'edge_factor': 0,
                    'visibility_factor': 0
                }
            }
        
        # 1. Yếu tố số lượng (25%)
        n_diffs = len(differences)
        count_factor = min(n_diffs / 10, 1.0)  # Chuẩn hóa: 10 điểm là max
        
        # 2. Yếu tố kích thước (25%)
        areas = [diff['w'] * diff['h'] for diff in differences]
        mean_area = statistics.mean(areas) if areas else 0
        min_area = min(areas) if areas else 0
        
        # Điểm nhỏ hơn thì khó hơn
        size_factor = 0
        if mean_area > 0:
            # Chuẩn hóa: diện tích trung bình < 1000 pixel là dễ, < 100 là rất khó
            size_factor = min(1000 / (mean_area + 100), 1.0)
        
        # 3. Yếu tố phân bố (20%)
        centers = []
        for diff in differences:
            center_x = diff['x'] + diff['w'] / 2
            center_y = diff['y'] + diff['h'] / 2
            centers.append((center_x, center_y))
        
        # Tính độ phân tán (cluster analysis đơn giản)
        if len(centers) > 1:
            avg_x = sum(c[0] for c in centers) / len(centers)
            avg_y = sum(c[1] for c in centers) / len(centers)
            distances_from_center = [
                ((c[0] - avg_x)**2 + (c[1] - avg_y)**2)**0.5 
                for c in centers
            ]
            avg_distance = statistics.mean(distances_from_center)
            # Chuẩn hóa: phân tán nhiều thì dễ tìm hơn
            distribution_factor = min(avg_distance / 300, 1.0)
        else:
            distribution_factor = 0.5
        
        # 4. Yếu tố vị trí biên (15%)
        edge_penalty = 0
        for center_x, center_y in centers:
            # Khoảng cách đến biên gần nhất
            dist_to_edge = min(
                center_x, self.image_width - center_x,
                center_y, self.image_height - center_y
            )
            # Điểm gần biên (<50 pixel) được penalty
            if dist_to_edge < 50:
                edge_penalty += (50 - dist_to_edge) / 50
        edge_factor = min(edge_penalty / len(centers), 1.0) if centers else 0
        
        # 5. Yếu tố visibility (15%) - dựa trên kích thước nhỏ nhất
        visibility_factor = 0
        if min_area > 0:
            # Điểm nhỏ nhất càng nhỏ càng khó
            visibility_factor = min(100 / (min_area + 10), 1.0)
        
        # Tổng hợp điểm với trọng số
        total_score = (
            0.25 * count_factor +
            0.25 * size_factor + 
            0.20 * (1 - distribution_factor) +  # Phân tán nhiều thì dễ → đảo ngược
            0.15 * edge_factor +
            0.15 * visibility_factor
        )
        
        return {
            'total_score': round(total_score, 3),
            'level': self._score_to_difficulty_level(total_score),
            'factors': {
                'count_factor': round(count_factor, 3),
                'size_factor': round(size_factor, 3),
                'distribution_factor': round(distribution_factor, 3),
                'edge_factor': round(edge_factor, 3),
                'visibility_factor': round(visibility_factor, 3)
            }
        }
    
    def _score_to_difficulty_level(self, score: float) -> str:
        """Chuyển điểm số thành mức độ khó"""
        if score < 0.3:
            return "DỄ"
        elif score < 0.5:
            return "TRUNG BÌNH"
        elif score < 0.7:
            return "KHÓ"
        else:
            return "RẤT KHÓ"
    
    def analyze_all_levels(self) -> Dict:
        """Phân tích độ khó tất cả levels"""
        results = {}
        for img in self.images:
            level_id = img['id']
            differences = img.get('differences', [])
            results[level_id] = self.calculate_comprehensive_difficulty(differences)
        
        return results
    
    def generate_difficulty_report(self) -> str:
        """Tạo báo cáo độ khó"""
        analysis = self.analyze_all_levels()
        
        report = "BÁO CÁO ĐỘ KHÓ CÁC LEVEL\n"
        report += "=" * 50 + "\n"
        
        for level_id, data in sorted(analysis.items()):
            report += f"Level {level_id}: {data['level']} (Điểm: {data['total_score']})\n"
            factors = data['factors']
            report += f"  - Số lượng: {factors['count_factor']}\n"
            report += f"  - Kích thước: {factors['size_factor']}\n"
            report += f"  - Phân bố: {factors['distribution_factor']}\n"
            report += f"  - Vị trí biên: {factors['edge_factor']}\n"
            report += f"  - Độ visible: {factors['visibility_factor']}\n"
            report += "\n"
        
        return report