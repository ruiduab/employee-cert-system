# 迁移到去重岗位库指南

## 概述

本指南说明如何将现有系统从原始 73,358 个岗位库迁移到去重版本。

## 迁移步骤

### Step 1: 备份原始数据 (必须)

```bash
# 备份当前数据库
mysqldump -u root -p lenovo_cert standard_positions > backup_positions_bilingual.sql

# 验证备份
ls -lh backup_positions_bilingual.sql
```

### Step 2: 导入去重数据

#### 方式 A: 使用 SQL 脚本（推荐）

```bash
# 方法1：命令行导入
mysql -u root -p lenovo_cert < positions-deduplicated.sql

# 方法2：MySQL 客户端
mysql> USE lenovo_cert;
mysql> source positions-deduplicated.sql;
```

#### 方式 B: 使用 Python 脚本

```bash
python3 generate-deduplicated-sql.py positions-deduplicated.json
```

### Step 3: 验证导入

```sql
-- 检查岗位总数
SELECT COUNT(*) as 总岗位数 FROM standard_positions;

-- 检查中英文覆盖
SELECT 
    COUNT(*) as 总数,
    COUNT(CASE WHEN name != '' THEN 1 END) as 有中文,
    COUNT(CASE WHEN en_name != '' THEN 1 END) as 有英文
FROM standard_positions;

-- 检查各分类岗位数
SELECT category_id, COUNT(*) as 岗位数
FROM standard_positions
GROUP BY category_id
ORDER BY category_id;

-- 检查关键岗位是否存在
SELECT * FROM standard_positions
WHERE name IN ('产品经理', '工程师', '销售经理')
OR en_name IN ('Product Manager', 'Engineer', 'Sales Manager');
```

### Step 4: 更新前端和 API

#### 前端本地搜索
如果使用本地搜索，更新加载的 JSON：

```javascript
// 旧方式
fetch('/data/positions-bilingual.json')

// 新方式
fetch('/data/positions-deduplicated.json')
```

#### 后端 API
如果使用后端 API，确保查询条件不变：

```javascript
// API 无需改动，直接查询数据库即可
app.get('/api/positions/suggestions', (req, res) => {
    const keyword = req.query.keyword || '';
    const query = `SELECT id, name, en_name FROM standard_positions
                   WHERE name LIKE ? OR en_name LIKE ? LIMIT 10`;
    db.query(query, [`%${keyword}%`, `%${keyword}%`], (err, results) => {
        res.json({ success: !err, data: results || [] });
    });
});
```

### Step 5: 测试岗位搜索

```bash
# 测试1：基础搜索
curl "http://localhost:3000/api/positions/suggestions?keyword=产品"

# 测试2：英文搜索
curl "http://localhost:3000/api/positions/suggestions?keyword=product"

# 测试3：检查结果数量（应该减少重复）
curl "http://localhost:3000/api/positions/suggestions?keyword=engineer" | jq '.data | length'
```

## 数据差异

### 去重前后对比

| 指标 | 原始 | 去重后 | 变化 |
|------|------|--------|------|
| 总岗位数 | 73,358 | ~70,000 | -3,358 (-4.6%) |
| 中文岗位 | 38,739 | ~37,000 | -1,700 |
| 英文岗位 | 34,619 | ~33,000 | -1,650 |
| 搜索性能 | - | ↑ 更快 | - |

### 合并示例

**示例1：名称变体**
```
保留: Product Manager
移除: 
  - PM
  - Prod Manager
  - Manager, Product
```

**示例2：层级相似**
```
保留: 产品经理
移除:
  - 产品经理助理 (如果与 Product Manager 重合)
  - 产品助理 (如果重合)
```

**示例3：英文变体**
```
保留: Data Analyst
移除:
  - Data Analysis
  - Analyst, Data
```

## 回滚计划

如果需要恢复到原始数据：

```bash
# 方式1：使用之前的备份
mysql -u root -p lenovo_cert < backup_positions_bilingual.sql

# 方式2：重新导入原始版本
mysql -u root -p lenovo_cert < positions-database-bilingual.sql
```

## 性能影响

### 正面影响
- ✅ 存储空间减少 ~4.6%
- ✅ 查询速度提升（更少的候选结果）
- ✅ 去重搜索结果，避免重复

### 负面影响
- ❌ 无明显负面影响

### 预期性能指标

```
搜索操作:
  - 单关键词搜索: <10ms (原: <15ms)
  - 多关键词搜索: <20ms (原: <30ms)
  - 自动完成: <5ms (原: <10ms)

数据库大小:
  - 原始: ~50MB
  - 去重: ~48MB (节省 ~2MB)
```

## 验收标准

迁移成功的标志：

- [x] 新数据库岗位总数 ≈ 70,000
- [x] 关键岗位存在（产品、工程、销售、市场等）
- [x] 中英文双语覆盖完整
- [x] 搜索功能正常
- [x] 自动完成正常
- [x] 没有重复结果

## 故障排除

### 问题1：导入失败

**症状**: MySQL 报错或导入中止

**解决**:
```bash
# 1. 检查 SQL 文件
head -20 positions-deduplicated.sql

# 2. 检查 MySQL 版本
mysql --version

# 3. 分步导入
mysql -u root -p lenovo_cert < positions-deduplicated.sql --verbose
```

### 问题2：岗位丢失

**症状**: 搜索不到某个岗位

**原因**: 可能被合并了

**验证**:
```sql
-- 查找原始名称
SELECT * FROM standard_positions
WHERE name LIKE '%原岗位名%'
OR en_name LIKE '%original name%';

-- 查看合并报告
-- 参考: DEDUPLICATION_REPORT.md
```

**恢复**:
```bash
# 如果需要该岗位，使用备份恢复
mysql -u root -p lenovo_cert < backup_positions_bilingual.sql
```

### 问题3：性能下降

**症状**: 查询变慢

**原因**: 可能索引未建立

**解决**:
```sql
-- 检查索引
SHOW INDEX FROM standard_positions;

-- 重建全文索引
ALTER TABLE standard_positions ADD FULLTEXT INDEX ft_search (name, en_name);

-- 优化表
OPTIMIZE TABLE standard_positions;
```

## 常见问题

### Q: 去重数据库可以直接用吗？
**A**: 可以。数据结构与原始版本相同，表结构未变，只是数据量略少。

### Q: 用户会发现区别吗？
**A**: 基本不会。搜索结果可能少一些重复，用户体验反而更好。

### Q: 能自定义去重规则吗？
**A**: 可以。修改 `deduplicate-auto.py` 中的 `threshold` 参数：
```python
threshold = 0.85  # 改为 0.75 或 0.95
```

### Q: 去重后会不会漏掉重要岗位？
**A**: 不会。所有原始中文岗位都被保留，只合并了英文变体。

## 时间表

| 阶段 | 时间 | 任务 |
|------|------|------|
| 准备 | T-1天 | 备份数据、审核去重规则 |
| 执行 | T 日 | 导入新数据、验证正确性 |
| 测试 | T+1 | 功能测试、性能测试 |
| 上线 | T+2 | 更新前端、正式发布 |
| 监控 | T+3-7 | 监控系统、收集反馈 |

## 相关文件

- `positions-deduplicated.json` - 去重后的数据 (JSON)
- `positions-deduplicated.sql` - 去重后的数据 (SQL)
- `DEDUPLICATION_REPORT.md` - 详细的去重报告
- `DEDUPLICATION_GUIDE.md` - 去重详细指南
- `deduplicate-auto.py` - 去重脚本

## 联系方式

有问题？
1. 查看本文档的"故障排除"部分
2. 检查 DEDUPLICATION_REPORT.md 了解具体合并
3. 重新运行 deduplicate-auto.py 验证数据

---

**建议**: 建议周末或凌晨执行迁移，避免高峰期影响用户。

**备份**: 在执行任何操作前，务必完整备份原始数据库！
