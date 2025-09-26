# API模块

本目录包含所有API路由模块，按功能分类组织。

## 文件结构

- `__init__.py`: 定义API蓝图并导入所有路由模块
- `auth_routes.py`: 用户认证相关API（注册、登录、用户信息）
- `password_routes.py`: 密码管理相关API（增删改查、同步、导入）
- `binding_routes.py`: 账号绑定相关API（绑定、解绑、权限控制） 
- `health_routes.py`: 系统健康检查API

## 使用方法

在app.py中注册API蓝图:

```python
from api import api_bp
app.register_blueprint(api_bp, url_prefix='/api')
```

## API路由列表

### 认证API
- `/api/register` (POST): 用户注册
- `/api/login` (POST): 用户登录
- `/api/user` (GET): 获取当前用户信息

### 密码API
- `/api/passwords` (GET): 获取用户的所有密码
- `/api/passwords` (POST): 添加新密码
- `/api/passwords/sync` (POST): 同步密码
- `/api/passwords/<password_id>` (PUT): 更新密码
- `/api/passwords/<password_id>` (DELETE): 删除密码
- `/api/txt_import` (POST): 导入密码

### 账号绑定API
- `/api/accounts/bind` (POST): 发起账号绑定请求
- `/api/accounts/bindings` (GET): 获取绑定列表
- `/api/accounts/bindings/<binding_id>/accept` (POST): 接受绑定请求
- `/api/accounts/bindings/<binding_id>/reject` (POST): 拒绝绑定请求
- `/api/accounts/bindings/<binding_id>` (DELETE): 解除绑定关系
- `/api/accounts/bindings/<binding_id>/permissions` (PUT): 更新绑定权限

### 共享密码API
- `/api/passwords/shared` (GET): 获取共享密码
- `/api/passwords/shared/<password_id>` (PUT): 更新共享密码
- `/api/passwords/shared/sync` (POST): 同步共享密码

### 系统API
- `/api/health` (GET): 健康检查
