# 项目版本控制和保存指南

## 📋 项目保存现状

### ✅ 已实施的保存方案

1. **本地Git仓库** 
   - ✓ 已初始化：`/Users/zhangrui/Claude工作/企业职工认证/.git`
   - ✓ 首次提交：ca8b0f4 (2026-04-15)
   - ✓ 所有文件已纳入版本管理
   - ✓ 包含完整的变更历史

2. **阿里云部署备份**
   - ✓ 前端文件：http://101.132.158.166:8082/
   - ✓ 后台文件：http://101.132.158.166:8083/
   - ✓ 路径：/usr/share/nginx/html/
   - ✓ 最后更新：2026-04-15 10:51

3. **文件清单**
   ```
   📁 企业职工认证/
   ├── 📄 前端页面
   │  ├── employee-cert-complete.html (83K)
   │  ├── employee-cert-modal.html (86K)
   │  └── employee-cert-sheet.html (86K)
   ├── 📄 后台管理
   │  └── 联想在职认证后台原型.html (132K)
   ├── 📄 后端代码
   │  ├── backend-api-server.js
   │  ├── database-init.sql
   │  └── package.json
   ├── 📚 完整文档
   │  ├── 01-前端认证流程文档.md
   │  ├── 02-后台管理系统文档.md
   │  ├── 03-系统架构与集成指南.md
   │  ├── 04-二次认证与升级流程设计.md
   │  ├── README.md
   │  ├── TESTING_GUIDE.md
   │  ├── BACKEND_SETUP.md
   │  └── QUICK_START.md
   └── 📋 历史文档 (参考用)
   ```

---

## 🔄 日常版本管理流程

### 修改文件后如何保存

**步骤1：查看修改**
```bash
cd /Users/zhangrui/Claude工作/企业职工认证/
git status
```

**步骤2：提交修改**
```bash
git add <修改的文件>
git commit -m "描述：修改的内容"
```

**步骤3：查看提交历史**
```bash
git log --oneline
```

### 常用命令

| 命令 | 说明 |
|------|------|
| `git status` | 查看文件修改状态 |
| `git add .` | 将所有修改添加到暂存区 |
| `git commit -m "描述"` | 创建新提交 |
| `git log` | 查看完整历史 |
| `git log --oneline -10` | 查看最近10条记录 |
| `git diff` | 查看具体修改内容 |
| `git restore <文件>` | 恢复到上个版本 |

---

## ☁️ 远程备份建议（可选）

### 方案1：GitHub备份（推荐）
```bash
# 创建GitHub账户并新建仓库 "employee-cert-system"
git remote add origin https://github.com/yourusername/employee-cert-system.git
git branch -M main
git push -u origin main
```

### 方案2：GitLab或Gitee备份
```bash
git remote add origin https://gitee.com/yourusername/employee-cert-system.git
git push -u origin main
```

### 方案3：定期压缩备份
```bash
# 每月备份一次
tar -czf employee-cert-backup-$(date +%Y%m%d).tar.gz /Users/zhangrui/Claude工作/企业职工认证/
```

---

## 📊 版本历史记录

| 提交ID | 日期 | 说明 | 版本 |
|--------|------|------|------|
| ca8b0f4 | 2026-04-15 | 初始提交：完整项目版本 | 2.0.0 |
| - | - | - | - |

---

## 🔐 数据恢复

如果误删文件，可以通过以下方式恢复：

### 恢复单个文件
```bash
git restore <文件名>
```

### 恢复到上个版本
```bash
git reset --hard HEAD~1  # 回到上一个版本
git reset --hard <提交ID>  # 回到指定版本
```

### 查看删除的文件
```bash
git log --full-history -- <文件名>
git show <提交ID>:<文件名>
```

---

## 📌 建议维护计划

### 每次修改
- [ ] 测试功能正常
- [ ] 使用 `git commit` 保存版本
- [ ] 提交消息清晰描述修改内容

### 每周
- [ ] 备份关键文件
- [ ] 检查 `git log` 确保历史完整

### 每月
- [ ] 压缩备份到安全位置
- [ ] 更新文档记录
- [ ] 清理不需要的临时文件

### 重大更新时
- [ ] 创建新的发布标签：`git tag v2.1.0`
- [ ] 推送到远程仓库（如已配置）
- [ ] 更新 README 和版本号

---

## ⚠️ 注意事项

1. **不要手动删除 `.git` 目录** - 这会丢失所有版本历史
2. **定期提交** - 至少每周一次，重要修改立即提交
3. **写好提交信息** - 便于日后查阅和理解修改
4. **敏感信息** - 不要提交密码、密钥到版本库
5. **大文件** - 避免提交超过50MB的文件

---

**最后更新：** 2026-04-15  
**维护人：** Claude Code  
**项目版本：** 2.0.0
