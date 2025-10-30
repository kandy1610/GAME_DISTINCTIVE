# core/user_manager.py
import json
import os
import hashlib
from .helpers import USERS_PATH

class UserManager:
    def __init__(self, users_file=USERS_PATH):
        self.users_file = users_file
        self.ensure_users_file()
    
    def ensure_users_file(self):
        os.makedirs(os.path.dirname(self.users_file), exist_ok=True)
        if not os.path.exists(self.users_file):
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump({"users": []}, f, indent=2)
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, username, password, email=""):
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for user in data["users"]:
                if user["username"] == username:
                    return False, "Username already exists"
            
            new_user = {
                "username": username,
                "password": self.hash_password(password),
                "email": email,
                "xp": 0,
                "level": 1,
                "completed_levels": [],
                "current_level": 1,
                "best_times": {},
                "stats": {
                    "games_played": 0,
                    "total_score": 0,
                    "avg_accuracy": 0
                }
            }
            
            data["users"].append(new_user)
            
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            return True, "Registration successful"
            
        except Exception as e:
            return False, f"Registration failed: {str(e)}"
    
    def login_user(self, username, password):
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            hashed_password = self.hash_password(password)
            
            for user in data["users"]:
                if user["username"] == username and user["password"] == hashed_password:
                    return True, "Login successful", user
            
            return False, "Invalid username or password", None
            
        except Exception as e:
            return False, f"Login failed: {str(e)}", None
    
    def update_user(self, username, updated_data):
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for i, user in enumerate(data["users"]):
                if user["username"] == username:
                    data["users"][i].update(updated_data)
                    break
            
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error updating user: {e}")
            return False