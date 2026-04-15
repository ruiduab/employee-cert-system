# 二次认证和升级认证 - 测试指南

## 📱 界面测试

### 场景1：首次认证用户的 Step 1

**预期显示**：
- 企业职工认证（单选框）
- 专业职称认证（单选框）

**操作**：
1. 打开 HTML 文件
2. 查看 Step 1 是否显示上述两个选项卡
3. 选择"企业职工认证"，点"下一步"

### 场景2：首次认证完成后返回首页

**预期显示**：
```
继续认证
选择升级认证或更新在职信息

[🎯] 升级：专业职称认证
    从基础认证升级为专业职称认证，获得专业身份和特权

[🔄] 更新在职认证信息
    更新您的企业、职位、行业等基本信息
```

**操作**：
1. 完成整个认证流程（Step 1-4）
2. 在 Step 5（成功页面）点击"返回首页"
3. **验证**：Step 1 是否显示了上述两个入口卡片（而不是原来的认证类型选项卡）

### 场景3：点击"升级：专业职称认证"

**预期行为**：
- 跳过 Step 1/2
- 直接进入 Step 3
- Step 3 仅显示专业职称选择（隐藏企业、职位、行业字段）
- 显示"专业职称认证资料要求"提示

**操作**：
1. 在 Step 1 的升级/更新入口点击"升级"卡片
2. **验证** Step 3：
   - [ ] 企业名称字段隐藏
   - [ ] 职位信息字段隐藏
   - [ ] 行业字段隐藏
   - [ ] 显示提示："📋 专业职称认证资料要求"
   - [ ] 提示内容包括不同职称的文件要求示例

3. 选择一个专业职称（如"设计师"）
4. **验证**：提示信息是否更新为对应职称的示例

### 场景4：升级认证的 Step 4

**预期显示**：
- 仅显示"其他材料补充"选项
- 隐藏邮箱、合同、税单选项

**操作**：
1. 在 Step 3 中选择专业职称
2. 进入 Step 4
3. **验证**：
   - [ ] 邮箱认证选项隐藏
   - [ ] 劳动合同选项隐藏
   - [ ] 个人所得税选项隐藏
   - [ ] "其他材料补充"自动被选中

### 场景5：点击"更新在职认证信息"

**预期行为**：
- 跳过 Step 1/2
- 直接进入 Step 3
- Step 3 显示企业、职位、行业字段（与首次认证相同）
- 企业和职位字段预填上一次的信息

**操作**：
1. 在 Step 1 的升级/更新入口点击"更新"卡片
2. **验证** Step 3：
   - [ ] 企业名称字段显示
   - [ ] 企业名称预填为上一次的值
   - [ ] 职位信息字段显示
   - [ ] 职位信息预填为上一次的值
   - [ ] 行业字段显示
   - [ ] 隐藏"专业职称认证资料要求"提示

---

## 🔌 后端 API 测试

### 1. 获取用户认证状态

```bash
# 测试用户 1：未认证
curl "http://localhost:8000/api/user/cert-status?uid=10003"

# 预期返回
{
  "success": true,
  "status": "not-certified",
  "certCount": 0,
  "lastCertData": null
}
```

```bash
# 测试用户 2：已基础认证
curl "http://localhost:8000/api/user/cert-status?uid=10001"

# 预期返回
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

### 2. 提交首次认证

```bash
curl -X POST http://localhost:8000/api/auth/submit \
  -H "Content-Type: application/json" \
  -H "X-User-ID: 10003" \
  -d '{
    "flowType": "first",
    "certNumber": 1,
    "isUpgrade": false,
    "certType": "basic",
    "company": "测试公司",
    "position": "工程师",
    "industry": "互联网/信息技术",
    "specialty": "",
    "authMethod": "contract",
    "timestamp": "2026-04-15T14:30:00Z"
  }'

# 预期返回
{
  "success": true,
  "message": "认证申请已提交",
  "newStatus": "basic-certified",
  "certNumber": 1,
  "certId": 1713177000000
}
```

### 3. 提交升级认证

```bash
curl -X POST http://localhost:8000/api/auth/submit \
  -H "Content-Type: application/json" \
  -H "X-User-ID: 10001" \
  -d '{
    "flowType": "upgrade",
    "certNumber": 2,
    "isUpgrade": true,
    "certType": "specialist_media",
    "company": null,
    "position": null,
    "industry": null,
    "specialty": "media-design",
    "authMethod": "other",
    "filePath": "/uploads/design_portfolio.pdf",
    "fileName": "design_portfolio.pdf",
    "timestamp": "2026-04-16T10:15:00Z"
  }'

# 预期返回
{
  "success": true,
  "message": "认证申请已提交",
  "newStatus": "specialist-certified",
  "certNumber": 2,
  "certId": 1713261300000
}
```

### 4. 查询用户认证历史

```bash
curl "http://localhost:8000/api/user/cert-history?uid=10001"

# 预期返回
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
    },
    {
      "id": 2,
      "uid": 10001,
      "cert_number": 2,
      "cert_type": "specialist_media",
      "is_upgrade": 1,
      "company": null,
      "position": null,
      "industry": null,
      "auth_method": "other",
      "review_status": "pending",
      "submitted_at": "2026-04-16 10:15:00",
      "reviewed_at": null
    }
  ]
}
```

---

## 🗄️ 数据库验证

### 查看用户认证状态

```sql
SELECT * FROM user_cert_status WHERE uid = 10001;
```

**预期输出**：
```
uid | status | cert_count | current_cert_type | last_cert_time
10001 | basic-certified | 1 | basic | 2026-04-15 14:30:00
```

### 查看认证历史

```sql
SELECT id, uid, cert_number, cert_type, is_upgrade, company, position, 
       auth_method, review_status, submitted_at 
FROM certification_history 
WHERE uid = 10001 
ORDER BY cert_number DESC;
```

**预期输出**：
```
id | uid | cert_number | cert_type | is_upgrade | company | position | auth_method | review_status | submitted_at
1 | 10001 | 1 | basic | 0 | 联想（北京）有限公司 | 产品经理 | email | approved | 2026-04-15 14:30:00
```

### 验证数据流

```sql
-- 1. 首次认证
INSERT INTO certification_history 
(uid, cert_number, cert_type, is_upgrade, company, position, industry, auth_method, review_status, submitted_at)
VALUES (10001, 1, 'basic', 0, '联想', '产品经理', 'tech', 'email', 'pending', NOW());

-- 2. 查看数据
SELECT * FROM certification_history WHERE uid = 10001;

-- 3. 更新状态
UPDATE user_cert_status 
SET status = 'basic-certified', cert_count = 1 
WHERE uid = 10001;

-- 4. 验证
SELECT * FROM user_cert_status WHERE uid = 10001;
```

---

## ✅ 完整测试清单

### 前端测试
- [ ] 未认证用户看到首次认证选项卡
- [ ] 已认证用户看到升级/更新入口卡片
- [ ] 升级入口隐藏企业字段，显示职称提示
- [ ] 更新入口显示企业字段，预填信息
- [ ] 升级 Step 4 仅显示"其他材料补充"
- [ ] 返回首页时正确检测用户状态
- [ ] 浏览器控制台无报错

### 后端测试
- [ ] `/api/user/cert-status` 返回正确的状态
- [ ] `/api/auth/submit` 正确保存认证数据
- [ ] 用户状态和认证历史正确更新
- [ ] `/api/user/cert-history` 返回完整的认证历史
- [ ] 后台 API `/api/admin/users` 显示认证次数

### 数据库测试
- [ ] `user_cert_status` 表数据正确
- [ ] `certification_history` 表完整记录
- [ ] 认证次数正确递增
- [ ] 升级标志正确标记

---

## 🐛 调试技巧

### 查看浏览器控制台日志

打开浏览器开发工具（F12），查看 Console 标签：

```javascript
// 应该看到以下日志
✓ 从后端获取用户状态: basic-certified
✓ 显示升级/更新选项卡，用户状态: basic-certified
✓ 升级认证流程：隐藏企业字段，显示职称认证提示
✓ 状态已更新: { userStatus: 'specialist-certified', ... }
✓ 认证数据已提交到后端: { success: true, ... }
```

### 查看网络请求

在浏览器开发工具的 Network 标签中：
1. 查看 `/api/user/cert-status` 的请求和响应
2. 查看 `/api/auth/submit` 的请求和响应
3. 验证 HTTP 状态码是否为 200

### 修改本地用户状态（用于演示）

在浏览器控制台中执行：

```javascript
// 模拟已基础认证
localStorage.setItem('userCertStatus', 'basic-certified');
location.reload();

// 模拟已完成专业认证
localStorage.setItem('userCertStatus', 'specialist-certified');
location.reload();

// 模拟未认证
localStorage.setItem('userCertStatus', 'not-certified');
location.reload();
```

---

## 📊 测试数据

| 用户ID | 状态 | 认证次数 | 用途 |
|--------|------|---------|------|
| 10001 | basic-certified | 1 | 测试升级/更新流程 |
| 10002 | specialist-certified | 2 | 测试已完成专业认证用户 |
| 10003 | not-certified | 0 | 测试首次认证流程 |

---

**更新日期**: 2026-04-15  
**版本**: 1.0
