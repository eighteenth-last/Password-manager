"""
认证工具模块
处理JWT令牌生成和验证
"""

import jwt
from functools import wraps
from flask import request, jsonify, current_app
from datetime import datetime, timedelta
from models.user import User
from utils.db import get_db
import inspect

def generate_token(user_id, secret_key, expiration_hours=24):
    """
    生成JWT令牌
    
    Args:
        user_id: 用户ID
        secret_key: 密钥
        expiration_hours: 过期时间（小时）
        
    Returns:
        str: JWT令牌
    """
    # 设置过期时间
    expiration = datetime.utcnow() + timedelta(hours=expiration_hours)
    
    # 创建载荷
    payload = {
        'user_id': user_id,
        'exp': expiration
    }
    
    # 生成令牌
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    
    return token

def token_required(f):
    """
    JWT令牌验证装饰器
    
    Args:
        f: 被装饰的函数
        
    Returns:
        function: 装饰后的函数
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # 对于OPTIONS请求，跳过令牌验证
        if request.method == 'OPTIONS':
            # 返回一个空函数来模拟装饰器行为
            from functools import partial
            return f(None, *args, **kwargs)
            
        token = None
        
        # 从请求头中获取令牌
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'message': '缺少访问令牌'}), 401
        
        try:
            # 解码令牌
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = payload['user_id']
            
            # 获取用户信息
            db = get_db()
            current_user = User.find_by_id(db, user_id)
            
            if not current_user:
                return jsonify({'message': '无效的访问令牌'}), 401
            
        except jwt.ExpiredSignatureError:
            return jsonify({'message': '访问令牌已过期'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': '无效的访问令牌'}), 401
        
        # 检查被装饰函数的参数签名
        signature = inspect.signature(f)
        if 'current_user' in signature.parameters:
            return f(current_user, *args, **kwargs)
        else:
            return f(*args, **kwargs)
    
    return decorated
