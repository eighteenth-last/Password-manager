"""
密码管家 - 后端API
使用Flask框架实现RESTful API
"""

from flask import Flask, request, make_response
from flask_cors import CORS
import os
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler

# 导入自定义模块
from utils.db import init_db
from api import api_bp

# 加载环境变量
load_dotenv()

# 创建Flask应用
app = Flask(__name__)

# 配置
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_secret_key')
app.config['JWT_EXPIRATION_HOURS'] = int(os.getenv('JWT_EXPIRATION_HOURS', '24'))
app.config['DATABASE_URI'] = os.getenv('DATABASE_URI', 'mysql://user:password@localhost/password_manager')

# 配置CORS
CORS(app, 
     resources={r"/*": {
         "origins": ["http://localhost:3003", "http://localhost:3000", "http://127.0.0.1:3002", "http://127.0.0.1:3000"],
         "allow_headers": ["Content-Type", "Authorization", "Accept"],
         "expose_headers": ["Content-Type", "Authorization"],
         "methods": ["GET", "PUT", "POST", "DELETE", "OPTIONS"],
         "supports_credentials": True
     }})

# 添加响应日志中间件
@app.after_request
def after_request(response):
    # 记录响应状态和头部 (DEBUG)
    app.logger.info(f"响应状态: {response.status_code}")
    app.logger.info(f"响应头部: {dict(response.headers)}")
    
    return response

# 设置日志
if not os.path.exists('logs'):
    os.makedirs('logs')

# 使用时间戳创建唯一的日志文件名，避免多进程冲突
import time
log_file = f'logs/app_{int(time.time())}.log'

file_handler = RotatingFileHandler(log_file, maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('密码管家后端启动')

# 初始化数据库（容错）
with app.app_context():
    try:
        init_db()
    except Exception as e:
        # 记录初始化错误但不要阻止应用启动，防止前端收到 CONNECTION_REFUSED
        app.logger.error(f"数据库初始化失败: {str(e)}")

# 注册API蓝图，所有API路由前缀为/api
app.register_blueprint(api_bp, url_prefix='/api')

# 添加favicon路由
@app.route('/favicon.ico')
def favicon():
    from flask import send_from_directory
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    app.run(debug=os.getenv('DEBUG', 'False').lower() == 'true', host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
