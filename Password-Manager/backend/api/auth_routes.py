"""
用户认证相关API路由
处理用户注册、登录和个人信息
"""

from flask import jsonify, request, current_app
from datetime import datetime
from . import api_bp
from models.user import User
from utils.db import get_db
from utils.auth import token_required, generate_token

@api_bp.route('/register', methods=['POST'])
def register():
    """用户注册接口"""
    data = request.get_json()
    
    # 验证请求数据
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': '缺少必要字段'}), 400
    
    email = data.get('email')
    password = data.get('password')
    
    # 检查邮箱是否已存在
    db = get_db()
    user = User.find_by_email(db, email)
    if user:
        return jsonify({'message': '该邮箱已注册'}), 409
    
    # 创建新用户
    try:
        user_id = User.create(db, email, password)
        
        # 生成访问令牌
        token = generate_token(
            user_id, 
            current_app.config['SECRET_KEY'], 
            current_app.config['JWT_EXPIRATION_HOURS']
        )
        
        return jsonify({
            'message': '注册成功',
            'user_id': user_id,
            'token': token,
            'expires_in': current_app.config['JWT_EXPIRATION_HOURS'] * 3600
        }), 201
    except Exception as e:
        current_app.logger.error(f"注册失败: {str(e)}")
        return jsonify({'message': '注册失败'}), 500

@api_bp.route('/login', methods=['POST'])
def login():
    """用户登录接口"""
    data = request.get_json()
    
    # 验证请求数据
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': '缺少必要字段'}), 400
    
    email = data.get('email')
    password = data.get('password')
    
    # 验证用户凭据
    db = get_db()
    user = User.find_by_email(db, email)
    
    if not user or not User.verify_password(user['password_hash'], password):
        return jsonify({'message': '邮箱或密码不正确'}), 401
    
    # 生成访问令牌
    token = generate_token(
        user['id'], 
        current_app.config['SECRET_KEY'], 
        current_app.config['JWT_EXPIRATION_HOURS']
    )
    
    return jsonify({
        'message': '登录成功',
        'user_id': user['id'],
        'email': user['email'],
        'token': token,
        'expires_in': current_app.config['JWT_EXPIRATION_HOURS'] * 3600
    })

@api_bp.route('/user', methods=['GET'])
@token_required
def get_user_info(current_user):
    """获取当前用户信息接口"""
    try:
        return jsonify({
            'id': current_user['id'],
            'email': current_user['email'],
            'created_at': current_user['created_at'].isoformat() if isinstance(current_user['created_at'], datetime) else current_user['created_at']
        })
    except Exception as e:
        current_app.logger.error(f"获取用户信息失败: {str(e)}")
        return jsonify({'message': '获取用户信息失败'}), 500