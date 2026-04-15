#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
岗位库扩展脚本
整合70k英文岗位和中文岗位，进行去重、分类、归一化

数据来源：
- jneidel/job-titles (70k+ 英文岗位)
- 项目现有的71个中文岗位
"""

import json
import re
from pathlib import Path
from collections import defaultdict

# 中文岗位原始数据（从现有SQL中提取）
CHINESE_POSITIONS = [
    ('产品经理', 'Product Manager', 1),
    ('产品总监', 'Director of Product', 2),
    ('产品助理', 'Product Assistant', 3),
    ('产品运营', 'Product Operations', 4),
    ('技术总监', 'Director of Technology', 5),
    ('工程师', 'Engineer', 6),
    ('开发工程师', 'Development Engineer', 7),
    ('前端工程师', 'Frontend Engineer', 8),
    ('后端工程师', 'Backend Engineer', 9),
    ('全栈工程师', 'Full Stack Engineer', 10),
    ('架构师', 'Architect', 11),
    ('技术主管', 'Technical Lead', 12),
    ('软件工程师', 'Software Engineer', 13),
    ('程序员', 'Programmer', 14),
    ('开发者', 'Developer', 15),
    ('iOS开发工程师', 'iOS Developer', 16),
    ('Android开发工程师', 'Android Developer', 17),
    ('小程序开发', 'Mini Program Developer', 18),
    ('移动端开发', 'Mobile Developer', 19),
    ('设计师', 'Designer', 20),
    ('平面设计师', 'Graphic Designer', 21),
    ('UI设计师', 'UI Designer', 22),
    ('交互设计师', 'Interaction Designer', 23),
    ('视觉设计师', 'Visual Designer', 24),
    ('用户体验设计师', 'UX Designer', 25),
    ('销售经理', 'Sales Manager', 26),
    ('销售总监', 'Sales Director', 27),
    ('业务经理', 'Business Manager', 28),
    ('客户经理', 'Account Manager', 29),
    ('渠道经理', 'Channel Manager', 30),
    ('销售代表', 'Sales Representative', 31),
    ('市场经理', 'Marketing Manager', 32),
    ('市场总监', 'Marketing Director', 33),
    ('品牌经理', 'Brand Manager', 34),
    ('内容运营', 'Content Operations', 35),
    ('社区运营', 'Community Operations', 36),
    ('人力资源', 'Human Resources', 37),
    ('人力资源经理', 'HR Manager', 38),
    ('行政', 'Administration', 39),
    ('招聘', 'Recruiter', 40),
    ('财务', 'Finance', 41),
    ('财务经理', 'Finance Manager', 42),
    ('成本会计', 'Cost Accountant', 43),
    ('税务经理', 'Tax Manager', 44),
    ('会计', 'Accountant', 45),
    ('法律顾问', 'Legal Counsel', 46),
    ('法务', 'Legal Affairs', 47),
    ('律师', 'Lawyer', 48),
    ('合规经理', 'Compliance Manager', 49),
    ('项目经理', 'Project Manager', 50),
    ('项目总监', 'Project Director', 51),
    ('运营经理', 'Operations Manager', 52),
    ('供应链经理', 'Supply Chain Manager', 53),
    ('质量经理', 'Quality Manager', 54),
    ('制造工程师', 'Manufacturing Engineer', 55),
    ('工业工程师', 'Industrial Engineer', 56),
    ('制造经理', 'Manufacturing Manager', 57),
    ('采购经理', 'Procurement Manager', 58),
    ('采购总监', 'Procurement Director', 59),
    ('物流经理', 'Logistics Manager', 60),
    ('仓储经理', 'Warehouse Manager', 61),
    ('部门经理', 'Department Manager', 62),
    ('总经理', 'General Manager', 63),
    ('董事长', 'Chairman', 64),
    ('总裁', 'President', 65),
    ('首席执行官', 'CEO', 66),
    ('数据科学家', 'Data Scientist', 67),
    ('数据分析师', 'Data Analyst', 68),
    ('算法工程师', 'Algorithm Engineer', 69),
    ('机器学习工程师', 'Machine Learning Engineer', 70),
    ('实习生', 'Intern', 71),
]

# 职位关键词映射（用于分类）
CATEGORY_KEYWORDS = {
    'Technology': ['developer', 'engineer', 'programmer', 'architect', 'software', 'web', 'backend', 'frontend', 'code', 'devops', 'cloud', 'sre'],
    'Design': ['designer', 'design', 'ui', 'ux', 'graphic', 'visual', 'interaction', 'industrial', 'product designer'],
    'Product': ['product', 'pm'],
    'Sales': ['sales', 'account executive', 'business development', 'rep', 'seller'],
    'Marketing': ['marketing', 'market', 'content', 'social', 'advertising', 'brand'],
    'HR': ['human resources', 'hr', 'recruiter', 'recruitment', 'talent'],
    'Finance': ['accountant', 'accounting', 'finance', 'auditor', 'tax', 'cfo', 'controller', 'treasurer'],
    'Legal': ['lawyer', 'attorney', 'legal', 'counsel', 'compliance'],
    'Operations': ['operations', 'project manager', 'project management', 'operations manager', 'logistics', 'supply chain'],
    'Data': ['data scientist', 'data analyst', 'analytics', 'bi', 'business intelligence'],
    'Manufacturing': ['manufacturing', 'production', 'quality', 'industrial'],
    'Executive': ['ceo', 'cto', 'cfo', 'director', 'vp', 'vice president', 'president', 'chairman', 'executive'],
}

def categorize_position(position_en):
    """根据职位英文名称进行分类"""
    pos_lower = position_en.lower()

    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in pos_lower for kw in keywords):
            return category

    return 'Other'

def normalize_position(position):
    """标准化职位名称"""
    # 转为小写
    pos = position.lower().strip()
    # 删除多余空格
    pos = re.sub(r'\s+', ' ', pos)
    # 删除特殊符号
    pos = re.sub(r'[^\w\s-]', '', pos)
    return pos

def load_english_positions(json_file):
    """加载英文岗位"""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('job-titles', [])
    except Exception as e:
        print(f"⚠️  加载英文岗位失败: {e}")
        return []

def deduplicate_and_categorize(chinese_pos, english_pos):
    """去重和分类"""
    seen = set()
    merged_positions = []
    category_count = defaultdict(int)

    # 先添加中文岗位
    print(f"\n📝 处理中文岗位 ({len(chinese_pos)} 个)...")
    for cn_name, en_name, idx in chinese_pos:
        norm_name = normalize_position(en_name)
        if norm_name not in seen:
            seen.add(norm_name)
            category = categorize_position(en_name)
            category_count[category] += 1
            merged_positions.append({
                'name_cn': cn_name,
                'name_en': en_name,
                'category': category,
                'source': 'chinese_original'
            })

    # 再添加英文岗位（去重）
    print(f"📝 处理英文岗位 ({len(english_pos)} 个)...")
    duplicates = 0
    for en_pos in english_pos:
        norm_pos = normalize_position(en_pos)
        # 避免重复和很短的岗位名
        if norm_pos not in seen and len(en_pos) > 2:
            seen.add(norm_pos)
            category = categorize_position(en_pos)
            category_count[category] += 1
            merged_positions.append({
                'name_en': en_pos,
                'category': category,
                'source': 'english_jneidel'
            })
        else:
            duplicates += 1

    print(f"✅ 合并完成:")
    print(f"  - 中文岗位: {len([p for p in merged_positions if 'name_cn' in p])}")
    print(f"  - 英文岗位: {len([p for p in merged_positions if 'name_cn' not in p])}")
    print(f"  - 去重数量: {duplicates}")
    print(f"  - 最终总数: {len(merged_positions)}")

    print(f"\n📊 按分类统计:")
    for category in sorted(category_count.keys()):
        count = category_count[category]
        print(f"  - {category}: {count}")

    return merged_positions

def generate_sql(positions):
    """生成扩展的SQL脚本"""
    sql_lines = []

    # 添加扩展职位分类表
    sql_lines.append("""-- ============================================================
-- 扩展的职位分类表
-- ============================================================

-- 清空并重新定义职位分类（包含新的分类）
TRUNCATE TABLE position_categories;

INSERT INTO position_categories (name, en_name, description, display_order) VALUES
('技术开发', 'Technology', '软件开发、工程师等技术岗位', 1),
('数据分析', 'Data', '数据科学家、分析师等数据岗位', 2),
('产品管理', 'Product', '产品经理等产品相关岗位', 3),
('设计', 'Design', 'UI/UX设计、平面设计等设计岗位', 4),
('销售业务', 'Sales', '销售、客户代表等销售岗位', 5),
('市场营销', 'Marketing', '市场经理、品牌经理等营销岗位', 6),
('人力资源', 'HR', '招聘、HR等人力资源岗位', 7),
('财务会计', 'Finance', '财务、会计等财务岗位', 8),
('法律合规', 'Legal', '律师、法务等法律岗位', 9),
('运营管理', 'Operations', '项目经理、运营等管理岗位', 10),
('制造生产', 'Manufacturing', '制造工程师、生产经理等岗位', 11),
('其他', 'Other', '其他岗位', 99);

-- ============================================================
-- 清空并重新导入标准岗位库（扩展版）
-- ============================================================

TRUNCATE TABLE standard_positions;

INSERT INTO standard_positions (name, en_name, category_id, keywords, is_active) VALUES
""")

    # 按分类组织数据
    categories_map = {
        'Technology': 1,
        'Data': 2,
        'Product': 3,
        'Design': 4,
        'Sales': 5,
        'Marketing': 6,
        'HR': 7,
        'Finance': 8,
        'Legal': 9,
        'Operations': 10,
        'Manufacturing': 11,
        'Other': 12
    }

    sql_values = []
    for idx, pos in enumerate(positions):
        category_id = categories_map.get(pos['category'], 12)

        if 'name_cn' in pos:
            # 中文岗位
            name = pos['name_cn']
            en_name = pos.get('name_en', '')
            keywords = json.dumps([name] + en_name.split()[:2])
        else:
            # 英文岗位
            name = pos['name_en']
            en_name = pos['name_en']
            keywords = json.dumps([name.split()[0]] if name else [])

        sql_values.append(
            f"('{name}', '{en_name}', {category_id}, '{keywords}', TRUE)"
        )

    sql_lines.append(',\n'.join(sql_values) + ';')

    # 添加统计信息
    sql_lines.append("""
-- ============================================================
-- 统计验证
-- ============================================================

SELECT '扩展岗位库统计' AS metric;
SELECT COUNT(*) as 标准岗位数 FROM standard_positions;
SELECT COUNT(DISTINCT category_id) as 职位分类数 FROM standard_positions;
SELECT category_id, COUNT(*) as 岗位数 FROM standard_positions GROUP BY category_id ORDER BY category_id;
""")

    return '\n'.join(sql_lines)

def main():
    print("=" * 70)
    print("🚀 岗位库扩展工具 - 合并71个中文 + 70k+ 英文岗位")
    print("=" * 70)

    # 加载英文岗位
    english_positions = load_english_positions('/tmp/job-titles-en.json')
    print(f"✅ 加载英文岗位: {len(english_positions)} 个")

    # 合并和去重
    merged = deduplicate_and_categorize(CHINESE_POSITIONS, english_positions)

    # 生成SQL
    print("\n📝 生成扩展SQL脚本...")
    sql_script = generate_sql(merged)

    # 保存SQL
    output_file = '/Users/zhangrui/Claude工作/企业职工认证/positions-database-expanded.sql'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(sql_script)

    print(f"✅ SQL脚本已保存: {output_file}")
    print(f"   文件大小: {len(sql_script) / 1024:.1f} KB")

    # 保存JSON备份
    json_file = '/Users/zhangrui/Claude工作/企业职工认证/positions-all.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump({
            'total': len(merged),
            'positions': merged
        }, f, ensure_ascii=False, indent=2)

    print(f"✅ JSON备份已保存: {json_file}")

    print("\n" + "=" * 70)
    print(f"✨ 岗位库扩展完成！")
    print(f"   原: 71 个岗位")
    print(f"   现: {len(merged):,} 个岗位")
    print(f"   增长: {(len(merged) - 71) / 71 * 100:.1f}%")
    print("=" * 70)

if __name__ == '__main__':
    main()
