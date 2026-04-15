# 前端岗位库集成指南

本文档说明如何在前端集成新的岗位库系统，实现更智能的岗位输入和自动完成功能。

## 📋 概述

新的岗位库系统提供：
- 📊 **200+ 个标准岗位** - 覆盖各行业
- 🔍 **智能搜索和自动完成** - 支持中英文、模糊匹配
- 🏷️ **分类系统** - 10 个职位分类，48+ 个行业分类
- ⚡ **高性能查询** - 带全文索引和缓存优化

## 🛠️ 实现方案

### 方案 A：前端本地数据（简单）

直接在前端加载标准岗位列表，无需后端 API。

```javascript
// 加载标准岗位列表（替代现有的 standardPositions）
async function loadStandardPositions() {
    // 方式 1: 从 JSON 文件加载
    const response = await fetch('/data/standard-positions.json');
    return await response.json();
    
    // 方式 2: 从 localStorage 缓存
    let positions = localStorage.getItem('standardPositions');
    if (!positions) {
        const response = await fetch('/data/standard-positions.json');
        positions = await response.json();
        localStorage.setItem('standardPositions', JSON.stringify(positions));
    }
    return JSON.parse(positions);
}

// 初始化岗位输入框
async function initPositionInput() {
    const positions = await loadStandardPositions();
    
    document.getElementById('position-input').addEventListener('input', (e) => {
        const keyword = e.target.value.toLowerCase();
        if (!keyword.trim()) {
            clearSuggestions();
            return;
        }
        
        // 本地过滤
        const suggestions = positions.filter(pos =>
            pos.name.toLowerCase().includes(keyword) ||
            pos.keywords.some(kw => kw.toLowerCase().includes(keyword))
        ).slice(0, 10);
        
        showSuggestions(suggestions);
    });
}
```

**优点**：
- ✅ 无需后端支持，响应快
- ✅ 可离线使用
- ✅ 降低服务器压力

**缺点**：
- ❌ 前端加载大量数据
- ❌ 无法动态更新岗位列表

### 方案 B：后端 API 查询（推荐）

通过后端 API 查询岗位库，支持动态更新。

#### 1. 后端 API 实现

在 `backend-api-server.js` 中添加以下端点：

```javascript
const express = require('express');
const app = express();

// ============================================================
// 岗位查询 API
// ============================================================

/**
 * 获取岗位建议（用于输入框自动完成）
 * GET /api/positions/suggestions?keyword=前端&limit=10
 */
app.get('/api/positions/suggestions', (req, res) => {
    const keyword = req.query.keyword || '';
    const limit = parseInt(req.query.limit) || 10;
    
    if (!keyword.trim()) {
        res.json({ success: true, data: [] });
        return;
    }
    
    // 使用全文索引或模糊匹配
    const query = `
        SELECT id, name, en_name, keywords
        FROM standard_positions
        WHERE is_active = TRUE
          AND (
            name LIKE ?
            OR en_name LIKE ?
            OR JSON_CONTAINS(keywords, ?)
          )
        LIMIT ?
    `;
    
    const searchTerm = `%${keyword}%`;
    const keywordJson = JSON.stringify(keyword);
    
    db.query(query, [searchTerm, searchTerm, keywordJson, limit], 
        (error, results) => {
            if (error) {
                console.error('Database error:', error);
                res.status(500).json({ success: false, error: error.message });
                return;
            }
            
            res.json({ 
                success: true, 
                data: results.map(pos => ({
                    id: pos.id,
                    name: pos.name,
                    en_name: pos.en_name
                }))
            });
        }
    );
});

/**
 * 获取所有职位分类
 * GET /api/positions/categories
 */
app.get('/api/positions/categories', (req, res) => {
    const query = `
        SELECT id, name, en_name, description
        FROM position_categories
        ORDER BY display_order
    `;
    
    db.query(query, (error, results) => {
        if (error) {
            res.status(500).json({ success: false, error: error.message });
            return;
        }
        res.json({ success: true, data: results });
    });
});

/**
 * 获取某个分类下的所有岗位
 * GET /api/positions/by-category?categoryId=1
 */
app.get('/api/positions/by-category', (req, res) => {
    const categoryId = parseInt(req.query.categoryId);
    
    if (!categoryId) {
        res.status(400).json({ success: false, error: 'categoryId required' });
        return;
    }
    
    const query = `
        SELECT id, name, en_name, keywords
        FROM standard_positions
        WHERE category_id = ? AND is_active = TRUE
        ORDER BY name
    `;
    
    db.query(query, [categoryId], (error, results) => {
        if (error) {
            res.status(500).json({ success: false, error: error.message });
            return;
        }
        res.json({ success: true, data: results });
    });
});

/**
 * 获取行业分类列表
 * GET /api/industries?level=1
 */
app.get('/api/industries', (req, res) => {
    const level = parseInt(req.query.level);
    
    let query = 'SELECT id, code, name, en_name FROM industries WHERE 1=1';
    const params = [];
    
    if (level) {
        query += ' AND level = ?';
        params.push(level);
    }
    
    query += ' ORDER BY code';
    
    db.query(query, params, (error, results) => {
        if (error) {
            res.status(500).json({ success: false, error: error.message });
            return;
        }
        res.json({ success: true, data: results });
    });
});

/**
 * 搜索岗位（支持高级过滤）
 * GET /api/positions/search?keyword=工程师&categoryId=1&limit=20
 */
app.get('/api/positions/search', (req, res) => {
    const keyword = req.query.keyword || '';
    const categoryId = req.query.categoryId;
    const limit = parseInt(req.query.limit) || 20;
    
    let query = `
        SELECT sp.id, sp.name, sp.en_name, sp.keywords,
               pc.name as category_name
        FROM standard_positions sp
        LEFT JOIN position_categories pc ON sp.category_id = pc.id
        WHERE sp.is_active = TRUE
    `;
    const params = [];
    
    if (keyword.trim()) {
        query += ` AND (sp.name LIKE ? OR sp.en_name LIKE ?)`;
        const searchTerm = `%${keyword}%`;
        params.push(searchTerm, searchTerm);
    }
    
    if (categoryId) {
        query += ` AND sp.category_id = ?`;
        params.push(parseInt(categoryId));
    }
    
    query += ` LIMIT ?`;
    params.push(limit);
    
    db.query(query, params, (error, results) => {
        if (error) {
            res.status(500).json({ success: false, error: error.message });
            return;
        }
        res.json({ success: true, data: results });
    });
});
```

#### 2. 前端调用

```javascript
/**
 * 初始化岗位输入框（使用后端 API）
 */
async function initPositionInputWithAPI() {
    const positionInput = document.getElementById('position-input');
    const suggestionsList = document.getElementById('position-suggestions');
    
    // 防抖
    let searchTimeout;
    positionInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        const keyword = e.target.value.trim();
        
        if (!keyword) {
            suggestionsList.style.display = 'none';
            return;
        }
        
        searchTimeout = setTimeout(async () => {
            try {
                const response = await fetch(
                    `/api/positions/suggestions?keyword=${encodeURIComponent(keyword)}&limit=10`
                );
                const result = await response.json();
                
                if (result.success) {
                    displaySuggestions(result.data, suggestionsList);
                }
            } catch (error) {
                console.error('搜索岗位失败:', error);
            }
        }, 300); // 300ms 防抖
    });
    
    // 点击建议项时填充输入框
    suggestionsList.addEventListener('click', (e) => {
        if (e.target.classList.contains('suggestion-item')) {
            positionInput.value = e.target.textContent;
            suggestionsList.style.display = 'none';
        }
    });
}

/**
 * 显示建议列表
 */
function displaySuggestions(suggestions, container) {
    if (!suggestions.length) {
        container.style.display = 'none';
        return;
    }
    
    container.innerHTML = suggestions
        .map(pos => `
            <div class="suggestion-item" data-id="${pos.id}">
                ${pos.name}
                ${pos.en_name ? `<span class="en-name">${pos.en_name}</span>` : ''}
            </div>
        `)
        .join('');
    
    container.style.display = 'block';
}

/**
 * 加载职位分类
 */
async function loadPositionCategories() {
    try {
        const response = await fetch('/api/positions/categories');
        const result = await response.json();
        
        if (result.success) {
            // 渲染分类选择器或其他 UI
            return result.data;
        }
    } catch (error) {
        console.error('加载职位分类失败:', error);
    }
}

/**
 * 获取某个分类下的所有岗位
 */
async function getPositionsByCategory(categoryId) {
    try {
        const response = await fetch(
            `/api/positions/by-category?categoryId=${categoryId}`
        );
        const result = await response.json();
        return result.success ? result.data : [];
    } catch (error) {
        console.error('获取岗位列表失败:', error);
        return [];
    }
}
```

### 方案 C：混合方案（最优）

结合本地数据和 API，优化性能：

```javascript
/**
 * 混合方案：首次从 API 加载，后续使用本地缓存
 */
class PositionManager {
    constructor() {
        this.positions = [];
        this.categories = [];
        this.cacheTime = 24 * 60 * 60 * 1000; // 24小时缓存
    }
    
    async init() {
        const cached = this.getFromCache('positions');
        
        if (cached && !this.isCacheExpired()) {
            this.positions = cached;
            return;
        }
        
        // 从 API 加载
        await this.loadFromAPI();
        this.saveToCache('positions', this.positions);
    }
    
    async loadFromAPI() {
        try {
            const response = await fetch('/api/positions/search?limit=500');
            const result = await response.json();
            if (result.success) {
                this.positions = result.data;
            }
        } catch (error) {
            console.error('加载岗位数据失败:', error);
        }
    }
    
    search(keyword) {
        const kw = keyword.toLowerCase();
        return this.positions.filter(pos =>
            pos.name.toLowerCase().includes(kw) ||
            pos.en_name?.toLowerCase().includes(kw)
        ).slice(0, 10);
    }
    
    saveToCache(key, data) {
        localStorage.setItem(key, JSON.stringify({
            data,
            timestamp: Date.now()
        }));
    }
    
    getFromCache(key) {
        const cached = localStorage.getItem(key);
        if (!cached) return null;
        return JSON.parse(cached).data;
    }
    
    isCacheExpired() {
        const cached = localStorage.getItem('positions');
        if (!cached) return true;
        const { timestamp } = JSON.parse(cached);
        return Date.now() - timestamp > this.cacheTime;
    }
}

// 使用示例
const positionManager = new PositionManager();
await positionManager.init();

// 搜索岗位
const results = positionManager.search('工程师');
```

## 🎯 在现有页面中的集成

### 更新 employee-cert-complete.html

```javascript
// 替代现有的 standardPositions 数组
// 使用方案 B 或 C

// 假设使用方案 B
async function setupPositionAutocomplete() {
    const positionInput = document.getElementById('position');
    
    positionInput.addEventListener('input', async (e) => {
        const keyword = e.target.value;
        if (!keyword) return;
        
        const response = await fetch(
            `/api/positions/suggestions?keyword=${encodeURIComponent(keyword)}`
        );
        const { data } = await response.json();
        
        // 显示建议列表
        const suggestionList = document.getElementById('position-suggestions');
        suggestionList.innerHTML = data
            .map(pos => `<div class="suggestion">${pos.name}</div>`)
            .join('');
    });
}

// 页面初始化时调用
document.addEventListener('DOMContentLoaded', async () => {
    await setupPositionAutocomplete();
});
```

## 📈 性能优化建议

### 1. 缓存策略

```javascript
// 使用 LRU 缓存
class LRUCache {
    constructor(maxSize = 100) {
        this.maxSize = maxSize;
        this.cache = new Map();
    }
    
    get(key) {
        if (!this.cache.has(key)) return null;
        
        // 移到末尾（最近使用）
        const value = this.cache.get(key);
        this.cache.delete(key);
        this.cache.set(key, value);
        return value;
    }
    
    set(key, value) {
        if (this.cache.has(key)) {
            this.cache.delete(key);
        }
        
        this.cache.set(key, value);
        
        // 超过容量时删除最旧的
        if (this.cache.size > this.maxSize) {
            const firstKey = this.cache.keys().next().value;
            this.cache.delete(firstKey);
        }
    }
}

const searchCache = new LRUCache(100);
```

### 2. 防抖优化

```javascript
// 搜索防抖
function debounceSearch(fn, delay = 300) {
    let timeoutId;
    return function(...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => fn(...args), delay);
    };
}

const debouncedSearch = debounceSearch(
    async (keyword) => {
        // 执行搜索
    },
    300
);
```

### 3. 分页加载

```javascript
// 当建议列表很长时，使用分页
async function loadMoreSuggestions(keyword, page = 1) {
    const response = await fetch(
        `/api/positions/search?keyword=${keyword}&page=${page}&limit=10`
    );
    return await response.json();
}
```

## 🔗 相关文档

- [POSITIONS_DATABASE_README.md](./POSITIONS_DATABASE_README.md) - 数据库详细文档
- [BACKEND_SETUP.md](./BACKEND_SETUP.md) - 后端配置指南
- [01-前端认证流程文档.md](./01-前端认证流程文档.md) - 前端流程说明

## 📚 参考代码片段

### HTML 结构

```html
<!-- 岗位输入框 -->
<div class="form-group">
    <label>岗位 *</label>
    <input 
        type="text" 
        id="position-input" 
        placeholder="请输入或选择岗位"
        autocomplete="off"
    />
    <ul id="position-suggestions" class="suggestions-list" style="display: none;">
        <!-- 动态插入建议 -->
    </ul>
</div>

<!-- 样式 -->
<style>
.suggestions-list {
    position: absolute;
    background: white;
    border: 1px solid #ccc;
    border-top: none;
    list-style: none;
    margin: 0;
    padding: 0;
    max-height: 200px;
    overflow-y: auto;
    z-index: 10;
}

.suggestion-item {
    padding: 10px;
    cursor: pointer;
    border-bottom: 1px solid #eee;
}

.suggestion-item:hover {
    background-color: #f5f5f5;
}

.suggestion-item .en-name {
    font-size: 12px;
    color: #999;
    margin-left: 10px;
}
</style>
```

---

**最后更新**: 2026-04-15  
**建议方案**: 方案 B（后端 API）或方案 C（混合）
