"""
用户模型
处理用户相关的数据库操作
"""

import bcrypt
from datetime import datetime
import uuid

class User:
    """用户模型类"""
    
    @staticmethod
    def create(db, email, password):
        """
        创建新用户
        
        Args:
            db: 数据库连接
            email: 用户邮箱
            password: 用户密码
            
        Returns:
            str: 用户ID
        """
        # 生成唯一ID
        user_id = str(uuid.uuid4())
        
        # 生成密码哈希
        password_hash = User.hash_password(password)
        
        # 当前时间
        now = datetime.now()
        
        # 插入用户记录
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO users (id, email, password_hash, created_at, updated_at) VALUES (%s, %s, %s, %s, %s)",
            (user_id, email, password_hash, now, now)
        )
        db.commit()
        
        return user_id
    
    @staticmethod
    def find_by_id(db, user_id):
        """
        通过ID查找用户
        
        Args:
            db: 数据库连接
            user_id: 用户ID
            
        Returns:
            dict: 用户信息，如果不存在则返回None
        """
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        return user
    
    @staticmethod
    def find_by_email(db, email):
        """
        通过邮箱查找用户
        
        Args:
            db: 数据库连接
            email: 用户邮箱
            
        Returns:
            dict: 用户信息，如果不存在则返回None
        """
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        return user
    
    @staticmethod
    def update(db, user_id, data):
        """
        更新用户信息
        
        Args:
            db: 数据库连接
            user_id: 用户ID
            data: 要更新的数据字典
            
        Returns:
            bool: 更新是否成功
        """
        # 过滤掉不允许更新的字段
        allowed_fields = ['email', 'master_key_encrypted']
        update_data = {k: v for k, v in data.items() if k in allowed_fields}
        
        if not update_data:
            return False
        
        # 添加更新时间
        update_data['updated_at'] = datetime.now()
        
        # 构建SQL语句
        set_clause = ", ".join([f"{field} = %s" for field in update_data.keys()])
        values = list(update_data.values())
        values.append(user_id)
        
        # 执行更新
        cursor = db.cursor()
        cursor.execute(
            f"UPDATE users SET {set_clause} WHERE id = %s",
            values
        )
        db.commit()
        
        return cursor.rowcount > 0
    
    @staticmethod
    def update_password(db, user_id, new_password):
        """
        更新用户密码
        
        Args:
            db: 数据库连接
            user_id: 用户ID
            new_password: 新密码
            
        Returns:
            bool: 更新是否成功
        """
        # 生成新的密码哈希
        password_hash = User.hash_password(new_password)
        
        # 执行更新
        cursor = db.cursor()
        cursor.execute(
            "UPDATE users SET password_hash = %s, updated_at = %s WHERE id = %s",
            (password_hash, datetime.now(), user_id)
        )
        db.commit()
        
        return cursor.rowcount > 0
    
    @staticmethod
    def delete(db, user_id):
        """
        删除用户
        
        Args:
            db: 数据库连接
            user_id: 用户ID
            
        Returns:
            bool: 删除是否成功
        """
        cursor = db.cursor()
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        db.commit()
        
        return cursor.rowcount > 0
    
    @staticmethod
    def hash_password(password):
        """
        对密码进行哈希
        
        Args:
            password: 明文密码
            
        Returns:
            str: 密码哈希值
        """
        # 生成盐值并对密码进行哈希
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password_hash, password):
        """
        验证密码
        
        Args:
            password_hash: 存储的密码哈希值
            password: 待验证的明文密码
            
        Returns:
            bool: 密码是否匹配
        """
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
