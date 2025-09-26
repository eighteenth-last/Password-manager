# 密码管家 - 多端同步密码管理系统

一个安全、高效的密码管理解决方案，支持多端同步、浏览器导入和账号绑定共享功能。

## 功能特点

- **多端同步**：通过云端账号实现多设备间密码库同步
- **浏览器导入**：支持从Chrome和Edge浏览器导入已保存的密码
- **TXT文件导入**：支持从格式化的TXT文件批量导入密码
- **CSV文件导入**：支持从CSV格式文件导入密码数据
- **账号绑定共享**：用户之间可以进行账号绑定，实现密码库共享（可控制读写权限）
- **本地加密**：所有密码在本地加密后再传输和存储，确保安全性
- **密码强度评估**：自动评估密码强度，并提供改进建议
- **随机密码生成**：内置随机密码生成器，创建高强度密码

## 项目结构

```
password-plugin/
├── backend/               # 后端API服务（Python/Flask）
│   ├── api/               # API路由模块
│   │   ├── __init__.py    # API蓝图定义
│   │   ├── auth_routes.py # 认证相关API
│   │   ├── password_routes.py # 密码管理API
│   │   ├── binding_routes.py  # 账号绑定API
│   │   └── health_routes.py   # 健康检查API
│   ├── models/            # 数据模型
│   ├── utils/             # 工具函数
│   └── app.py             # 应用入口
├── database/              # 数据库相关文件
│   ├── init.sql           # 数据库初始化脚本
│   ├── Chrome 密码.csv     # Chrome浏览器密码导出示例
│   └── Microsoft Edge 密码.csv # Edge浏览器密码导出示例
└── frontend/              # 前端管理界面（Vue3）
    ├── public/            # 静态资源
    ├── src/               # 源代码
    │   ├── assets/        # 资源文件
    │   ├── components/    # 组件
    │   │   └── BrowserImportDialog.vue # 浏览器导入对话框
    │   ├── router/        # 路由配置
    │   ├── store/         # Pinia状态管理
    │   │   └── passwords.js # 密码管理状态
    │   ├── utils/         # 工具函数
    │   │   └── axios.js   # HTTP请求配置
    │   ├── views/         # 页面视图
    │   │   ├── auth/      # 认证相关页面
    │   │   └── dashboard/ # 主控面板页面
    │   ├── App.vue        # 应用根组件
    │   └── main.js        # 应用入口
    ├── .env               # 环境变量
    └── package.json       # 依赖配置
```

## 安装与使用

### 后端服务器

1. 安装依赖：

```bash
cd backend
pip install -r requirements.txt
```

2. 配置环境变量：

```bash
# 复制示例配置文件
cp .env.example .env

# 编辑配置文件，设置数据库连接信息和密钥
```

3. 初始化数据库：

```bash
# 使用MySQL客户端执行初始化脚本
mysql -u root -p < database/init.sql
```

4. 启动服务器：

```bash
cd backend
python app.py
```

### 前端管理界面

1. 安装依赖：

```bash
cd frontend
npm install    # 安装依赖
```

2. 启动开发服务器：

```bash
npm run dev
```

3. 构建生产版本：

```bash
npm run build
```

## 使用指南

### 账号管理

1. 注册新账号：访问首页，点击"注册"，填写邮箱和密码
2. 登录系统：使用注册的邮箱和密码登录
3. 修改个人信息：在"个人中心"页面可修改个人信息

### 密码管理

1. 添加密码：点击"添加密码"按钮，填写网站名称、URL、用户名和密码
2. 编辑密码：在密码列表中点击"编辑"按钮修改密码信息
3. 删除密码：在密码列表中点击"删除"按钮删除密码
4. 复制密码：在密码列表中点击"复制密码"按钮将密码复制到剪贴板

### 导入功能

1. 从TXT导入：
   - 点击"导入TXT"按钮
   - 选择格式化的TXT文件（支持多种格式）
   - 点击"导入"或"全部导入"按钮

2. 从浏览器导入：
   - 点击"浏览器导入"按钮
   - 按照提示从Chrome或Edge浏览器导出密码为CSV文件
   - 选择CSV文件并点击"导入"按钮

### 账号绑定与共享

1. 绑定账号：在"账号绑定"页面输入对方邮箱，发送绑定请求
2. 接受绑定：在"账号绑定"页面查看并接受绑定请求
3. 设置权限：可设置绑定账号的权限（只读/读写）
4. 查看共享密码：在"密码管理"页面的"共享密码"标签页查看

## 安全说明

- 所有密码在传输和存储前都会使用AES-256算法进行加密
- 密码加密密钥不会传输或存储在服务器上，确保即使数据库被攻破也无法解密
- 支持HTTPS安全传输，防止中间人攻击
- 使用JWT进行身份验证，确保API调用安全

## 技术栈

- **后端**：Python + Flask + MySQL
- **前端**：Vue3 + Element Plus + Pinia
- **API通信**：RESTful API + JWT认证
- **加密技术**：AES-256-GCM + PBKDF2

## 开发指南

### API开发

- API路由采用模块化设计，位于`backend/api/`目录
- 使用Flask蓝图组织API结构
- 通过`@token_required`装饰器保护需要认证的API

### 前端开发

- 使用Vue3组合式API开发组件
- 使用Pinia进行状态管理
- 使用Element Plus构建UI界面
- 使用Vue Router进行路由管理

## 贡献指南

1. Fork本仓库
2. 创建功能分支：`git checkout -b feature/amazing-feature`
3. 提交更改：`git commit -m 'Add some amazing feature'`
4. 推送到分支：`git push origin feature/amazing-feature`
5. 提交Pull Request