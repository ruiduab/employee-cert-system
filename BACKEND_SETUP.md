# 后端 API 服务部署指南

## 📋 目录

1. [系统要求](#系统要求)
2. [环境配置](#环境配置)
3. [数据库初始化](#数据库初始化)
4. [安装依赖](#安装依赖)
5. [启动服务](#启动服务)
6. [API 文档](#api-文档)
7. [前后端联调](#前后端联调)

---

## 系统要求

- **Node.js**: >= 14.0.0
- **npm**: >= 6.0.0
- **MySQL**: >= 5.7 或 8.0
- **操作系统**: Linux / macOS / Windows

---

## 环境配置

### Step 1: 复制配置文件

```bash
cp .env.example .env
```

### Step 2: 编辑 `.env` 文件

```env
# 服务器端口
PORT=8000

# MySQL 数据库配置
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=lenovo_cert
DB_PORT=3306

# CORS 配置（前端访问地址）
CORS_ORIGIN=http://localhost:3000,http://101.132.158.166:8082,http://101.132.158.166:8083
```

### Step 3: 验证配置

```bash
# 测试 MySQL 连接
mysql -u root -p -h localhost -P 3306
```

---

## 数据库初始化

### Step 1: 创建数据库和表

```bash
# 方式1：使用初始化脚本（推荐）
mysql -u root -p < database-init.sql

# 方式2：手动创建
mysql -u root -p
mysql> CREATE DATABASE lenovo_cert CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
mysql> USE lenovo_cert;
mysql> [复制 database-init.sql 中的所有 CREATE TABLE 语句]
```

### Step 2: 验证数据库

```bash
mysql -u root -p
mysql> USE lenovo_cert;
mysql> SHOW TABLES;
```

**应该看到以下表**：
- users
- user_cert_status
- certification_history
- realname_auth
- employee_auth
- material_auth
- audit_log

### Step 3: 插入示例数据

```bash
# 数据库初始化脚本已包含示例数据
# 验证示例数据是否插入成功
mysql -u root -p
mysql> USE lenovo_cert;
mysql> SELECT * FROM users;
mysql> SELECT * FROM user_cert_status;
```

### Step 4: 导入岗位和行业分类数据（新增）

**可选但推荐**：导入标准化的岗位库和行业分类数据。

#### 方式 A：使用 Python 导入脚本（推荐）

```bash
# 1. 安装依赖
pip install mysql-connector-python

# 2. 执行导入脚本
python3 import-positions-data.py \
  --host localhost \
  --user root \
  --password your_password \
  --database lenovo_cert
```

#### 方式 B：直接导入 SQL 文件

```bash
# 方式1：命令行
mysql -u root -p lenovo_cert < positions-database-init.sql

# 方式2：MySQL 客户端
mysql> USE lenovo_cert;
mysql> source positions-database-init.sql;
```

#### 验证导入

```sql
-- 检查导入的数据
SELECT COUNT(*) as 行业分类数 FROM industries;
SELECT COUNT(*) as 职位分类数 FROM position_categories;
SELECT COUNT(*) as 标准岗位数 FROM standard_positions;

-- 查看样本岗位
SELECT name FROM standard_positions LIMIT 5;
```

**详见**: [POSITIONS_DATABASE_README.md](./POSITIONS_DATABASE_README.md)

---

## 安装依赖

```bash
# 进入项目目录
cd /path/to/lenovo-cert-system

# 安装 npm 依赖
npm install

# 验证安装
npm list
```

**关键依赖**：
- `express`: Web 框架
- `mysql2`: MySQL 数据库驱动
- `cors`: 跨域资源共享
- `dotenv`: 环境变量配置

---

## 启动服务

### 开发环境

```bash
# 使用 nodemon（自动重启）
npm run dev

# 或直接运行
node backend-api-server.js
```

**预期输出**：
```
🚀 认证系统后端服务已启动 (端口: 8000)
📍 API 地址: http://localhost:8000
   - GET  /api/user/cert-status - 获取用户认证状态
   - POST /api/auth/submit - 提交认证申请
   - GET  /api/user/cert-history - 获取认证历史
```

### 生产环境

```bash
# 设置环境变量
export NODE_ENV=production
export PORT=8000

# 启动服务（使用 PM2 进程管理）
npm install -g pm2
pm2 start backend-api-server.js --name "lenovo-cert-api"

# 查看日志
pm2 logs lenovo-cert-api

# 停止服务
pm2 stop lenovo-cert-api
```

---

## API 文档

### 1. 获取用户认证状态

**请求**：
```
GET /api/user/cert-status?uid=10001
```

**响应成功**：
```json
{
  "success": true,
  "status": "basic-certified",
  "certCount": 1,
  "lastCertData": {
    "company": "联想（北京）有限公司",
    "position": "产品经理",
    "industry": "互联网/信息技术",
    "specialty": "",
    "authMethod": "email"
  },
  "lastCertDate": "2026-04-15 14:30:00"
}
```

**状态说明**：
- `not-certified`: 未认证
- `basic-certified`: 已基础认证
- `specialist-certified`: 已完成专业认证

---

### 2. 提交认证申请

**请求**：
```
POST /api/auth/submit
Content-Type: application/json

{
  "flowType": "first",
  "certNumber": 1,
  "isUpgrade": false,
  "certType": "basic",
  "company": "联想（北京）有限公司",
  "position": "产品经理",
  "industry": "互联网/信息技术",
  "specialty": "",
  "authMethod": "email",
  "filePath": "/uploads/user_10001_cert_1.pdf",
  "fileName": "email_verify.pdf",
  "timestamp": "2026-04-15T14:30:00Z"
}
```

**响应成功**：
```json
{
  "success": true,
  "message": "认证申请已提交",
  "newStatus": "basic-certified",
  "certNumber": 1,
  "certId": 1713177000000
}
```

**参数说明**：
- `flowType`: 流程类型（first=首次, upgrade=升级, update=更新）
- `certNumber`: 认证次数
- `isUpgrade`: 是否为升级认证
- `certType`: 认证类型（basic 或 specialist_xxx）

---

### 3. 获取用户认证历史

**请求**：
```
GET /api/user/cert-history?uid=10001
```

**响应**：
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "uid": 10001,
      "cert_number": 1,
      "cert_type": "basic",
      "is_upgrade": 0,
      "company": "联想（北京）有限公司",
      "position": "产品经理",
      "industry": "互联网/信息技术",
      "auth_method": "email",
      "review_status": "approved",
      "submitted_at": "2026-04-15 14:30:00",
      "reviewed_at": "2026-04-15 15:00:00"
    }
  ]
}
```

---

### 4. 后台：获取员工列表

**请求**：
```
GET /api/admin/users?page=1&pageSize=50&status=all
```

**响应**：
```json
{
  "success": true,
  "data": [
    {
      "uid": 10001,
      "name": "张三",
      "phone": "13812345678",
      "email": "zhangsan@lenovo.com",
      "status": "basic-certified",
      "cert_count": 1,
      "current_cert_type": "basic",
      "last_cert_time": "2026-04-15 14:30:00"
    }
  ],
  "pagination": {
    "page": 1,
    "pageSize": 50,
    "total": 100,
    "totalPages": 2
  }
}
```

---

## 前后端联调

### 前端配置

在前端 HTML 文件中，确保 API 调用指向正确的后端地址：

```javascript
// 方式1：绝对 URL
fetch('http://localhost:8000/api/user/cert-status')

// 方式2：相对路径（需要 Nginx 反向代理）
fetch('/api/user/cert-status')
```

### Nginx 反向代理配置

```nginx
# 在 Nginx 配置中添加 API 代理
server {
    listen 8082;
    server_name _;

    # 前端静态文件
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ =404;
    }

    # API 代理
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 测试 API

```bash
# 1. 测试健康检查
curl http://localhost:8000/health

# 2. 测试获取用户状态
curl "http://localhost:8000/api/user/cert-status?uid=10001"

# 3. 测试提交认证
curl -X POST http://localhost:8000/api/auth/submit \
  -H "Content-Type: application/json" \
  -d '{
    "flowType": "first",
    "certNumber": 1,
    "isUpgrade": false,
    "certType": "basic",
    "company": "联想",
    "position": "工程师",
    "industry": "互联网/信息技术",
    "authMethod": "email",
    "timestamp": "2026-04-15T14:30:00Z"
  }'

# 4. 测试获取认证历史
curl "http://localhost:8000/api/user/cert-history?uid=10001"
```

---

## 常见问题

### Q1: 启动时报 "ECONNREFUSED" 错误

**原因**: 数据库连接失败

**解决**:
1. 检查 MySQL 是否运行: `mysql -u root -p`
2. 检查 `.env` 中的数据库配置
3. 检查数据库是否已创建: `SHOW DATABASES;`

### Q2: 表不存在错误

**原因**: 数据库初始化失败

**解决**:
```bash
# 重新运行初始化脚本
mysql -u root -p < database-init.sql

# 验证表
mysql -u root -p
mysql> USE lenovo_cert;
mysql> SHOW TABLES;
```

### Q3: CORS 错误

**原因**: 前端地址未配置在 `CORS_ORIGIN` 中

**解决**: 编辑 `.env` 文件，添加前端地址

```env
CORS_ORIGIN=http://localhost:3000,http://101.132.158.166:8082,http://101.132.158.166:8083
```

### Q4: 如何修改认证审核状态

暂时的解决方案是直接修改数据库：

```sql
-- 批准某个认证
UPDATE certification_history 
SET review_status = 'approved', reviewer_id = 1, reviewed_at = NOW() 
WHERE id = 1;

-- 驳回某个认证
UPDATE certification_history 
SET review_status = 'rejected', reviewer_id = 1, review_remark = '资料不完整', reviewed_at = NOW() 
WHERE id = 2;
```

后续版本会添加完整的审核 API。

---

## 部署到阿里云

### 步骤 1: SSH 连接到服务器

```bash
ssh root@101.132.158.166
```

### 步骤 2: 安装 Node.js 和 npm

```bash
# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt-get install -y nodejs

# 验证
node -v
npm -v
```

### 步骤 3: 安装 MySQL

```bash
# 如果未安装
sudo apt-get install -y mysql-server

# 启动 MySQL
sudo systemctl start mysql
```

### 步骤 4: 上传代码并初始化

```bash
# 在本地
scp backend-api-server.js package.json database-init.sql .env.example root@101.132.158.166:/opt/lenovo-cert/

# 在远程服务器
cd /opt/lenovo-cert
cp .env.example .env
npm install
mysql -u root -p < database-init.sql
```

### 步骤 5: 启动服务（PM2）

```bash
# 全局安装 PM2
npm install -g pm2

# 启动应用
pm2 start backend-api-server.js --name "lenovo-cert"

# 设置开机自启
pm2 startup
pm2 save

# 查看状态
pm2 status
pm2 logs
```

---

## 监控和维护

### 查看日志

```bash
pm2 logs lenovo-cert-api
pm2 logs lenovo-cert-api --lines 100
pm2 logs lenovo-cert-api --follow
```

### 性能监控

```bash
pm2 monit
```

### 备份数据库

```bash
# 定期备份（建议每天一次）
mysqldump -u root -p lenovo_cert > backup_$(date +%Y%m%d).sql

# 恢复备份
mysql -u root -p lenovo_cert < backup_20260415.sql
```

---

**更新日期**: 2026-04-15  
**维护者**: 技术团队
