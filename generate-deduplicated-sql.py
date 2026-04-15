#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从去重后的JSON生成SQL数据库脚本
"""

import json
import sys

def generate_sql(json_file):
    """生成SQL脚本"""
    print(f"📂 加载数据: {json_file}")

    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    positions = data['positions']
    total = len(positions)
    original = data.get('original_total', total)
    deduplicated = data.get('deduplicated', 0)

    print(f"✅ 加载完成: {total} 个岗位")
    if deduplicated > 0:
        print(f"   (从 {original} 个去重至 {total} 个，节省 {deduplicated} 个)\n")

    # 生成SQL
    sql_lines = []

    header = f"""-- ============================================================
-- 去重后的中英文双语岗位库 v3.0
-- 包含 {total:,} 个岗位（去重后）
-- 原始 {original:,} 个，合并 {deduplicated} 个重复岗位
-- ============================================================

TRUNCATE TABLE standard_positions;

INSERT INTO standard_positions (name, en_name, category_id, keywords, is_active) VALUES
"""

    sql_lines.append(header)

    # 按分类组织
    categories_map = {{
        'Technology': 1, 'Data': 2, 'Product': 3, 'Design': 4,
        'Sales': 5, 'Marketing': 6, 'HR': 7, 'Finance': 8,
        'Legal': 9, 'Operations': 10, 'Manufacturing': 11, 'Executive': 12, 'Other': 13
    }}

    sql_values = []
    for pos in positions:
        category_id = categories_map.get(pos.get('category', 'Other'), 13)

        cn_name = pos.get('name_cn', pos.get('name_en', ''))
        en_name = pos.get('name_en', '')

        # SQL转义
        cn_name = cn_name.replace("'", "\\'")
        en_name = en_name.replace("'", "\\'")

        # 生成关键词
        keywords = []
        if cn_name:
            keywords.append(cn_name)
        if en_name:
            keywords.extend(en_name.split()[:3])

        keywords_json = json.dumps(keywords, ensure_ascii=False)

        sql_values.append(
            f"('{cn_name}', '{en_name}', {category_id}, '{keywords_json}', TRUE)"
        )

    sql_lines.append(',\n'.join(sql_values) + ';')

    # 添加统计
    stats = f"""
-- ============================================================
-- 统计验证
-- ============================================================

SELECT '去重后的岗位库统计' AS metric;
SELECT COUNT(*) as 总岗位数 FROM standard_positions;
SELECT COUNT(DISTINCT category_id) as 职位分类数 FROM standard_positions;
SELECT category_id, COUNT(*) as 岗位数
FROM standard_positions
GROUP BY category_id
ORDER BY category_id;

-- 显示样本数据
SELECT name as 中文, en_name as 英文, category_id
FROM standard_positions
LIMIT 30;
"""

    sql_lines.append(stats)

    return '\n'.join(sql_lines)

if __name__ == '__main__':
    json_file = sys.argv[1] if len(sys.argv) > 1 else \
                '/Users/zhangrui/Claude工作/企业职工认证/positions-deduplicated.json'

    sql_script = generate_sql(json_file)

    # 保存SQL
    output_file = json_file.replace('.json', '.sql')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(sql_script)

    print(f"\n📝 SQL脚本已生成")
    print(f"✅ 保存为: {output_file}")
    print(f"   大小: {len(sql_script) / 1024 / 1024:.1f} MB")
    print(f"   岗位数: {len(json.loads(open(json_file).read())['positions']):,}")
