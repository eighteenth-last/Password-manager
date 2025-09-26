"""
密码管家API模块
包含所有REST API路由
"""

from flask import Blueprint

# 创建蓝图
api_bp = Blueprint('api', __name__)

# 导入路由模块
from api.auth_routes import *
from api.password_routes import *
from api.binding_routes import *
from api.health_routes import *
from api.test_routes import *

# 注意: 在app.py中需要使用api_bp.route而不是app.route来注册路由