import json
from app import app
from utils.db import get_db
from models.password import Password

# 创建应用上下文
with app.app_context():
    # 获取数据库连接
    db = get_db()
    
    # 获取所有用户
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id FROM users")
    users = cursor.fetchall()
    
    print(f"找到 {len(users)} 个用户")
    
    # 遍历所有用户
    for user in users:
        user_id = user['id']
        passwords = Password.find_by_user_id(db, user_id)
        
        print(f"用户 {user_id} 有 {len(passwords)} 个密码")
        
        # 打印第一个密码的结构
        if passwords:
            print("密码数据结构:")
            print(json.dumps(passwords[0], indent=2))
            break