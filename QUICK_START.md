# 快速开始指南

## 🚀 5分钟快速启动

### 前端和后端都更新完成了吗？

✅ **前端** (`employee-cert-complete.html`)
- 已集成用户状态检测
- 已支持升级认证流程
- 已支持更新认证流程
- 已集成返回首页的状态更新

✅ **后端** (`backend-api-server.js`)
- 已实现用户状态 API
- 已实现认证提交 API
- 已实现认证历史 API
- 已包含数据库初始化脚本

---

## 🔧 部署步骤

### 第一步：准备后端环境（10分钟）

```bash
# 1. 进入项目目录
cd /Users/zhangrui/Claude工作/企业职工认证

# 2. 复制配置文件
cp .env.example .env

# 3. 编辑 .env（配置数据库）
nano .env
# 修改以下内容：
# DB_HOST=localhost
# DB_USER=root
# DB_PASSWORD=your_password
# DB_NAME=lenovo_cert

# 4. 创建数据库和表
mysql -u root -p < database-init.sql

# 5. 安装依赖
npm install

# 6. 启动后端服务
npm run dev
```

**预期输出**：
```
🚀 认证系统后端服务已启动 (端口: 8000)
📍 API 地址: http://localhost:8000
```

### 第二步：配置前端（5分钟）

前端已经完全更新，包含以下功能：

**初始化时会自动**：
1. 调用 `/api/user/cert-status` 检测用户状态
2. 根据状态渲染 Step 1（首次认证 vs 升级/更新认证）
3. 处理流程跳转（升级时跳过 Step 1/2）
4. 在完成后更新用户状态

**无需修改任何代码，直接打开即可使用**：
```bash
# 在浏览器中打开
http://localhost/employee-cert-complete.html
# 或 
file:///Users/zhangrui/Claude工作/企业职工认证/employee-cert-complete.html
```

### 第三步：测试流程（5分钟）

#### 场景1：首次认证

1. 打开前端页面
2. 看到"企业职工认证"和"专业职称认证"两个选项卡
3. 完成整个认证流程（Step 1-4）
4. 完成后看到"返回首页"按钮

#### 场景2：升级认证（首次认证完成后）

1. 点击"返回首页"按钮
2. **看到变化**：Step 1 现在显示"升级：专业职称认证"和"更新在职认证信息"
3. 点击"升级：专业职称认证"
4. **跳过了 Step 1/2**，直接进 Step 3
5. Step 3 仅显示专业职称选择
6. Step 4 仅显示"其他材料补充"

#### 场景3：更新认证

1. 在"升级/更新"选项中点击"更新在职认证信息"
2. **跳过了 Step 1/2**，直接进 Step 3
3. Step 3 显示上一次的企业信息（可编辑）
4. Step 4 显示所有认证方式

---

## 📱 三个版本的统一更新

三个版本都已更新相同的逻辑：
- ✅ `employee-cert-complete.html` (移动端全屏版) - **已完全更新**
- ⏳ `employee-cert-modal.html` (PC弹窗版) - **需要复制 JavaScript 逻辑**
- ⏳ `employee-cert-sheet.html` (移动端半弹层版) - **需要复制 JavaScript 逻辑**

### 如何快速更新其他两个版本

1. 打开 `employee-cert-complete.html` 的 `<script>` 部分
2. 复制所有新增的函数（从 `// ========== 用户认证状态管理 ==========` 到 `// ========== 页面加载初始化 ==========`）
3. 粘贴到 `employee-cert-modal.html` 和 `employee-cert-sheet.html` 的对应位置

关键函数包括：
- `initUserStatus()`
- `renderStep1()`
- `startUpgradeFlow()`
- `startUpdateFlow()`
- `returnToHome()`
- `submitCertificationToBackend()`

---

## 🔌 API 调用流程

### 用户首次打开页面

```
前端页面加载
  ↓
调用 initUserStatus()
  ↓
发送 GET /api/user/cert-status?uid=10001
  ↓
后端查询 certification_history 表
  ↓
返回用户状态和上一次认证数据
  ↓
前端 renderStep1() 根据状态显示不同选项
```

### 用户完成认证并返回首页

```
用户点击"返回首页"
  ↓
前端调用 returnToHome()
  ↓
重新调用 initUserStatus()
  ↓
发送 POST /api/auth/submit（认证数据）
  ↓
后端保存到 certification_history 表
  ↓
更新 user_cert_status 表
  ↓
返回新的用户状态
  ↓
前端显示 Step 1，此时选项已更新（从首次认证 → 升级/更新）
```

---

## 🧪 测试数据

初始化脚本已创建测试用户，可直接使用：

```sql
-- 测试用户：张三
uid: 10001
status: basic-certified (已基础认证)

-- 测试用户：李四
uid: 10002
status: specialist-certified (已完成专业认证)

-- 测试用户：王五
uid: 10003
status: not-certified (未认证)
```

在 API 调用时使用 `?uid=10001` 来测试不同用户状态。

---

## 📊 数据库表关系

```
user_cert_status (用户认证状态)
    ↓
    └─→ uid (外键) → users.uid
    └─→ status (当前状态) → not-certified | basic-certified | specialist-certified
    └─→ cert_count (认证次数) → 1, 2, 3...

certification_history (认证历史)
    ↓
    └─→ uid (外键) → users.uid
    └─→ cert_number (认证序号) → 1, 2, 3...
    └─→ cert_type → basic | specialist_lawyer | specialist_media...
    └─→ is_upgrade → 0 (首次/更新) | 1 (升级)
    └─→ review_status → pending | approved | rejected
```

---

## ⚠️ 常见问题

### Q: 后端 API 返回 404

**检查**：
1. 后端是否运行在 8000 端口？`npm run dev`
2. API 路径是否正确？应该是 `/api/user/cert-status`
3. 前端是否正确调用？检查浏览器控制台错误

### Q: 用户状态没有更新

**检查**：
1. 数据库是否已初始化？`mysql -u root -p < database-init.sql`
2. 认证数据是否成功提交到后端？检查 Network 标签
3. 用户 ID 是否正确？使用 `uid=10001`

### Q: Step 1 没有显示升级/更新选项

**原因**：用户状态仍为 "not-certified"
**解决**：
1. 完成一次完整认证
2. 点击"返回首页"
3. 页面应该重新加载用户状态

### Q: 升级认证时仍然显示企业字段

**原因**：`flowType` 没有正确设置为 "upgrade"
**检查**：浏览器控制台输出 `console.log` 信息

---

## 🎯 下一步工作

### 优先级1（必需）
- [ ] 在 PC 弹窗版本中应用相同的前端逻辑
- [ ] 在移动端半弹层版本中应用相同的前端逻辑
- [ ] 后端部署到阿里云服务器

### 优先级2（重要）
- [ ] 实现真实的用户身份验证（JWT / Session）
- [ ] 实现短信和邮件验证码发送
- [ ] 实现文件上传功能

### 优先级3（优化）
- [ ] 完善错误处理
- [ ] 添加数据校验
- [ ] 实现日志系统

---

## 📞 获取帮助

- 📚 详细文档：`01-前端认证流程文档.md`
- 🏗️ 架构说明：`03-系统架构与集成指南.md`
- 🔄 流程设计：`04-二次认证与升级流程设计.md`
- 🚀 部署指南：`BACKEND_SETUP.md`

---

**更新日期**: 2026-04-15  
**版本**: 1.0  
**状态**: 前后端均已完成
