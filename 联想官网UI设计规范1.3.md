# 联想官网 UI 设计规范 1.3
> Lenovo Official Website Design System — Claude Code Reference

---

## 目录 Table of Contents

1. [品牌标识 Brand Identity](#1-品牌标识-brand-identity)
2. [颜色系统 Color System](#2-颜色系统-color-system)
3. [按钮规范 Button System](#3-按钮规范-button-system)
4. [卡片规范 Card System](#4-卡片规范-card-system)
5. [输入框规范 Input System](#5-输入框规范-input-system)
6. [图标库 Icon Library](#6-图标库-icon-library)
7. [CSS 变量速查 CSS Variables](#7-css-变量速查-css-variables)
8. [使用规则 Usage Rules](#8-使用规则-usage-rules)

---

## 1. 品牌标识 Brand Identity

### Logo

| 属性 | 值 |
|------|-----|
| Logo 图片地址 | `https://p4.lefile.cn/fes/cms/2021/09/24/skz7mq0zavm0hd8xfaq0nrofxcwje3959207.png` |
| 推荐用法 | `<img src="[上方地址]" alt="Lenovo 联想" />` |

> **规则**：Logo 不可变色、拉伸、裁切，背景需保持足够对比度。

---

## 2. 颜色系统 Color System

### 2.1 主色 Primary Color

| 名称 | Token | HEX | 用途 |
|------|-------|-----|------|
| 主色 | `--color-primary` | `#FF2F2F` | 页面需要突出的位置，CTA 按钮、强调元素 |

### 2.2 辅色 Secondary Colors

| 名称 | Token | HEX | 用途 |
|------|-------|-----|------|
| 辅色1 | `--color-secondary-1` | `#252525` | 最常用，正文文字、标题 |
| 辅色2 | `--color-secondary-2` | `#454545` | 配合辅色1，次级文字 |
| 辅色3 | `--color-secondary-3` | `#606060` | 配合辅色1，三级文字 |
| 辅色4 | `--color-secondary-4` | `#979797` | 配合辅色1、辅色2，提示文字、占位符 |
| 辅色5 | `--color-secondary-5` | `#BDBDBD` | 装饰文字、禁用状态文字 |
| 辅色6 | `--color-secondary-6` | `#F6F6F6` | 背景色，页面底色 |

### 2.3 中性色 Neutral Colors

| 名称 | Token | HEX | 用途 |
|------|-------|-----|------|
| 白色 | `--color-white` | `#FFFFFF` | 纯白背景、实心按钮文字 |
| 近白 | `--color-near-white` | `#FCFCFC` | 输入框背景、卡片背景 |
| 浅灰边框 | `--color-border-light` | `#DBDBDB` | 默认边框、分隔线 |
| 深灰边框 | `--color-border-dark` | `#454545` | 聚焦边框、线性按钮边框 |
| 主色浅底 | `--color-primary-light` | `#FFF9F9` | 选中卡片高亮背景 |

---

## 3. 按钮规范 Button System

### 3.1 实心按钮 Solid Button（主要操作）

| 属性 | 值 | Token |
|------|-----|-------|
| 背景色 | `#FF2F2F` | `--color-primary` |
| 边框色 | `#FF2F2F` | `--color-primary` |
| 文字色 | `#FFFFFF` | `--color-white` |

```css
/* 实心按钮 Solid Button */
.btn-solid {
  background-color: var(--color-primary);
  border: 1px solid var(--color-primary);
  color: var(--color-white);
  cursor: pointer;
}

.btn-solid:hover {
  opacity: 0.88;
}

.btn-solid:active {
  opacity: 0.75;
}
```

### 3.2 线性按钮 Outlined Button（次要操作）

| 属性 | 值 | Token |
|------|-----|-------|
| 背景色 | `#FFFFFF` | `--color-white` |
| 边框色 | `#252525` | `--color-secondary-1` |
| 文字色 | `#252525` | `--color-secondary-1` |

```css
/* 线性按钮 Outlined Button */
.btn-outlined {
  background-color: var(--color-white);
  border: 1px solid var(--color-secondary-1);
  color: var(--color-secondary-1);
  cursor: pointer;
}

.btn-outlined:hover {
  background-color: var(--color-secondary-6);
}
```

---

## 4. 卡片规范 Card System

### 4.1 选中状态 Selected State

| 属性 | 值 | Token |
|------|-----|-------|
| 高亮背景色 | `#FFF9F9` | `--color-primary-light` |
| 边框色 | `#FF2F2F` | `--color-primary` |
| 文字色 | `#252525` | `--color-secondary-1` |

### 4.2 未选中状态 Unselected State

| 属性 | 值 | Token |
|------|-----|-------|
| 背景色 | `#FCFCFC` | `--color-near-white` |
| 边框色 | `#DBDBDB` | `--color-border-light` |
| 文字色 | `#252525` | `--color-secondary-1` |

```css
/* 卡片 Card */
.card {
  background-color: var(--color-near-white);
  border: 1px solid var(--color-border-light);
  color: var(--color-secondary-1);
}

.card.selected {
  background-color: var(--color-primary-light);
  border-color: var(--color-primary);
}
```

---

## 5. 输入框规范 Input System

### 5.1 未输入状态 Default State

| 属性 | 值 | Token |
|------|-----|-------|
| 背景色 | `#FCFCFC` | `--color-near-white` |
| 边框色 | `#DBDBDB` | `--color-border-light` |
| 文字色（占位符）| `#979797` | `--color-secondary-4` |

### 5.2 输入中状态 Active State

| 属性 | 值 | Token |
|------|-----|-------|
| 背景色 | `#FCFCFC` | `--color-near-white` |
| 边框色 | `#454545` | `--color-secondary-2` |
| 文字色 | `#252525` | `--color-secondary-1` |

### 5.3 报错状态 Error State

| 属性 | 值 | Token |
|------|-----|-------|
| 背景色 | `#FCFCFC` | `--color-near-white` |
| 边框色 | `#FF2F2F` | `--color-primary` |
| 文字色 | `#FF2F2F` | `--color-primary` |

```css
/* 输入框 Input */
.input {
  background-color: var(--color-near-white);
  border: 1px solid var(--color-border-light);
  color: var(--color-secondary-4); /* placeholder */
}

.input:focus {
  border-color: var(--color-secondary-2);
  color: var(--color-secondary-1);
  outline: none;
}

.input.error {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.input::placeholder {
  color: var(--color-secondary-4);
}
```

---

## 6. 图标库 Icon Library

### 6.1 官方图标库

| 属性 | 值 |
|------|-----|
| 图标库名称 | IconPark |
| 官方地址 | [https://iconpark.oceanengine.com/official](https://iconpark.oceanengine.com/official) |
| 提供方 | 字节跳动开源 |

### 6.2 使用规范

- **优先使用** IconPark 官方图标库，保持全站图标风格统一
- **推荐风格**：`outline`（线性）风格，与联想官网整体轻量简洁的视觉调性一致
- **图标颜色**：遵循颜色系统，使用 `--color-secondary-1` 至 `--color-secondary-4` 区间，强调图标使用 `--color-primary`
- **禁止**混用多种图标库来源，避免风格不统一

### 6.3 引入方式（NPM）

```bash
npm install @icon-park/react   # React 项目
npm install @icon-park/vue-next  # Vue 3 项目
npm install @icon-park/svg     # 纯 SVG / 原生 HTML
```

```jsx
// React 示例
import { Search } from '@icon-park/react';

<Search theme="outline" size="20" fill="var(--color-secondary-1)" />
```

---

## 7. CSS 变量速查 CSS Variables

将以下变量粘贴至项目全局样式（如 `global.css` / `variables.css` / `:root`）：

```css
:root {
  /* === 主色 Primary === */
  --color-primary: #FF2F2F;
  --color-primary-light: #FFF9F9;

  /* === 辅色 Secondary === */
  --color-secondary-1: #252525;   /* 正文主色 */
  --color-secondary-2: #454545;   /* 次级文字 */
  --color-secondary-3: #606060;   /* 三级文字 */
  --color-secondary-4: #979797;   /* 提示/占位 */
  --color-secondary-5: #BDBDBD;   /* 装饰/禁用 */
  --color-secondary-6: #F6F6F6;   /* 页面背景 */

  /* === 中性色 Neutral === */
  --color-white: #FFFFFF;
  --color-near-white: #FCFCFC;
  --color-border-light: #DBDBDB;
  --color-border-dark: #454545;
}
```

---

## 8. 使用规则 Usage Rules

### 7.1 颜色使用优先级

```
强调/CTA        → --color-primary (#FF2F2F)
正文/标题        → --color-secondary-1 (#252525)
副标题/次级文字   → --color-secondary-2 (#454545)
辅助说明文字     → --color-secondary-3 (#606060)
占位/提示文字    → --color-secondary-4 (#979797)
禁用/装饰文字    → --color-secondary-5 (#BDBDBD)
页面背景         → --color-secondary-6 (#F6F6F6)
组件背景         → --color-near-white (#FCFCFC)
```

### 7.2 禁止事项 Don'ts

- ❌ 不得使用规范外颜色（如自定义蓝色、绿色等）
- ❌ 不得将主色 `#FF2F2F` 用于大面积背景
- ❌ 不得在白色背景上使用辅色5 `#BDBDBD` 承载关键信息（对比度不足）
- ❌ 不得修改 Logo 图片颜色或比例

### 7.3 组件状态对照速查

| 组件 | 状态 | 背景 | 边框 | 文字 |
|------|------|------|------|------|
| 实心按钮 | 默认 | `#FF2F2F` | `#FF2F2F` | `#FFFFFF` |
| 线性按钮 | 默认 | `#FFFFFF` | `#252525` | `#252525` |
| 卡片 | 选中 | `#FFF9F9` | `#FF2F2F` | `#252525` |
| 卡片 | 未选中 | `#FCFCFC` | `#DBDBDB` | `#252525` |
| 输入框 | 默认 | `#FCFCFC` | `#DBDBDB` | `#979797` |
| 输入框 | 聚焦 | `#FCFCFC` | `#454545` | `#252525` |
| 输入框 | 报错 | `#FCFCFC` | `#FF2F2F` | `#FF2F2F` |

---

> 版本：1.3 ｜ 来源：联想官网UI设计规范1_0.pdf ｜ 适用项目：联想官网 Claude Code 开发
