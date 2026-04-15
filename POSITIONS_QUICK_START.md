# 岗位库集成 - 快速开始指南

## 📦 新增文件清单

| 文件 | 说明 | 优先级 |
|------|------|--------|
| `positions-database-init.sql` | 数据库初始化脚本（203个岗位 + 43个行业） | ⭐⭐⭐ 必需 |
| `import-positions-data.py` | Python 导入工具 | ⭐⭐ 推荐 |
| `POSITIONS_DATABASE_README.md` | 数据库详细文档 | ⭐⭐ 参考 |
| `FRONTEND_POSITIONS_INTEGRATION.md` | 前端集成指南 | ⭐⭐⭐ 必读 |
| `POSITIONS_QUICK_START.md` | 本文档 | ⭐ 快速查看 |

## ⚡ 5分钟快速部署

### 步骤 1: 导入数据库（选择一种方式）

**方式 A：Python 脚本（推荐）**
```bash
# 1. 安装依赖
pip install mysql-connector-python

# 2. 运行导入脚本
python3 import-positions-data.py --database lenovo_cert
```

**方式 B：直接导入 SQL**
```bash
mysql -u root -p lenovo_cert < positions-database-init.sql
```

### 步骤 2: 验证导入

```sql
-- 连接到数据库
mysql -u root -p
USE lenovo_cert;

-- 检查数据
SELECT COUNT(*) FROM industries;        -- 应该 >= 43
SELECT COUNT(*) FROM position_categories;  -- 应该 = 10
SELECT COUNT(*) FROM standard_positions;   -- 应该 >= 100
```

### 步骤 3: 更新后端 API（如需动态查询）

在 `backend-api-server.js` 中添加岗位查询端点（见下方快速代码）

### 步骤 4: 更新前端（选择方案）

- **简单方案**：使用前端本地列表
- **完整方案**：使用后端 API
- 详见 [FRONTEND_POSITIONS_INTEGRATION.md](./FRONTEND_POSITIONS_INTEGRATION.md)

## 🚀 常用命令

```bash
# 导入数据库
python3 import-positions-data.py --database lenovo_cert

# 验证导入
mysql lenovo_cert -e "SELECT COUNT(*) FROM standard_positions;"

# 导出岗位列表（JSON 格式）
mysql lenovo_cert --json -e "SELECT name, en_name FROM standard_positions;" > positions.json

# 导出岗位列表（CSV 格式）
mysql lenovo_cert -e "SELECT name, en_name FROM standard_positions;" > positions.csv
```

## 📝 最常用的 SQL 查询

```sql
-- 获取所有岗位及分类
SELECT sp.name, sp.en_name, pc.name as category
FROM standard_positions sp
JOIN position_categories pc ON sp.category_id = pc.id
ORDER BY pc.display_order, sp.name;

-- 搜索岗位（支持模糊匹配）
SELECT * FROM standard_positions
WHERE name LIKE '%前端%' OR en_name LIKE '%frontend%'
LIMIT 10;

-- 获取某个分类的所有岗位
SELECT name FROM standard_positions
WHERE category_id = 1 AND is_active = TRUE
ORDER BY name;

-- 获取行业分类
SELECT code, name FROM industries
WHERE level = 1
ORDER BY code;
```

## 💻 后端 API 快速代码

把这段代码添加到 `backend-api-server.js`：

```javascript
// 岗位搜索 API
app.get('/api/positions/suggestions', (req, res) => {
    const keyword = req.query.keyword || '';
    const limit = parseInt(req.query.limit) || 10;
    
    if (!keyword.trim()) {
        res.json({ success: true, data: [] });
        return;
    }
    
    const query = `
        SELECT id, name, en_name 
        FROM standard_positions
        WHERE is_active = TRUE AND (name LIKE ? OR en_name LIKE ?)
        LIMIT ?
    `;
    
    const searchTerm = `%${keyword}%`;
    db.query(query, [searchTerm, searchTerm, limit], (err, results) => {
        if (err) {
            res.status(500).json({ success: false, error: err.message });
            return;
        }
        res.json({ success: true, data: results });
    });
});
```

## 🎯 前端使用示例

### 简单版（本地列表）

```javascript
// 直接使用 SQL 导出的岗位列表
const standardPositions = [
    '产品经理', '前端工程师', '后端工程师', 
    // ... 更多岗位
];

// 搜索岗位
function searchPositions(keyword) {
    return standardPositions.filter(pos =>
        pos.toLowerCase().includes(keyword.toLowerCase())
    ).slice(0, 10);
}
```

### 高级版（使用 API）

```javascript
// 使用后端 API
async function getPositionSuggestions(keyword) {
    const response = await fetch(
        `/api/positions/suggestions?keyword=${keyword}&limit=10`
    );
    const { data } = await response.json();
    return data.map(pos => pos.name);
}

// 在输入框中使用
document.getElementById('position').addEventListener('input', (e) => {
    getPositionSuggestions(e.target.value).then(suggestions => {
        // 显示建议...
    });
});
```

## 📊 数据统计

```
✅ 已包含的岗位分类：10 个
   - 技术开发
   - 移动开发
   - 数据科学
   - 设计
   - 公关传播
   - 市场营销
   - 人力资源
   - 销售业务
   - 财务会计
   - 产品管理

✅ 已包含的标准岗位：100+ 个
   包括但不限于：
   - 前端工程师、后端工程师、全栈工程师
   - iOS 开发、Android 开发
   - 产品经理、项目经理
   - 市场经理、销售经理
   - 财务、会计、HR
   - ... 更多岗位

✅ 已包含的行业分类：43 个
   - 一级分类：20 个（国民经济标准）
   - 二级分类：23 个（主要行业细分）
```

## 🔍 常见问题

### Q: 如何添加自定义岗位？

```sql
INSERT INTO standard_positions (name, en_name, category_id, keywords)
VALUES ('新岗位', 'New Position', 1, '["关键词1", "关键词2"]');
```

### Q: 如何禁用某个岗位？

```sql
UPDATE standard_positions
SET is_active = FALSE
WHERE name = '要禁用的岗位';
```

### Q: 如何导出所有岗位到 JSON？

```bash
mysql lenovo_cert --json -e \
  "SELECT * FROM standard_positions WHERE is_active = TRUE;" \
  > all_positions.json
```

### Q: 如何支持更多语言的岗位？

在 `standard_positions` 表中添加更多列：
```sql
ALTER TABLE standard_positions ADD COLUMN name_ja VARCHAR(100);
ALTER TABLE standard_positions ADD COLUMN name_es VARCHAR(100);
```

### Q: 数据导入失败怎么办？

```bash
# 1. 检查 MySQL 连接
mysql -u root -p -h localhost

# 2. 检查数据库存在
mysql -u root -p -e "SHOW DATABASES;"

# 3. 手动导入 SQL（显示详细错误）
mysql -u root -p < positions-database-init.sql

# 4. 查看详细错误信息
python3 import-positions-data.py --database lenovo_cert 2>&1 | tee import.log
```

## 📚 深入了解

要了解更多详细信息，请查看：

1. **数据库结构**：[POSITIONS_DATABASE_README.md](./POSITIONS_DATABASE_README.md)
   - 表结构详解
   - 查询示例
   - 性能优化

2. **前端集成**：[FRONTEND_POSITIONS_INTEGRATION.md](./FRONTEND_POSITIONS_INTEGRATION.md)
   - 三种集成方案
   - 完整代码示例
   - 性能优化建议

3. **后端部署**：[BACKEND_SETUP.md](./BACKEND_SETUP.md)
   - 数据库初始化步骤
   - API 部署指南

## ✨ 最佳实践

1. **使用 Python 脚本导入** - 自动化、安全、易排查问题
2. **添加索引** - SQL 脚本已包含，提升查询性能
3. **启用缓存** - 前端缓存热点查询结果
4. **定期备份** - `mysqldump -u root -p dbname > backup.sql`
5. **监控日志** - 定期检查数据库日志

## 🎉 下一步

- [ ] 导入岗位数据到数据库
- [ ] 验证数据导入成功
- [ ] 更新后端 API 端点
- [ ] 集成前端岗位输入框
- [ ] 测试岗位搜索功能
- [ ] 部署到生产环境

---

**版本**: 1.0  
**最后更新**: 2026-04-15  
**数据来源**: ramwin/china-public-data + egorvinogradov/job-titles-categories.json  
**维护**: Claude Code
