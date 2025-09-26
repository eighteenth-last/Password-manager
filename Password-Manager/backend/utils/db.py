"""
数据库工具模块
处理数据库连接和初始化
"""

import mysql.connector
from flask import current_app, g
import os

def get_db():
    """
    获取数据库连接
    
    Returns:
        MySQLConnection: 数据库连接对象
    """
    if 'db' not in g:
        try:
            # 尝试连接到指定数据库
            g.db = mysql.connector.connect(
                host=os.getenv('DB_HOST', 'localhost'), #数据库地址
                user=os.getenv('DB_USER', 'root'), # 数据库用户名
                password=os.getenv('DB_PASSWORD', '你的数据库密码'),  # 数据库密码
                database=os.getenv('DB_NAME', 'password_manager')  # 数据库名
            )
        except mysql.connector.Error as err:
            if err.errno == 1049:  # 数据库不存在错误
                # 连接到MySQL服务器（不指定数据库）
                connection = mysql.connector.connect(
                    host=os.getenv('DB_HOST', 'localhost'),  # 数据库地址
                    user=os.getenv('DB_USER', 'root'),  # 数据库用户名
                    password=os.getenv('DB_PASSWORD', '你的数据库密码')  # 数据库密码
                )
                cursor = connection.cursor()
                
                # 创建数据库
                db_name = os.getenv('DB_NAME', 'password_manager')  # 数据库名
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
                connection.commit()
                cursor.close()
                connection.close()
                
                # 重新连接到新创建的数据库
                g.db = mysql.connector.connect(
                    host=os.getenv('DB_HOST', 'localhost'),  # 地址
                    user=os.getenv('DB_USER', 'root'),  # 用户
                    password=os.getenv('DB_PASSWORD', '你的数据库密码'), #密码
                    database=db_name
                )
            else:
                # 其他错误，直接抛出
                raise
    
    return g.db

def close_db(e=None):
    """
    关闭数据库连接
    
    Args:
        e: 异常对象（可选）
    """
    db = g.pop('db', None)
    
    if db is not None:
        db.close()

def init_db():
    """
    初始化数据库
    创建必要的表
    """
    db = get_db()
    cursor = db.cursor()
    
    # 创建用户表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id VARCHAR(36) PRIMARY KEY,
        email VARCHAR(100) NOT NULL UNIQUE,
        password_hash VARCHAR(255) NOT NULL,
        master_key_encrypted TEXT,
        created_at DATETIME NOT NULL,
        updated_at DATETIME NOT NULL
    )
    """)
    
    # 创建密码表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS passwords (
        id VARCHAR(36) PRIMARY KEY,
        user_id VARCHAR(36) NOT NULL,
        domain VARCHAR(255) NOT NULL,
        website_url VARCHAR(500) NOT NULL,
        encrypted_username TEXT NOT NULL,
        encrypted_password TEXT NOT NULL,
        created_at DATETIME NOT NULL,
        updated_at DATETIME NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)
    
    # 创建账号绑定表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS account_bindings (
        id VARCHAR(36) PRIMARY KEY,
        account_a_id VARCHAR(36) NOT NULL,
        account_b_id VARCHAR(36) NOT NULL,
        binding_status ENUM('pending', 'active') NOT NULL,
        permissions ENUM('read', 'write') NOT NULL,
        created_at DATETIME NOT NULL,
        updated_at DATETIME NOT NULL,
        FOREIGN KEY (account_a_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (account_b_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)
    
    # 提交事务
    db.commit()
    
    current_app.logger.info('数据库初始化完成')

def init_app(app):
    """
    初始化应用
    注册数据库关闭函数
    
    Args:
        app: Flask应用实例
    """
    app.teardown_appcontext(close_db)
