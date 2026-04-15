#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动去重脚本 - 无需交互输入
使用标准去重模式（0.85阈值）
"""

import json
import re
from difflib import SequenceMatcher
from collections import defaultdict
from pathlib import Path

def normalize_position(pos):
    """标准化职位名称"""
    pos = pos.lower().strip()
    pos = re.sub(r'[^\w\s\u4e00-\u9fff]', '', pos)
    pos = re.sub(r'\s+', ' ', pos)
    return pos

def get_tokens(pos):
    """提取关键词"""
    tokens = set()
    words = pos.split()
    for w in words:
        if len(w) > 2:
            tokens.add(w)
        if len(w) >= 3:
            tokens.add(w[:3])
    return tokens

def similarity_score(s1, s2):
    """计算相似度"""
    if s1 == s2:
        return 1.0
    max_len = max(len(s1), len(s2))
    if max_len == 0:
        return 1.0
    return SequenceMatcher(None, s1, s2).ratio()

def main():
    print("=" * 90)
    print("⚡ 自动岗位去重工具（标准模式，0.85阈值）")
    print("=" * 90)

    # 加载
    json_file = '/Users/zhangrui/Claude工作/企业职工认证/positions-bilingual.json'
    print(f"\n📂 加载: {json_file}")

    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    positions = data['positions']
    print(f"✅ 已加载 {len(positions):,} 个岗位\n")

    threshold = 0.85

    # 第一步：建立关键词索引
    print("📑 步骤1/3：建立索引...")
    keyword_index = defaultdict(list)

    for i, pos in enumerate(positions):
        if i % 15000 == 0 and i > 0:
            print(f"  已索引 {i:,} 个岗位...")

        pos_cn = pos.get('name_cn', '').lower() if pos.get('name_cn') else ''
        pos_en = pos.get('name_en', '').lower() if pos.get('name_en') else ''

        norm_cn = normalize_position(pos_cn) if pos_cn else ''
        norm_en = normalize_position(pos_en) if pos_en else ''

        tokens = set()
        if norm_cn:
            tokens.update(get_tokens(norm_cn))
        if norm_en:
            tokens.update(get_tokens(norm_en))

        for token in tokens:
            keyword_index[token].append(i)

    print(f"✅ 索引完成：{len(keyword_index)} 个关键词\n")

    # 第二步：寻找相似岗位
    print("🔗 步骤2/3：寻找相似岗位...")

    duplicates = defaultdict(list)
    processed = set()

    for idx, pos in enumerate(positions):
        if idx % 15000 == 0 and idx > 0:
            progress = idx / len(positions) * 100
            print(f"  [{idx:,}/{len(positions):,}] {progress:.1f}% - 已找到 {len(duplicates)} 个组")

        if idx in processed:
            continue

        pos_cn = pos.get('name_cn', '')
        pos_en = pos.get('name_en', '')
        norm_cn = normalize_position(pos_cn) if pos_cn else ''
        norm_en = normalize_position(pos_en) if pos_en else ''

        # 获取候选
        candidates = set()
        tokens = set()
        if norm_cn:
            tokens.update(get_tokens(norm_cn))
        if norm_en:
            tokens.update(get_tokens(norm_en))

        for token in tokens:
            candidates.update(keyword_index[token])

        candidates.discard(idx)

        # 比较
        similar_group = [idx]
        for cand_idx in candidates:
            if cand_idx in processed or cand_idx == idx:
                continue

            cand_pos = positions[cand_idx]
            cand_cn = cand_pos.get('name_cn', '')
            cand_en = cand_pos.get('name_en', '')
            norm_cand_cn = normalize_position(cand_cn) if cand_cn else ''
            norm_cand_en = normalize_position(cand_en) if cand_en else ''

            max_score = 0
            if norm_cn and norm_cand_cn:
                max_score = max(max_score, similarity_score(norm_cn, norm_cand_cn))
            if norm_en and norm_cand_en:
                max_score = max(max_score, similarity_score(norm_en, norm_cand_en))
            if norm_cn and norm_cand_en:
                max_score = max(max_score, similarity_score(norm_cn, norm_cand_en) * 0.8)

            if max_score >= threshold:
                similar_group.append(cand_idx)
                processed.add(cand_idx)

        if len(similar_group) > 1:
            duplicates[idx] = similar_group

        processed.add(idx)

    print(f"✅ 找到 {len(duplicates)} 个相似岗位组\n")

    total_merged = sum(len(g) - 1 for g in duplicates.values())
    print(f"📋 相似岗位统计:")
    print(f"   相似组数: {len(duplicates)}")
    print(f"   可合并数: {total_merged} 个")
    print(f"   节省率: {total_merged / len(positions) * 100:.2f}%\n")

    # 第三步：合并
    print("🔄 步骤3/3：合并岗位...")

    merged = []
    removed_indices = set()
    merge_log = []

    for idx, pos in enumerate(positions):
        if idx % 15000 == 0 and idx > 0:
            progress = idx / len(positions) * 100
            print(f"  [{idx:,}/{len(positions):,}] {progress:.1f}% - 已合并")

        if idx in removed_indices:
            continue

        if idx in duplicates:
            group = duplicates[idx]
            for dup_idx in group[1:]:
                removed_indices.add(dup_idx)

            best_pos = pos
            removed_names = []

            for dup_idx in group[1:]:
                dup_pos = positions[dup_idx]
                if (best_pos.get('source') != 'chinese_original' and
                    dup_pos.get('source') == 'chinese_original'):
                    removed_names.append(best_pos.get('name_cn') or best_pos.get('name_en'))
                    best_pos = dup_pos
                elif ('name_cn' not in best_pos or not best_pos.get('name_cn')) and \
                     'name_cn' in dup_pos and dup_pos.get('name_cn'):
                    removed_names.append(best_pos.get('name_cn') or best_pos.get('name_en'))
                    best_pos = dup_pos
                else:
                    removed_names.append(dup_pos.get('name_cn') or dup_pos.get('name_en'))

            merged.append(best_pos)
            merge_log.append({
                'kept': best_pos.get('name_cn') or best_pos.get('name_en'),
                'merged': len(group) - 1,
                'removed': removed_names
            })
        else:
            merged.append(pos)

    print(f"✅ 合并完成\n")

    # 保存结果
    print("💾 保存结果...")

    output_file = '/Users/zhangrui/Claude工作/企业职工认证/positions-deduplicated.json'
    output_data = {
        'total': len(merged),
        'original_total': len(positions),
        'deduplicated': len(positions) - len(merged),
        'description': '去重后的中英文双语岗位库',
        'positions': merged
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"✅ JSON已保存: {output_file}")
    print(f"   大小: {len(json.dumps(output_data)) / 1024 / 1024:.1f} MB")

    # 生成报告
    report_file = '/Users/zhangrui/Claude工作/企业职工认证/DEDUPLICATION_REPORT.md'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# 岗位库自动去重报告\n\n")
        f.write(f"**处理时间**: 2026-04-15\n")
        f.write(f"**去重方式**: 高效分组去重\n")
        f.write(f"**相似度阈值**: {threshold}\n\n")
        f.write(f"## 📊 统计结果\n\n")
        f.write(f"| 指标 | 数值 |\n")
        f.write(f"|------|------|\n")
        f.write(f"| 原始岗位数 | {len(positions):,} |\n")
        f.write(f"| 去重后 | {len(merged):,} |\n")
        f.write(f"| 合并数量 | {len(positions) - len(merged):,} |\n")
        f.write(f"| 节省率 | {(len(positions) - len(merged)) / len(positions) * 100:.2f}% |\n")
        f.write(f"| 相似组数 | {len(duplicates)} |\n\n")

        f.write(f"## 📋 合并示例 (前30个)\n\n")
        f.write(f"| # | 保留岗位 | 合并数 | 移除的岗位 |\n")
        f.write(f"|---|----------|--------|------------|\n")

        for i, log in enumerate(merge_log[:30], 1):
            kept = log['kept'][:25]
            merged_count = log['merged']
            removed = ', '.join(str(x)[:15] for x in log['removed'][:2])
            if len(log['removed']) > 2:
                removed += f" +{len(log['removed'])-2}"
            f.write(f"| {i} | {kept} | {merged_count} | {removed} |\n")

        if len(merge_log) > 30:
            f.write(f"\n... 还有 {len(merge_log)-30} 个合并操作\n")

    print(f"✅ 报告已保存: {report_file}\n")

    # 最终统计
    print("=" * 90)
    print(f"✨ 岗位库去重完成！")
    print(f"   原始: {len(positions):,} → 去重后: {len(merged):,}")
    print(f"   节省: {len(positions) - len(merged):,} 个岗位 ({(len(positions) - len(merged)) / len(positions) * 100:.2f}%)")
    print("=" * 90 + "\n")

if __name__ == '__main__':
    main()
