"""
账号绑定相关API路由
处理账号之间的绑定、解绑和权限管理
"""

from flask import jsonify, request, current_app
from . import api_bp
from models.user import User
from models.binding import Binding
from utils.db import get_db
from utils.auth import token_required

@api_bp.route('/accounts/bind', methods=['POST', 'OPTIONS'])
@token_required
def bind_account(current_user):
    # 处理OPTIONS请求
    if request.method == 'OPTIONS':
        return '', 204
    """账号绑定请求接口"""
    data = request.get_json()
    
    # 验证请求数据
    if not data or not data.get('targetEmail'):
        return jsonify({'message': '缺少必要字段'}), 400
    
    target_email = data.get('targetEmail')
    
    # 不能绑定自己
    if target_email == current_user['email']:
        return jsonify({'message': '不能绑定自己的账号'}), 400
    
    try:
        db = get_db()
        
        # 查找目标用户
        target_user = User.find_by_email(db, target_email)
        if not target_user:
            return jsonify({'message': '目标账号不存在'}), 404
        
        # 检查是否已经存在绑定关系
        existing_binding = Binding.find_by_account_ids(db, current_user['id'], target_user['id'])
        if existing_binding:
            return jsonify({'message': '已存在绑定关系'}), 409
        
        # 创建绑定请求
        binding_id = Binding.create(db, current_user['id'], target_user['id'], 'pending', 'read')
        
        return jsonify({
            'message': '绑定请求已发送',
            'binding_id': binding_id
        })
    except Exception as e:
        current_app.logger.error(f"发送绑定请求失败: {str(e)}")
        return jsonify({'message': '发送绑定请求失败'}), 500

@api_bp.route('/accounts/bindings', methods=['GET', 'OPTIONS'])
@token_required
def get_bindings(current_user):
    # 处理OPTIONS请求
    if request.method == 'OPTIONS':
        return '', 204
    """获取账号绑定列表接口"""
    try:
        db = get_db()
        
        # 获取当前用户的绑定关系
        bindings = Binding.find_by_user_id(db, current_user['id'])
        
        # 获取待处理的绑定请求
        pending_requests = Binding.find_pending_requests(db, current_user['id'])
        
        return jsonify({
            'bindings': bindings,
            'pendingRequests': pending_requests
        })
    except Exception as e:
        current_app.logger.error(f"获取绑定列表失败: {str(e)}")
        return jsonify({'message': '获取绑定列表失败'}), 500

@api_bp.route('/accounts/bindings/<binding_id>/accept', methods=['POST', 'OPTIONS'])
@token_required
def accept_binding(current_user, binding_id):
    # 处理OPTIONS请求
    if request.method == 'OPTIONS':
        return '', 204
    """接受绑定请求接口"""
    try:
        db = get_db()
        
        # 检查绑定请求是否存在且目标是当前用户
        binding = Binding.find_by_id(db, binding_id)
        if not binding or binding['account_b_id'] != current_user['id'] or binding['binding_status'] != 'pending':
            return jsonify({'message': '绑定请求不存在或无权限接受'}), 404
        
        # 更新绑定状态为活动
        Binding.update_status(db, binding_id, 'active')
        
        return jsonify({'message': '已接受绑定请求'})
    except Exception as e:
        current_app.logger.error(f"接受绑定请求失败: {str(e)}")
        return jsonify({'message': '接受绑定请求失败'}), 500

@api_bp.route('/accounts/bindings/<binding_id>/reject', methods=['POST', 'OPTIONS'])
@token_required
def reject_binding(current_user, binding_id):
    # 处理OPTIONS请求
    if request.method == 'OPTIONS':
        return '', 204
    """拒绝绑定请求接口"""
    try:
        db = get_db()
        
        # 检查绑定请求是否存在且目标是当前用户
        binding = Binding.find_by_id(db, binding_id)
        if not binding or binding['account_b_id'] != current_user['id'] or binding['binding_status'] != 'pending':
            return jsonify({'message': '绑定请求不存在或无权限拒绝'}), 404
        
        # 删除绑定请求
        Binding.delete(db, binding_id)
        
        return jsonify({'message': '已拒绝绑定请求'})
    except Exception as e:
        current_app.logger.error(f"拒绝绑定请求失败: {str(e)}")
        return jsonify({'message': '拒绝绑定请求失败'}), 500

@api_bp.route('/accounts/bindings/<binding_id>', methods=['DELETE', 'OPTIONS'])
@token_required
def unbind_account(current_user, binding_id):
    # 处理OPTIONS请求
    if request.method == 'OPTIONS':
        return '', 204
    """解除账号绑定接口"""
    try:
        db = get_db()
        
        # 检查绑定关系是否存在且属于当前用户
        binding = Binding.find_by_id(db, binding_id)
        if not binding or (binding['account_a_id'] != current_user['id'] and binding['account_b_id'] != current_user['id']):
            return jsonify({'message': '绑定关系不存在或无权限解除'}), 404
        
        # 删除绑定关系
        Binding.delete(db, binding_id)
        
        return jsonify({'message': '已解除绑定关系'})
    except Exception as e:
        current_app.logger.error(f"解除绑定关系失败: {str(e)}")
        return jsonify({'message': '解除绑定关系失败'}), 500

@api_bp.route('/accounts/bindings/<binding_id>/permissions', methods=['PUT', 'OPTIONS'])
@token_required
def update_binding_permissions(current_user, binding_id):
    # 处理OPTIONS请求
    if request.method == 'OPTIONS':
        return '', 204
    """更新绑定权限接口"""
    data = request.get_json()
    
    # 验证请求数据
    if not data or 'permissions' not in data:
        return jsonify({'message': '缺少必要字段'}), 400
    
    permissions = data.get('permissions')
    if permissions not in ['read', 'write']:
        return jsonify({'message': '无效的权限值'}), 400
    
    try:
        db = get_db()
        
        # 检查绑定关系是否存在且发起者是当前用户
        binding = Binding.find_by_id(db, binding_id)
        if not binding or binding['account_a_id'] != current_user['id']:
            return jsonify({'message': '绑定关系不存在或无权限更新'}), 404
        
        # 更新绑定权限
        Binding.update_permissions(db, binding_id, permissions)
        
        return jsonify({'message': '已更新绑定权限'})
    except Exception as e:
        current_app.logger.error(f"更新绑定权限失败: {str(e)}")
        return jsonify({'message': '更新绑定权限失败'}), 500