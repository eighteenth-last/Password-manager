"""
密码管理API路由
"""
from flask import jsonify, request, current_app
import csv
import io
from datetime import datetime
from models.password import Password
from utils.db import get_db
from utils.auth import token_required
from . import api_bp

@api_bp.route('/add', methods=['POST', 'OPTIONS'])
@token_required
def add_password(current_user):
    # 处理OPTIONS请求
    if request.method == 'OPTIONS':
        return '', 204
    """添加新密码
    
    Args:
        current_user: 当前用户对象，由token_required装饰器提供
        
    Returns:
        JSON响应
    """
    data = request.get_json()
    
    # 验证必要字段
    if not all(k in data for k in ['domain', 'username', 'password']):
        return jsonify({'message': '缺少必要字段'}), 400
    
    # 获取字段
    domain = data.get('domain')
    url = data.get('url', '')
    username = data.get('username')
    password = data.get('password')
    notes = data.get('notes', '')
    
    try:
        # 获取数据库连接
        db = get_db()
        
        # 检查是否已存在相同的记录
        existing = Password.find_by_domain_and_username(db, current_user['id'], domain, username)
        if existing:
            return jsonify({'message': f'已存在相同的账号记录: {domain} - {username}'}), 409
        
        # 创建新密码记录
        new_password = Password.create(db, current_user['id'], domain, url, username, password, notes)
        
        # 返回成功信息
        return jsonify({
            'message': '密码添加成功',
            'password': new_password.to_dict()
        }), 201
    except Exception as e:
        current_app.logger.error(f"添加密码失败: {str(e)}")
        return jsonify({'message': '添加密码失败'}), 500

@api_bp.route('/passwords', methods=['GET', 'POST', 'OPTIONS'])
@token_required
def list_passwords(current_user):
    """获取用户的所有密码或添加新密码
    
    Args:
        current_user: 当前用户对象，由token_required装饰器提供
        
    Returns:
        JSON响应，包含密码列表或新添加的密码
    """
    # 处理OPTIONS请求
    if request.method == 'OPTIONS':
        return '', 204
        
    # 处理POST请求 - 添加新密码
    if request.method == 'POST':
        data = request.get_json()
        
        # 验证必要字段
        if not all(k in data for k in ['domain', 'username', 'password']):
            return jsonify({'message': '缺少必要字段'}), 400
        
        # 获取字段
        domain = data.get('domain')
        url = data.get('url', '')
        username = data.get('username')
        password = data.get('password')
        notes = data.get('notes', '')
        
        try:
            # 获取数据库连接
            db = get_db()
            
            # 检查是否已存在相同的记录
            existing = Password.find_by_domain_and_username(db, current_user['id'], domain, username)
            if existing:
                return jsonify({'message': f'已存在相同的账号记录: {domain} - {username}'}), 409
            
            # 创建新密码记录
            new_password = Password.create(db, current_user['id'], domain, url, username, password, notes)
            
            # 返回成功信息
            return jsonify({
                'message': '密码添加成功',
                'password': new_password.to_dict()
            }), 201
        except Exception as e:
            current_app.logger.error(f"添加密码失败: {str(e)}")
            return jsonify({'message': '添加密码失败'}), 500
        
    try:
        # 获取数据库连接
        db = get_db()
        
        # 查询用户的所有密码
        passwords = Password.find_by_user_id(db, current_user['id'])
        
        # 密码已经是字典格式，无需转换
        password_list = passwords
        
        # 返回结果
        return jsonify({'passwords': password_list}), 200
    except Exception as e:
        current_app.logger.error(f"获取密码列表失败: {str(e)}")
        return jsonify({'message': '获取密码列表失败'}), 500
        
@api_bp.route('/passwords/shared', methods=['GET', 'OPTIONS'])
@token_required
def list_shared_passwords(current_user):
    """获取共享给用户的密码
    
    Args:
        current_user: 当前用户对象，由token_required装饰器提供
        
    Returns:
        JSON响应，包含共享密码列表
    """
    # 处理OPTIONS请求
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        # 获取数据库连接
        db = get_db()
        
        # 查询共享密码
        shared_passwords = Password.find_shared_with_user(db, current_user['id'])
        
        # 返回结果
        return jsonify({'sharedPasswords': shared_passwords}), 200
    except Exception as e:
        current_app.logger.error(f"获取共享密码列表失败: {str(e)}")
        return jsonify({'message': '获取共享密码列表失败'}), 500

@api_bp.route('/passwords/<password_id>', methods=['GET', 'PUT', 'DELETE', 'OPTIONS'])
@token_required
def handle_single_password(current_user, password_id):
    """处理单个密码的获取、更新、删除操作
    
    Args:
        current_user: 当前用户对象，由token_required装饰器提供
        password_id: 密码ID
        
    Returns:
        JSON响应
    """
    # 处理OPTIONS请求
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        # 获取数据库连接
        db = get_db()
        
        # 查找密码记录
        password_record = Password.find_by_id(db, password_id)
        if not password_record:
            return jsonify({'message': '密码记录不存在'}), 404
            
        # 检查是否属于当前用户
        if password_record['user_id'] != current_user['id']:
            return jsonify({'message': '无权操作此密码记录'}), 403
        
        # GET请求 - 获取密码详情
        if request.method == 'GET':
            return jsonify(password_record), 200
            
        # DELETE请求 - 删除密码
        elif request.method == 'DELETE':
            Password.delete(db, password_id)
            return jsonify({'message': '密码删除成功'}), 200
            
        # PUT请求 - 更新密码
        elif request.method == 'PUT':
            data = request.get_json()
            
            # 获取要更新的字段
            domain = data.get('domain')
            url = data.get('url', '')
            username = data.get('username')
            password = data.get('password')
            
            # 更新记录
            updated = Password.update(db, password_id, domain, url, username, password)
            
            # 返回更新后的密码记录
            updated_record = Password.find_by_id(db, password_id)
            return jsonify(updated_record), 200
            
    except Exception as e:
        current_app.logger.error(f"处理密码操作失败: {str(e)}")
        return jsonify({'message': f'处理密码操作失败: {str(e)}'}), 500


@api_bp.route('/update/<int:password_id>', methods=['PUT', 'OPTIONS'])
@token_required
def update_password(current_user, password_id):
    # 处理OPTIONS请求
    if request.method == 'OPTIONS':
        return '', 204
    """更新密码
    
    Args:
        current_user: 当前用户对象，由token_required装饰器提供
        password_id: 密码ID
        
    Returns:
        JSON响应
    """
    data = request.get_json()
    
    # 获取要更新的字段
    domain = data.get('domain')
    url = data.get('url')
    username = data.get('username')
    password = data.get('password')
    notes = data.get('notes')
    
    try:
        # 获取数据库连接
        db = get_db()
        
        # 查找密码记录
        password_record = Password.find_by_id(db, password_id)
        if not password_record:
            return jsonify({'message': '密码记录不存在'}), 404
            
        # 检查是否属于当前用户
        if password_record.user_id != current_user['id']:
            return jsonify({'message': '无权操作此密码记录'}), 403
            
        # 更新记录
        updated = Password.update(db, password_id, domain, url, username, password, notes)
        
        # 返回结果
        return jsonify({
            'message': '密码更新成功',
            'password': updated.to_dict()
        }), 200
    except Exception as e:
        current_app.logger.error(f"更新密码失败: {str(e)}")
        return jsonify({'message': '更新密码失败'}), 500

@api_bp.route('/delete/<int:password_id>', methods=['DELETE', 'OPTIONS'])
@token_required
def delete_password(current_user, password_id):
    # 处理OPTIONS请求
    if request.method == 'OPTIONS':
        return '', 204
    """删除密码
    
    Args:
        current_user: 当前用户对象，由token_required装饰器提供
        password_id: 密码ID
        
    Returns:
        JSON响应
    """
    try:
        # 获取数据库连接
        db = get_db()
        
        # 查找密码记录
        password_record = Password.find_by_id(db, password_id)
        if not password_record:
            return jsonify({'message': '密码记录不存在'}), 404
            
        # 检查是否属于当前用户
        if password_record.user_id != current_user['id']:
            return jsonify({'message': '无权操作此密码记录'}), 403
            
        # 删除记录
        Password.delete(db, password_id)
        
        # 返回结果
        return jsonify({'message': '密码删除成功'}), 200
    except Exception as e:
        current_app.logger.error(f"删除密码失败: {str(e)}")
        return jsonify({'message': '删除密码失败'}), 500

@api_bp.route('/passwords/sync', methods=['POST', 'OPTIONS'])
@token_required
def sync_passwords(current_user):
    """同步密码
    
    Args:
        current_user: 当前用户对象，由token_required装饰器提供
        
    Returns:
        JSON响应
    """
    # 处理OPTIONS请求
    if request.method == 'OPTIONS':
        return '', 204
        
    data = request.get_json()
    
    if not data or not isinstance(data.get('passwords'), list):
        return jsonify({'message': '请求格式错误，应包含密码数组'}), 400
        
    try:
        # 获取数据库连接
        db = get_db()
        
        # 获取客户端密码列表
        client_passwords = data.get('passwords', [])
        
        # 获取服务器上的密码列表
        server_passwords = Password.find_by_user_id(db, current_user['id'])
        
        # 创建服务器密码的ID映射
        server_password_map = {p['id']: p for p in server_passwords}
        
        # 处理同步逻辑
        updated = []
        deleted = []
        
        # 更新或添加密码
        for client_password in client_passwords:
            password_id = client_password.get('id')
            
            # 如果服务器上有此密码，检查是否需要更新
            if password_id and password_id in server_password_map:
                server_password = server_password_map[password_id]
                client_updated_at = datetime.fromisoformat(client_password.get('updated_at'))
                server_updated_at = datetime.fromisoformat(server_password['updated_at'])
                
                # 如果客户端版本更新，则更新服务器版本
                if client_updated_at > server_updated_at:
                    Password.update(
                        db, 
                        password_id, 
                        client_password.get('domain'), 
                        client_password.get('url', ''), 
                        client_password.get('username'), 
                        client_password.get('password'),
                        client_password.get('notes', '')
                    )
                    updated.append(password_id)
            # 如果服务器上没有此密码，添加新密码
            else:
                new_password = Password.create(
                    db, 
                    current_user['id'], 
                    client_password.get('domain'), 
                    client_password.get('url', ''), 
                    client_password.get('username'), 
                    client_password.get('password'),
                    client_password.get('notes', '')
                )
                updated.append(new_password.id)
        
        # 获取更新后的服务器密码列表
        updated_server_passwords = Password.find_by_user_id(db, current_user['id'])
        
        # 返回结果
        return jsonify({
            'message': '密码同步成功',
            'serverPasswords': updated_server_passwords,
            'updated': updated,
            'deleted': deleted
        }), 200
    except Exception as e:
        current_app.logger.error(f"同步密码失败: {str(e)}")
        return jsonify({'message': '同步密码失败'}), 500

@api_bp.route('/passwords/shared/sync', methods=['POST', 'OPTIONS'])
@token_required
def sync_shared_passwords(current_user):
    """同步共享密码
    
    Args:
        current_user: 当前用户对象，由token_required装饰器提供
        
    Returns:
        JSON响应
    """
    # 处理OPTIONS请求
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        # 获取数据库连接
        db = get_db()
        
        # 获取共享密码
        shared_passwords = Password.find_shared_with_user(db, current_user['id'])
        
        # 返回结果
        return jsonify({
            'message': '共享密码同步成功',
            'sharedPasswords': shared_passwords
        }), 200
    except Exception as e:
        current_app.logger.error(f"同步共享密码失败: {str(e)}")
        return jsonify({'message': '同步共享密码失败'}), 500

@api_bp.route('/import', methods=['POST'])
@token_required
def import_passwords(current_user):
    """导入密码（多条记录）
    
    Args:
        current_user: 当前用户对象，由token_required装饰器提供
        
    Returns:
        JSON响应
    """
    data = request.get_json()
    return _process_imports(current_user, data)


def _process_imports(current_user, data):
    """
    内部处理函数：对给定 data（包含 passwords 数组）执行导入逻辑并返回 Flask Response
    """
    if not isinstance(data, dict) or 'passwords' not in data or not isinstance(data['passwords'], list):
        return jsonify({'message': '请求格式错误，应包含密码数组'}), 400

    # 获取是否强制导入参数
    force_import = data.get('forceImport', False)

    try:
        # 获取数据库连接
        db = get_db()

        # 用于记录操作结果
        imported_count = 0
        skipped_count = 0
        skipped_details = []
        imported_passwords = []

        # 获取当前用户的所有密码
        current_passwords = Password.find_by_user_id(db, current_user['id'])
        current_passwords_map = {f"{p['domain']}:{p['encrypted_username']}": p for p in current_passwords}

        # 处理每条记录
        for item in data['passwords']:
            # 验证必要字段
            if not all(k in item for k in ['domain', 'username', 'password']):
                skipped_details.append(f"缺少必要字段 - {item.get('domain', 'Unknown')}")
                skipped_count += 1
                continue

            domain = item['domain']
            username = item['username']
            password = item['password']
            url = item.get('url', '')
            notes = item.get('notes', '')

            # 生成唯一键
            key = f"{domain}:{username}"

            # 检查是否已存在
            if key in current_passwords_map:
                if force_import:
                    # 更新现有记录
                    existing = current_passwords_map[key]
                    updated_password = Password.update(db, existing.id, domain, url, username, password, notes)
                    imported_passwords.append(updated_password.to_dict())
                    imported_count += 1
                else:
                    skipped_details.append(f"已存在相同记录: {domain} - {username}")
                    skipped_count += 1
            else:
                # 添加新记录
                new_password = Password.create(db, current_user['id'], domain, url, username, password, notes)
                imported_passwords.append(new_password.to_dict())
                imported_count += 1

        # 返回结果
        return jsonify({
            'message': f'导入完成，成功导入 {imported_count} 条记录，跳过 {skipped_count} 条记录',
            'importedCount': imported_count,
            'skippedCount': skipped_count,
            'skippedDetails': skipped_details,
            'importedPasswords': imported_passwords
        }), 200
    except Exception as e:
        current_app.logger.error(f"导入密码失败: {str(e)}")
        return jsonify({'message': '导入密码失败'}), 500

@api_bp.route('/import/txt', methods=['POST', 'OPTIONS'])
@api_bp.route('/txt_import', methods=['POST', 'OPTIONS'])
@token_required
def import_txt_passwords(current_user):
    """从TXT文件导入密码（一行一个记录，格式为"网站名 用户名 密码"，空格分隔）
    
    Args:
        current_user: 当前用户对象，由token_required装饰器提供
        
    Returns:
        JSON响应
    """
    # 处理 OPTIONS 预检请求
    if request.method == 'OPTIONS':
        return '', 204

    # 如果前端以 JSON 方式发送 passwords 数组（前端 importPasswords 使用此方式），则复用 import_passwords 逻辑
    if request.is_json:
        try:
            data = request.get_json()
        except Exception:
            data = None

        if isinstance(data, dict) and 'passwords' in data:
            # 直接调用 _process_imports 函数处理导入逻辑
            return _process_imports(current_user, data)

    # 检查是否有文件上传
    if 'file' not in request.files:
        return jsonify({'message': '未找到文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': '未选择文件'}), 400
    
    # 检查文件扩展名
    if not file.filename.lower().endswith('.txt'):
        return jsonify({'message': '文件类型不支持，请上传TXT文件'}), 400
    
    force_import = request.form.get('forceImport', 'false').lower() == 'true'
    
    try:
        # 读取文件内容
        content = file.read().decode('utf-8')
        lines = content.split('\n')
        
        passwords = []
        errors = []
        
        # 解析每一行
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # 分割行内容
            parts = line.split()
            
            # 验证格式
            if len(parts) < 3:
                errors.append(f"第{i+1}行格式错误: {line}")
                continue
            
            domain = parts[0]
            username = parts[1]
            password = ' '.join(parts[2:])  # 密码可能包含空格
            
            passwords.append({
                'domain': domain,
                'url': domain if '.' in domain else '',
                'username': username,
                'password': password
            })
        
        # 如果没有有效数据，返回错误
        if not passwords:
            return jsonify({
                'message': '未找到有效的密码记录',
                'importedCount': 0,
                'skippedCount': 0,
                'errors': errors
            }), 400
        
        # 调用导入API
        db = get_db()
        imported_count = 0
        skipped_count = 0
        skipped_details = []
        imported_passwords = []
        
        # 获取当前用户的所有密码
        current_passwords = Password.find_by_user_id(db, current_user['id'])
        current_passwords_map = {f"{p['domain']}:{p['encrypted_username']}": p for p in current_passwords}
        
        # 处理每条记录
        for item in passwords:
            domain = item['domain']
            username = item['username']
            password = item['password']
            url = item.get('url', '')
            notes = item.get('notes', '')
            
            # 生成唯一键
            key = f"{domain}:{username}"
            
            # 检查是否已存在
            if key in current_passwords_map:
                if force_import:
                    # 更新现有记录
                    existing = current_passwords_map[key]
                    updated_password = Password.update(db, existing.id, domain, url, username, password, notes)
                    imported_passwords.append(updated_password.to_dict())
                    imported_count += 1
                else:
                    skipped_details.append(f"已存在相同记录: {domain} - {username}")
                    skipped_count += 1
            else:
                # 添加新记录
                new_password = Password.create(db, current_user['id'], domain, url, username, password, notes)
                imported_passwords.append(new_password.to_dict())
                imported_count += 1
        
        # 返回结果
        return jsonify({
            'message': f'导入完成，成功导入 {imported_count} 条记录，跳过 {skipped_count} 条记录',
            'importedCount': imported_count,
            'skippedCount': skipped_count,
            'skippedDetails': skipped_details,
            'importedPasswords': imported_passwords,
            'errors': errors
        })
    except Exception as e:
        current_app.logger.error(f"导入密码失败: {str(e)}")
        return jsonify({'message': '导入密码失败'}), 500

@api_bp.route('/batch_delete', methods=['POST', 'OPTIONS'])
@token_required
def batch_delete_passwords(current_user):
    """批量删除密码
    
    Args:
        current_user: 当前用户对象，由token_required装饰器提供
        
    Returns:
        JSON响应
    """
    # 处理 OPTIONS 预检请求
    if request.method == 'OPTIONS':
        return '', 204

    try:
        data = request.get_json()
        
        # 验证请求数据
        if not isinstance(data, dict) or 'password_ids' not in data:
            return jsonify({'message': '请求格式错误，应包含password_ids数组'}), 400
        
        password_ids = data['password_ids']
        if not isinstance(password_ids, list) or len(password_ids) == 0:
            return jsonify({'message': '密码ID列表不能为空'}), 400
        
        # 获取数据库连接
        db = get_db()
        
        # 记录操作结果
        deleted_count = 0
        failed_count = 0
        failed_details = []
        
        # 批量删除密码
        for password_id in password_ids:
            try:
                # 查找密码记录
                password_record = Password.find_by_id(db, password_id)
                if not password_record:
                    failed_details.append(f"密码记录不存在: {password_id}")
                    failed_count += 1
                    continue
                    
                # 检查是否属于当前用户
                if password_record['user_id'] != current_user['id']:
                    failed_details.append(f"无权删除密码: {password_id}")
                    failed_count += 1
                    continue
                
                # 删除密码
                if Password.delete(db, password_id):
                    deleted_count += 1
                else:
                    failed_details.append(f"删除失败: {password_id}")
                    failed_count += 1
                    
            except Exception as e:
                current_app.logger.error(f"删除密码 {password_id} 失败: {str(e)}")
                failed_details.append(f"删除失败: {password_id} - {str(e)}")
                failed_count += 1
        
        # 返回结果
        return jsonify({
            'message': f'批量删除完成，成功删除 {deleted_count} 条记录，失败 {failed_count} 条记录',
            'deletedCount': deleted_count,
            'failedCount': failed_count,
            'failedDetails': failed_details
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"批量删除密码失败: {str(e)}")
        return jsonify({'message': '批量删除密码失败'}), 500

@api_bp.route('/csv_import', methods=['POST', 'OPTIONS'])
def csv_import_passwords():
    """从CSV文件导入密码 - 此API保留仅用于向后兼容，实际导入工作已移至前端处理"""
    from flask import current_app, make_response
    
    # 处理预检请求
    if request.method == 'OPTIONS':
        response = make_response()
        # 根据请求的Origin返回相同的值
        origin = request.headers.get('Origin', '*')
        response.headers.add('Access-Control-Allow-Origin', origin)
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Max-Age', '3600')
        return response
    
    # 记录调用信息
    current_app.logger.info("CSV导入API已被调用，但此功能已移至前端处理")
    
    # 返回提示信息 - CSV导入现在由前端直接处理，使用与TXT导入相同的API
    return jsonify({
        'message': '注意：CSV导入现在由前端直接处理',
        'importedCount': 0,
        'skippedCount': 0,
        'skippedDetails': []
    })