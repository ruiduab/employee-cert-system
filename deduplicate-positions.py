#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能岗位去重脚本
合并相似度高的岗位名称，支持中英文
"""

import json
import re
from difflib import SequenceMatcher
from collections import defaultdict
from pathlib import Path

def levenshtein_distance(s1, s2):
    """编辑距离算法 - 计算两个字符串的相似度"""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]

def similarity_score(s1, s2):
    """计算两个字符串的相似度分数 (0-1)"""
    max_len = max(len(s1), len(s2))
    if max_len == 0:
        return 1.0

    # 方法1：Levenshtein距离
    distance = levenshtein_distance(s1, s2)
    leven_score = 1 - (distance / max_len)

    # 方法2：SequenceMatcher
    seq_score = SequenceMatcher(None, s1, s2).ratio()

    # 综合评分（权重各占50%）
    return (leven_score + seq_score) / 2

def normalize_position(pos):
    """标准化职位名称用于比较"""
    # 转小写
    pos = pos.lower().strip()
    # 移除特殊字符
    pos = re.sub(r'[^\w\s\u4e00-\u9fff]', '', pos)
    # 规范空格
    pos = re.sub(r'\s+', ' ', pos)
    return pos

def find_duplicate_groups(positions, threshold=0.85):
    """
    找出相似的岗位组
    threshold: 相似度阈值（0-1）
    """
    groups = []
    used = set()

    positions_with_idx = [(i, p) for i, p in enumerate(positions)]

    print(f"\n🔍 开始检测重复岗位（阈值: {threshold})...")
    print(f"   总岗位数: {len(positions)}\n")

    for i, (idx1, pos1) in enumerate(positions_with_idx):
        if idx1 in used:
            continue

        if (i + 1) % 5000 == 0:
            progress = (i + 1) / len(positions) * 100
            print(f"  [{i+1:6d}/{len(positions)}] {progress:5.1f}% - 找到{len(groups)}个相似组")

        # 获取岗位名称
        pos1_cn = pos1.get('name_cn', '')
        pos1_en = pos1.get('name_en', '')

        group = [idx1]

        # 与后续岗位比较
        for idx2, pos2 in positions_with_idx[i+1:]:
            if idx2 in used:
                continue

            pos2_cn = pos2.get('name_cn', '')
            pos2_en = pos2.get('name_en', '')

            # 比较中文名称
            if pos1_cn and pos2_cn:
                cn_score = similarity_score(normalize_position(pos1_cn),
                                           normalize_position(pos2_cn))
                if cn_score >= threshold:
                    group.append(idx2)
                    used.add(idx2)
                    continue

            # 比较英文名称
            if pos1_en and pos2_en:
                en_score = similarity_score(normalize_position(pos1_en),
                                           normalize_position(pos2_en))
                if en_score >= threshold:
                    group.append(idx2)
                    used.add(idx2)
                    continue

            # 中英文交叉比较（针对翻译偏差）
            if pos1_cn and pos2_en:
                cross_score = similarity_score(normalize_position(pos1_cn),
                                              normalize_position(pos2_en))
                if cross_score >= 0.7:  # 更低阈值
                    group.append(idx2)
                    used.add(idx2)
                    continue

        if len(group) > 1:
            groups.append(group)
            used.add(idx1)

    return groups

def merge_duplicate_positions(positions, groups):
    """
    合并重复岗位，保留最佳版本
    """
    print(f"\n📋 开始合并 {len(groups)} 个相似岗位组...\n")

    merged_positions = []
    merged_indices = set()
    merge_log = []

    # 处理重复组
    for group_idx, group in enumerate(groups):
        if (group_idx + 1) % 1000 == 0:
            progress = (group_idx + 1) / len(groups) * 100
            print(f"  [{group_idx+1:6d}/{len(groups)}] {progress:5.1f}%")

        # 找出最完整的岗位（优先级：有中文 > 完整 > 更新）
        best_idx = group[0]
        best_pos = positions[best_idx]

        for idx in group[1:]:
            pos = positions[idx]
            # 优先级：原始中文数据 > 有中文名称 > 英文完整
            if (best_pos.get('source') != 'chinese_original' and
                pos.get('source') == 'chinese_original'):
                best_idx = idx
                best_pos = pos
            elif ('name_cn' not in best_pos or not best_pos.get('name_cn')) and \
                 'name_cn' in pos and pos.get('name_cn'):
                best_idx = idx
                best_pos = pos

        merged_indices.add(best_idx)
        merged_positions.append(best_pos)

        # 记录合并信息
        merged_names = []
        for idx in group:
            pos = positions[idx]
            name = pos.get('name_cn') or pos.get('name_en', '?')
            if name not in merged_names:
                merged_names.append(name)

        merge_log.append({
            'kept': best_pos.get('name_cn') or best_pos.get('name_en'),
            'merged_count': len(group) - 1,
            'removed_names': [n for n in merged_names if n != (best_pos.get('name_cn') or best_pos.get('name_en'))]
        })

    # 添加未重复的岗位
    for i, pos in enumerate(positions):
        if i not in merged_indices and not any(i in g for g in groups):
            merged_positions.append(pos)

    return merged_positions, merge_log

def main():
    print("=" * 90)
    print("🧹 岗位库智能去重工具")
    print("=" * 90)

    # 加载数据
    json_file = '/Users/zhangrui/Claude工作/企业职工认证/positions-bilingual.json'
    print(f"\n📂 加载岗位数据: {json_file}")

    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    positions = data['positions']
    print(f"✅ 已加载 {len(positions)} 个岗位\n")

    # 选择相似度阈值
    print("🎯 相似度阈值:")
    print("   1. 严格去重 (0.95) - 只合并几乎相同的岗位")
    print("   2. 标准去重 (0.85) - 合并很相似的岗位 ✅ 推荐")
    print("   3. 宽松去重 (0.75) - 合并相似的岗位\n")

    choice = input("选择 (1/2/3, 默认2): ").strip() or '2'
    thresholds = {'1': 0.95, '2': 0.85, '3': 0.75}
    threshold = thresholds.get(choice, 0.85)

    # 查找重复
    groups = find_duplicate_groups(positions, threshold)

    if not groups:
        print(f"\n✅ 未找到相似岗位！当前库已经很干净。")
        return

    print(f"\n✅ 找到 {len(groups)} 个相似岗位组")
    print(f"   可合并的重复岗位: {sum(len(g) - 1 for g in groups)} 个\n")

    # 显示示例
    print("📋 合并示例 (前10个):")
    print(f"{'#':<4} {'操作':<60} {'合并数':<4}")
    print("─" * 90)

    for i, group in enumerate(groups[:10], 1):
        primary = positions[group[0]]
        primary_name = primary.get('name_cn') or primary.get('name_en', '?')
        other_names = []
        for idx in group[1:]:
            pos = positions[idx]
            name = pos.get('name_cn') or pos.get('name_en', '?')
            other_names.append(name)

        operation = f"{primary_name} ← {', '.join(other_names[:2])}"
        if len(other_names) > 2:
            operation += f" ... ({len(other_names)-2}个)"

        print(f"{i:<4} {operation:<60} {len(group)-1:<4}")

    if len(groups) > 10:
        print(f"{'...':<4} {'... 还有' + str(len(groups)-10) + '个组 ...':<60}")

    # 确认合并
    confirm = input(f"\n继续合并？(y/n, 默认n): ").strip().lower()
    if confirm != 'y':
        print("取消合并")
        return

    # 执行合并
    merged_positions, merge_log = merge_duplicate_positions(positions, groups)

    print(f"\n✅ 合并完成!")
    print(f"   原始数量: {len(positions):,}")
    print(f"   合并后: {len(merged_positions):,}")
    print(f"   减少: {len(positions) - len(merged_positions):,} 个 ({(len(positions) - len(merged_positions)) / len(positions) * 100:.2f}%)")

    # 生成合并报告
    print(f"\n📊 合并统计:")
    total_merged = sum(log['merged_count'] for log in merge_log)
    print(f"   总合并操作: {total_merged}")

    # 保存结果
    output_file = '/Users/zhangrui/Claude工作/企业职工认证/positions-deduplicated.json'
    output_data = {
        'total': len(merged_positions),
        'original_total': len(positions),
        'deduplicated': len(positions) - len(merged_positions),
        'description': '去重后的岗位库',
        'positions': merged_positions
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"\n📝 保存去重后的JSON...")
    print(f"✅ 已保存: {output_file}")
    print(f"   大小: {len(json.dumps(output_data)) / 1024 / 1024:.1f} MB")

    # 保存合并报告
    report_file = '/Users/zhangrui/Claude工作/企业职工认证/DEDUPLICATION_REPORT.md'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# 岗位库去重报告\n\n")
        f.write(f"**处理时间**: 2026-04-15\n")
        f.write(f"**相似度阈值**: {threshold}\n\n")
        f.write(f"## 统计结果\n\n")
        f.write(f"- 原始岗位数: {len(positions):,}\n")
        f.write(f"- 去重后: {len(merged_positions):,}\n")
        f.write(f"- 合并数量: {len(positions) - len(merged_positions):,} ({(len(positions) - len(merged_positions)) / len(positions) * 100:.2f}%)\n")
        f.write(f"- 相似岗位组: {len(groups)}\n\n")

        f.write(f"## 合并示例 (前20个)\n\n")
        f.write(f"| # | 保留 | 合并数 | 移除的名称 |\n")
        f.write(f"|---|------|--------|------------|\n")

        for i, log in enumerate(merge_log[:20], 1):
            kept = log['kept'][:30]
            merged_count = log['merged_count']
            removed = ', '.join(log['removed_names'][:3])
            if len(log['removed_names']) > 3:
                removed += f" ... ({len(log['removed_names'])-3}个)"
            f.write(f"| {i} | {kept} | {merged_count} | {removed} |\n")

        if len(merge_log) > 20:
            f.write(f"\n... 还有 {len(merge_log)-20} 个合并操作\n")

    print(f"\n📊 合并报告已保存: {report_file}")

    print(f"\n{'='*90}")
    print(f"✨ 岗位库去重完成！")
    print(f"   下一步：更新SQL脚本导入新的去重数据库")
    print(f"{'='*90}\n")

if __name__ == '__main__':
    main()
