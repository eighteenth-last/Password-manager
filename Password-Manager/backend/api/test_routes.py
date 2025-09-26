"""
测试API路由
"""
from flask import jsonify
from . import api_bp

@api_bp.route('/test', methods=['GET', 'OPTIONS'])
def test_api():
    """测试API接口，不需要验证"""
    from flask import request
    if request.method == 'OPTIONS':
        return '', 204
    return jsonify({"message": "API测试成功"})
