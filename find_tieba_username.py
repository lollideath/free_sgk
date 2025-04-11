# find_tieba_username
# 用遍历法查找百度账号里缺失的字
import requests
import json
from urllib.parse import quote
import time
from tqdm import tqdm

# Function to get user data from the API
def get_user_data(username):
    encoded_username = quote(username, safe='')
    url = f"http://tieba.baidu.com/i/sys/user_json?un={encoded_username}&ie=utf-8"
    response = requests.get(url)
    if response.status_code == 200:
        if response.content.strip():
            try:
                raw_data = response.content.decode('utf-8', errors='ignore')
                data = json.loads(raw_data)
                
                portrait = data.get('creator', {}).get("portrait", "na")

                return {
                    "raw_name": data.get("raw_name", "na"),
                    "id": data.get("id", "na"),
                    "name": data.get("creator", {}).get("name", "na"),
                    "name_show": data.get("creator", {}).get("name_show", "na"),
                    "show_nickname": data.get("creator", {}).get("show_nickname", "na"),
                    "url": f"https://tieba.baidu.com/home/main?id={portrait}&fr=home"
                }
            except (ValueError, json.JSONDecodeError):
                return None
        else:
            return None
    else:
        return None

# List of symbols and all Chinese characters
symbols = list("~!@#$%^&*()_+-=[]{}|;:,.<>?")
common_chinese_chars = [chr(i) for i in range(0x4e00, 0x4e20)]

# Generate all Chinese characters (Unicode range)
all_chinese_chars = [chr(i) for i in range(0x4e00, 0x9fa6)]  # 所有中文字符

# Remaining Chinese characters excluding the common ones
remaining_chinese_chars = [char for char in all_chinese_chars if char not in common_chinese_chars]

# Combine common Chinese characters, symbols and remaining Chinese characters
search_order = list(common_chinese_chars) + symbols + remaining_chinese_chars

# Function to find the correct username
def find_correct_username():
    base_username = "前面{}后面"
    
    with open("valid_usernames.txt", "w", encoding="utf-8") as file:
        for char in tqdm(search_order, desc="Searching usernames"):
            username = base_username.format(char)
            user_data = get_user_data(username)
            if user_data:
                file.write(f"Found valid username: {username}\n")
                file.write(f"User data: {json.dumps(user_data, ensure_ascii=False)}\n\n")
                print(f"Found valid username: {username}")
                print(f"User data: {user_data}")
                break
            
            # Delay to prevent too frequent requests
            time.sleep(1)
        else:
            print("No valid username found.")

if __name__ == "__main__":
    find_correct_username()
