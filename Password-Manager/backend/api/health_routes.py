"""
健康检查相关API路由
"""

from flask import jsonify
from datetime import datetime
from . import api_bp

@api_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat()
    })