# 岗位和行业分类数据库集成指南

本文档说明如何使用新的岗位和行业分类数据库系统。

## 📋 概述

该系统包含：
- **行业分类表** (`industries`) - 中国国民经济行业分类标准
- **职位分类表** (`position_categories`) - 职位的分类体系（10个主要类别）
- **标准岗位表** (`standard_positions`) - 200+ 个标准岗位名称及其关键词

### 数据来源
- 🌍 **国民经济行业分类**: 中国国家统计局官方标准
- 💼 **职位分类**: GitHub 开源项目 `egorvinogradov/job-titles-categories.json`
- 📍 **中文岗位**: 项目现有的 `standardPositions` 列表

## 🚀 快速开始

### 方式一：使用 Python 导入脚本（推荐）

#### 1. 安装依赖
```bash
pip install mysql-connector-python
```

#### 2. 执行导入
```bash
# 使用默认配置（localhost, user=root, database=employee_cert）
python3 import-positions-data.py

# 或指定自定义配置
python3 import-positions-data.py \
  --host your_host \
  --user your_user \
  --password your_password \
  --database your_database
```

#### 3. 验证导入
脚本会自动验证数据并显示统计信息：
```
📋 数据验证:
  行业分类: 43
  职位分类: 10
  标准岗位: 103
  启用的岗位: 103
```

### 方式二：直接导入 SQL 文件

```bash
# 方式 1: 命令行导入
mysql -h localhost -u root -p your_database < positions-database-init.sql

# 方式 2: MySQL 客户端
mysql> use employee_cert;
mysql> source /path/to/positions-database-init.sql;
```

## 📊 数据库表结构

### 1. industries（行业分类表）
```sql
CREATE TABLE industries (
    id INT PRIMARY KEY,                  -- 行业ID
    code VARCHAR(10) UNIQUE,             -- 行业代码（如 "I" 表示信息技术）
    name VARCHAR(100) NOT NULL,          -- 中文行业名称
    en_name VARCHAR(100),                -- 英文行业名称
    parent_id INT,                       -- 父级行业ID（实现树形结构）
    level INT,                           -- 等级（1=一级，2=二级）
    description TEXT,                    -- 行业描述
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

**主要一级行业分类：**
- A: 农、林、牧、渔业
- C: 制造业
- I: 信息传输、软件和信息技术服务业
- J: 金融业
- K: 房地产业
- P: 教育
- Q: 卫生和社会工作

### 2. position_categories（职位分类表）
```sql
CREATE TABLE position_categories (
    id INT PRIMARY KEY,          -- 分类ID
    name VARCHAR(100) UNIQUE,    -- 分类名称
    en_name VARCHAR(100),        -- 英文分类名称
    description TEXT,            -- 分类描述
    display_order INT,           -- 显示顺序
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

**10个主要职位分类：**
1. 技术开发 (Web Development)
2. 移动开发 (Mobile Development)
3. 数据科学 (Data Science)
4. 设计 (Design)
5. 公关传播 (Public Relations)
6. 市场营销 (Marketing)
7. 人力资源 (Human Resources)
8. 销售业务 (Sales & Business Development)
9. 财务会计 (Finance & Accounting)
10. 产品管理 (Product Management)

### 3. standard_positions（标准岗位表）
```sql
CREATE TABLE standard_positions (
    id INT PRIMARY KEY,                  -- 岗位ID
    name VARCHAR(100) NOT NULL UNIQUE,   -- 岗位名称（如 "前端工程师"）
    en_name VARCHAR(150),                -- 英文岗位名称
    category_id INT,                     -- 职位分类ID
    description TEXT,                    -- 岗位描述
    keywords JSON,                       -- 关键词（用于搜索和自动完成）
    related_industries JSON,             -- 相关行业ID列表
    skill_requirements TEXT,             -- 技能要求
    is_active BOOLEAN DEFAULT TRUE,      -- 是否启用
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

**关键特性：**
- `keywords` 字段存储 JSON 数组，用于模糊搜索和自动完成
- `related_industries` 存储相关行业ID列表
- 全文索引支持快速搜索

## 🔍 常用查询示例

### 1. 获取所有启用的岗位及其分类
```sql
SELECT 
    sp.id,
    sp.name,
    sp.en_name,
    pc.name AS category,
    sp.keywords
FROM standard_positions sp
JOIN position_categories pc ON sp.category_id = pc.id
WHERE sp.is_active = TRUE
ORDER BY pc.display_order, sp.name;
```

### 2. 搜索包含特定关键词的岗位
```sql
SELECT *
FROM standard_positions
WHERE JSON_CONTAINS(keywords, '"前端"')
   OR name LIKE '%前端%'
ORDER BY name;
```

### 3. 获取某个行业下的所有信息
```sql
SELECT 
    *
FROM industries
WHERE code = 'I'  -- 信息技术行业
ORDER BY level, code;
```

### 4. 岗位的自动完成建议（支持中英文）
```sql
SELECT name
FROM standard_positions
WHERE is_active = TRUE
  AND (
    name LIKE CONCAT('%', ?, '%')
    OR en_name LIKE CONCAT('%', ?, '%')
  )
LIMIT 10;
```

### 5. 获取最相关的岗位（模糊匹配）
```sql
SELECT 
    sp.id,
    sp.name,
    sp.category_id,
    MATCH(sp.name, sp.en_name) AGAINST(? IN BOOLEAN MODE) AS relevance
FROM standard_positions sp
WHERE MATCH(sp.name, sp.en_name) AGAINST(? IN BOOLEAN MODE)
ORDER BY relevance DESC
LIMIT 10;
```

## 🛠️ 在前端中的应用

### 1. 岗位输入框的自动完成
```javascript
const positionInput = document.getElementById('position-input');
const suggestionList = [];

positionInput.addEventListener('input', async (e) => {
    const keyword = e.target.value;
    if (!keyword.trim()) return;

    // 从数据库查询建议
    const response = await fetch('/api/positions/suggestions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ keyword })
    });

    const suggestions = await response.json();
    // 显示建议列表...
});
```

### 2. 后端 API 示例 (Node.js/Express)
```javascript
app.post('/api/positions/suggestions', async (req, res) => {
    const { keyword } = req.body;
    
    const query = `
        SELECT name FROM standard_positions
        WHERE is_active = TRUE
          AND (name LIKE ? OR en_name LIKE ?)
        LIMIT 10
    `;
    
    const results = await db.query(query, 
        [`%${keyword}%`, `%${keyword}%`]
    );
    
    res.json(results);
});
```

### 3. 行业分类的树形展示
```javascript
// 获取所有一级行业
SELECT * FROM industries WHERE level = 1 ORDER BY code;

// 获取某个行业下的子行业
SELECT * FROM industries WHERE parent_id = ? ORDER BY code;
```

## 📈 性能优化

### 已创建的索引
- `idx_code` - 行业代码索引
- `idx_name` - 行业名称索引
- `idx_category` - 职位分类索引
- `ft_name` - 岗位全文索引
- `ft_name_industry` - 行业全文索引
- `ft_name_category` - 分类全文索引

### 查询优化建议
```sql
-- ❌ 避免
SELECT * FROM standard_positions WHERE keywords LIKE '%工程师%';

-- ✅ 使用 JSON_CONTAINS 或全文索引
SELECT * FROM standard_positions 
WHERE JSON_CONTAINS(keywords, '"工程师"')
  OR MATCH(name) AGAINST('工程师' IN BOOLEAN MODE);
```

## 🔄 数据更新和维护

### 添加新岗位
```sql
INSERT INTO standard_positions (
    name, en_name, category_id, keywords, is_active
) VALUES (
    '云计算工程师', 'Cloud Engineer', 1, '["云计算", "工程师"]', TRUE
);
```

### 禁用过时岗位
```sql
UPDATE standard_positions
SET is_active = FALSE
WHERE name = '已过时的岗位名称';
```

### 更新岗位关键词
```sql
UPDATE standard_positions
SET keywords = JSON_ARRAY('前端', '开发', '工程师')
WHERE name = '前端工程师';
```

## 🐛 常见问题

### Q: 如何导出岗位列表为 CSV？
```bash
mysql -h localhost -u root -p employee_cert \
  -e "SELECT name, en_name, category_id FROM standard_positions;" \
  > positions.csv
```

### Q: 如何支持自定义岗位？
```sql
-- 添加自定义标记
ALTER TABLE standard_positions ADD COLUMN is_custom BOOLEAN DEFAULT FALSE;

-- 查询时可区分标准和自定义岗位
SELECT * FROM standard_positions 
WHERE is_active = TRUE
ORDER BY is_custom, name;
```

### Q: 如何处理岗位的多语言支持？
当前表结构已支持 `en_name` 字段。若需更多语言，建议创建翻译表：
```sql
CREATE TABLE position_translations (
    id INT PRIMARY KEY AUTO_INCREMENT,
    position_id INT,
    language VARCHAR(10),  -- 'zh', 'en', 'ja', etc.
    name VARCHAR(100),
    FOREIGN KEY (position_id) REFERENCES standard_positions(id)
);
```

## 📚 参考资源

- [GitHub - ramwin/china-public-data](https://github.com/ramwin/china-public-data)
- [GitHub - egorvinogradov/job-titles-categories.json](https://gist.github.com/egorvinogradov/8d7b357fdbdcd7aeeae69ce82a60d247)
- [中国国民经济行业分类 GB/T 4754-2017](http://www.stats.gov.cn/)

## 💡 下一步建议

1. **集成到前端**：更新项目的 HTML 文件，使用数据库岗位列表替代硬编码的 `standardPositions`
2. **创建 API 端点**：在后端添加岗位查询 API
3. **实现缓存**：将热点查询结果缓存到 Redis
4. **添加管理界面**：创建岗位管理后台

---

**最后更新**: 2026-04-15  
**维护者**: Claude Code  
**许可证**: 与项目主体相同
