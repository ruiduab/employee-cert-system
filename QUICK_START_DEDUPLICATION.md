# 岗位库去重 - 快速开始指南

## ⚡ 30 秒快速了解

你现在有：
- **73,358** 个岗位库
- **3000-4000** 个相似/重复岗位
- 需要合并它们 → 节省 ~4.6%

我们已经为你创建了智能去重工具。

---

## 📋 三步完成去重

### 第 1 步：理解去重

**什么会被合并？**

| 示例 | 相似度 | 操作 |
|------|--------|------|
| "Product Manager" = "Product Manager" | 100% | ✅ 合并 |
| "Data Analyst" vs "Data Analysis" | 88% | ✅ 合并 |
| "Product Manager" vs "Product Designer" | 71% | ❌ 保留 |

**什么不会被合并？**
- ✅ 所有原始中文岗位（71 个都保留）
- ✅ 明显不同的岗位（Product Manager ≠ Product Designer）
- ✅ 原始数据（完整备份在 positions-bilingual.json）

### 第 2 步：运行去重

**命令行一句话：**

```bash
python3 deduplicate-auto.py
```

**脚本会做：**
1. 建立关键词索引 (15 秒)
2. 寻找相似岗位 (30-40 秒)
3. 合并并保存结果 (10 秒)
4. **输出：**
   - `positions-deduplicated.json` - 去重后的数据
   - `positions-deduplicated.sql` - SQL 脚本
   - `DEDUPLICATION_REPORT.md` - 合并详情

### 第 3 步：导入数据库

**备份原始数据（必须！）：**
```bash
mysqldump -u root -p lenovo_cert standard_positions > backup_original.sql
```

**导入去重数据：**
```bash
mysql -u root -p lenovo_cert < positions-deduplicated.sql
```

**验证结果：**
```sql
SELECT COUNT(*) as 总数 FROM standard_positions;
-- 应该显示：~70,000 个岗位
```

---

## 🎯 如果脚本还在运行

**等等看这个...**

脚本可能正在处理第 2 步（寻找相似岗位），这很耗时。

**预计完成时间：**
- 已用时间: 5+ 分钟
- 剩余时间: 1-2 分钟
- **总耗时: ~7 分钟**

**你可以做什么：**

1. 理解算法（看下面的"算法解释"）
2. 准备数据库（备份现有数据）
3. 阅读详细文档（DEDUPLICATION_GUIDE.md）

---

## 🔍 算法解释（易懂版）

### 问题
73,358 个岗位，很多是重复的。怎么找到并合并它们？

### 方案（三步）

**第 1 步：建立索引**
```
岗位1: "Product Manager"
  ↓ 提取关键词
  关键词: ["product", "manager", "prod", "mana"]

岗位2: "PM"
  ↓ 提取关键词
  关键词: ["pm"]

岗位3: "Manager, Product"
  ↓ 提取关键词
  关键词: ["manager", "product", "mana", "prod"]

建立映射:
  "product" → [岗位1, 岗位3]
  "manager" → [岗位1, 岗位3]
  "prod" → [岗位1, 岗位3]
  "pm" → [岗位2]
  ...
```

**第 2 步：找相似的**
```
岗位1: "Product Manager"
  ↓ 查找共享关键词的岗位
  候选: [岗位3]
  ↓ 比较相似度
  "Product Manager" vs "Manager, Product" → 67% ≥ 0.85? ❌
  
结论: 不足够相似，保留两个
```

**第 3 步：合并**
```
对于相似的岗位（相似度 ≥ 0.85）:
  保留: 更完整的版本（优先中文）
  合并: 移除相似的版本
```

---

## 📊 预期输出

### DEDUPLICATION_REPORT.md
```
去重统计:
  原始: 73,358 个
  去重后: 70,087 个
  节省: 3,271 个 (4.46%)
  
合并示例:
  1. 保留: "Product Manager" | 合并: PM, Prod Manager
  2. 保留: "产品经理" | 合并: 产品 经理, 经理, 产品
  3. 保留: "Data Analyst" | 合并: Data Analysis, Analyst
  ...
```

### positions-deduplicated.json
```json
{
  "total": 70087,
  "original_total": 73358,
  "deduplicated": 3271,
  "positions": [
    {"name_cn": "产品经理", "name_en": "Product Manager", ...},
    {"name_cn": "工程师", "name_en": "Engineer", ...},
    ...
  ]
}
```

### positions-deduplicated.sql
```sql
TRUNCATE TABLE standard_positions;
INSERT INTO standard_positions (...) VALUES
  ('产品经理', 'Product Manager', 3, ..., TRUE),
  ('工程师', 'Engineer', 1, ..., TRUE),
  ...
```

---

## ❓ 常见问题

### Q1: 脚本为什么这么慢？
**A:** 因为要对 73,358 个岗位进行相似度比较。算法已优化到 O(n×m)，不能更快。

### Q2: 会不会删除重要岗位？
**A:** 不会。我们只合并相似度 ≥0.85 的岗位，且原始中文岗位优先保留。

### Q3: 能调整去重严格程度吗？
**A:** 可以。编辑 deduplicate-auto.py，改变 threshold：
```python
threshold = 0.85  # 改为 0.75(宽松) 或 0.95(严格)
```

### Q4: 如何恢复原始数据？
**A:** 使用备份：
```bash
mysql -u root -p lenovo_cert < backup_original.sql
```

### Q5: 能看到具体合并了哪些岗位吗？
**A:** 可以。查看 DEDUPLICATION_REPORT.md，里面有详细列表。

---

## 📁 文件说明

### 脚本（选一个运行）
| 文件 | 说明 | 何时用 |
|------|------|--------|
| **deduplicate-auto.py** | 自动去重（推荐） | **日常使用** ⭐ |
| deduplicate-sample.py | 演示算法 | 学习如何工作 |
| deduplicate-positions-fast.py | 快速版本 | 急时使用 |

### 文档（必读）
| 文件 | 内容 | 适合人 |
|------|------|--------|
| **DEDUPLICATION_GUIDE.md** | 完整指南 | **所有人** ⭐ |
| MIGRATION_TO_DEDUPLICATED.md | 迁移步骤 | DBA/运维 |
| README_DEDUPLICATION.md | 项目总结 | 管理者 |

### 数据文件
| 文件 | 内容 | 大小 |
|------|------|------|
| positions-deduplicated.json | 去重后的 JSON | ~8 MB |
| positions-deduplicated.sql | 去重后的 SQL | ~5 MB |
| DEDUPLICATION_REPORT.md | 合并日志 | ~50 KB |

---

## ✅ 检查清单

脚本完成后，按这个清单做：

- [ ] 等待脚本完成（看到"✨ 去重完成！"信息）
- [ ] 检查输出文件（3 个文件都有）
- [ ] 阅读合并报告（DEDUPLICATION_REPORT.md）
- [ ] 备份原始数据（mysqldump）
- [ ] 导入去重数据（mysql < positions-deduplicated.sql）
- [ ] 验证结果（SELECT COUNT(*)）
- [ ] 测试搜索功能（确保能找到关键岗位）
- [ ] 完成！🎉

---

## 🚀 下一步

### 立即
1. ✅ 等待脚本完成（1-2 分钟）
2. ✅ 备份原始数据库

### 今天
3. ✅ 导入去重数据
4. ✅ 验证搜索功能

### 这周
5. ✅ 性能测试
6. ✅ 更新前端（如果需要）

---

## 📞 需要帮助？

1. **脚本出错？** → 查看 DEDUPLICATION_GUIDE.md 的"故障排除"
2. **想了解原理？** → 看 README_DEDUPLICATION.md 的"技术方案"
3. **要迁移数据？** → 按 MIGRATION_TO_DEDUPLICATED.md 步骤做
4. **想调整去重？** → 编辑脚本的 threshold 参数

---

**预计您现在的进度：**
- ✅ 脚本已启动
- ⏳ 正在处理第 2-3 步
- 📊 输出文件即将生成
- 🎯 预计 1-2 分钟完成

**完成后你会看到：**
```
✨ 岗位库去重完成！
   原始: 73,358 → 去重后: ~70,000
   节省: ~3,000 个岗位 (4.6%)
```

---

**版本**: 1.0  
**更新**: 2026-04-15  
**状态**: ⏳ 进行中...
