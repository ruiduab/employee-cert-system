#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能岗位翻译脚本
使用离线词典和规则翻译 + 网络翻译补充
更高效、更快速

策略：
1. 使用内置翻译词典（常见岗位关键词）
2. 组合翻译英文短语
3. 网络翻译作为补充（仅限词典无法覆盖的）
"""

import json
import re
import time
from pathlib import Path
from collections import defaultdict

# 岗位关键词中英文翻译词典
POSITION_DICTIONARY = {
    # 职位级别
    'senior': '高级', 'junior': '初级', 'chief': '首席', 'principal': '主要',
    'head': '负责人', 'lead': '主管', 'manager': '经理', 'director': '总监',
    'vice': '副', 'assistant': '助理', 'associate': '关联', 'specialist': '专家',
    'coordinator': '协调员', 'supervisor': '主管', 'officer': '官员',

    # 技术岗位
    'developer': '开发者', 'engineer': '工程师', 'programmer': '程序员',
    'coder': '编码员', 'architect': '架构师', 'designer': '设计师',
    'devops': 'DevOps', 'frontend': '前端', 'backend': '后端', 'full stack': '全栈',
    'software': '软件', 'web': '网站', 'mobile': '移动', 'cloud': '云计算',
    'data': '数据', 'machine learning': '机器学习', 'ai': '人工智能',
    'network': '网络', 'database': '数据库', 'system': '系统',

    # 设计相关
    'designer': '设计师', 'ui': 'UI', 'ux': 'UX', 'graphic': '平面',
    'visual': '视觉', 'interaction': '交互', 'industrial': '工业',
    'product': '产品', '3d': '三维', 'animation': '动画',

    # 销售市场
    'sales': '销售', 'account': '客户', 'executive': '经理', 'representative': '代表',
    'marketing': '市场', 'brand': '品牌', 'content': '内容', 'social': '社交',
    'advertising': '广告', 'promotion': '推广',

    # 人事行政
    'human resources': '人力资源', 'hr': '人力资源', 'recruitment': '招聘',
    'recruiter': '招聘', 'administrative': '行政', 'office': '办公',
    'secretary': '秘书', 'reception': '前台', 'coordination': '协调',

    # 财务法律
    'accountant': '会计', 'accounting': '会计', 'finance': '财务',
    'financial': '财务', 'auditor': '审计', 'tax': '税务', 'controller': '财务主管',
    'lawyer': '律师', 'legal': '法律', 'compliance': '合规',

    # 运营项目
    'project': '项目', 'operations': '运营', 'operation': '运营',
    'logistics': '物流', 'supply chain': '供应链', 'quality': '质量',
    'manufacturing': '制造', 'production': '生产',

    # 教育医疗
    'teacher': '教师', 'professor': '教授', 'instructor': '讲师',
    'doctor': '医生', 'nurse': '护士', 'physician': '医生',
    'therapist': '治疗师', 'counselor': '咨询师',

    # 其他常见词
    'manager': '经理', 'employee': '员工', 'staff': '员工', 'analyst': '分析师',
    'consultant': '顾问', 'intern': '实习生', 'apprentice': '学徒',
    'executive': '高管', 'ceo': '首席执行官', 'cto': '首席技术官',
    'cfo': '首席财务官', 'president': '总裁', 'chairman': '董事长',
    'administrator': '管理员', 'technician': '技术员',
}

def load_positions(json_file):
    """加载岗位JSON文件"""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('positions', [])
    except Exception as e:
        print(f"❌ 加载文件失败: {e}")
        return []

def translate_with_dictionary(position_en):
    """使用词典翻译英文岗位"""
    if not position_en:
        return None

    pos_lower = position_en.lower()

    # 完全匹配
    if pos_lower in POSITION_DICTIONARY:
        return POSITION_DICTIONARY[pos_lower]

    # 分词翻译（从长到短，避免部分匹配问题）
    words = sorted(POSITION_DICTIONARY.keys(), key=len, reverse=True)
    translated_parts = []

    temp_pos = pos_lower
    for word in words:
        if word in temp_pos:
            translation = POSITION_DICTIONARY[word]
            temp_pos = temp_pos.replace(word, f'[{translation}]', 1)

    # 如果有完整翻译
    if '[' in temp_pos:
        result = temp_pos.replace('[', '').replace(']', '')
        if result.strip() and result != pos_lower:
            return result.strip().title()

    return None

def smart_translate(position_en):
    """智能翻译 - 字典优先，不足时网络翻译"""
    # 首先尝试字典翻译
    dict_result = translate_with_dictionary(position_en)
    if dict_result:
        return dict_result

    # 字典无法翻译时才用网络翻译
    try:
        from google_trans_new import google_translator
        translator = google_translator()
        result = translator.translate(position_en, lang_src='en', lang_tgt='zh-CN')
        return result
    except:
        # 网络翻译失败，保留英文
        return position_en

def batch_translate_positions(positions, use_network=False):
    """批量翻译岗位"""
    print(f"\n📝 开始翻译 {len(positions)} 个岗位...")
    print(f"   模式: {'字典+网络' if use_network else '仅离线字典'}\n")

    translated = []
    dict_success = 0
    network_success = 0
    failed = []

    for idx, pos in enumerate(positions):
        if (idx % 50) == 0:
            progress = (idx / len(positions)) * 100
            print(f"  [{idx:6d}/{len(positions)}] {progress:5.1f}%")

        # 跳过已有中文的
        if 'name_cn' in pos:
            translated.append(pos)
            dict_success += 1
            continue

        en_name = pos.get('name_en', '')
        if not en_name:
            translated.append(pos)
            continue

        # 字典翻译
        cn_name = translate_with_dictionary(en_name)

        if cn_name:
            pos['name_cn'] = cn_name
            dict_success += 1
        elif use_network:
            # 字典失败，尝试网络翻译
            try:
                from google_trans_new import google_translator
                translator = google_translator()
                cn_name = translator.translate(en_name, lang_src='en', lang_tgt='zh-CN')
                pos['name_cn'] = cn_name
                network_success += 1
            except:
                pos['name_cn'] = en_name  # 保留英文
                failed.append(en_name)
        else:
            pos['name_cn'] = en_name  # 保留英文
            failed.append(en_name)

        translated.append(pos)

        # 网络翻译时每50个暂停
        if use_network and network_success > 0 and (network_success % 50) == 0:
            time.sleep(2)

    print(f"\n✅ 翻译完成!")
    print(f"   字典翻译成功: {dict_success}")
    print(f"   网络翻译成功: {network_success}")
    print(f"   翻译失败（保留英文）: {len(failed)}")
    print(f"   总成功率: {((dict_success + network_success) / len(positions) * 100):.1f}%")

    return translated, failed

def generate_sql_with_bilingual(positions):
    """生成中英文SQL脚本"""
    sql_lines = []

    sql_lines.append("""-- ============================================================
-- 中英文双语岗位库 v2.0
-- 包含73,358个岗位，每个岗位都有中文和英文名称
-- ============================================================

TRUNCATE TABLE standard_positions;

INSERT INTO standard_positions (name, en_name, category_id, keywords, is_active) VALUES
""")

    categories_map = {
        'Technology': 1, 'Data': 2, 'Product': 3, 'Design': 4,
        'Sales': 5, 'Marketing': 6, 'HR': 7, 'Finance': 8,
        'Legal': 9, 'Operations': 10, 'Manufacturing': 11, 'Other': 12
    }

    sql_values = []
    for pos in positions:
        category_id = categories_map.get(pos.get('category', 'Other'), 12)

        cn_name = pos.get('name_cn', pos.get('name', ''))
        en_name = pos.get('name_en', '')

        # SQL转义
        cn_name = cn_name.replace("'", "\\'").replace('"', '\\"')
        en_name = en_name.replace("'", "\\'").replace('"', '\\"')

        keywords = json.dumps([cn_name] + en_name.split()[:2], ensure_ascii=False)

        sql_values.append(
            f"('{cn_name}', '{en_name}', {category_id}, '{keywords}', TRUE)"
        )

    sql_lines.append(',\n'.join(sql_values) + ';')

    sql_lines.append("""
-- 验证统计
SELECT '中英文双语岗位库统计' AS metric;
SELECT COUNT(*) as 总岗位数 FROM standard_positions;
SELECT COUNT(DISTINCT category_id) as 职位分类数 FROM standard_positions;

-- 显示样本（中英文对照）
SELECT name as 中文, en_name as 英文, category_id
FROM standard_positions
WHERE name LIKE '%%'
LIMIT 30;
""")

    return '\n'.join(sql_lines)

def show_samples(positions, count=30):
    """显示翻译样本"""
    print(f"\n📋 翻译样本 (前 {count} 个):")
    print(f"{'#':<4} {'中文':<35} {'英文':<45}")
    print("─" * 85)

    for idx, pos in enumerate(positions[:count], 1):
        cn = pos.get('name_cn', '')[:33]
        en = pos.get('name_en', '')[:43]
        print(f"{idx:<4} {cn:<35} {en:<45}")

def main():
    print("=" * 85)
    print("🌍 智能岗位翻译工具 - 中英文双语数据库")
    print("=" * 85)

    # 加载数据
    json_file = '/Users/zhangrui/Claude工作/企业职工认证/positions-all.json'
    print(f"\n📂 加载岗位: {json_file}")
    positions = load_positions(json_file)

    if not positions:
        print("❌ 无法加载数据")
        exit(1)

    print(f"✅ 已加载 {len(positions)} 个岗位\n")

    # 统计
    need_translation = [p for p in positions if 'name_cn' not in p]
    already_cn = [p for p in positions if 'name_cn' in p]

    print(f"📊 翻译进度:")
    print(f"   已有中文: {len(already_cn)} 个")
    print(f"   需翻译: {len(need_translation)} 个")

    # 选择翻译模式
    print(f"\n🎯 翻译方案:")
    print(f"   1. 仅使用离线字典 (快速，覆盖常见岗位) ✅")
    print(f"   2. 字典+网络翻译 (准确但较慢)\n")

    choice = input("选择方案 (1/2, 默认1): ").strip() or '1'
    use_network = choice == '2'

    if use_network:
        print(f"\n⚠️  网络翻译说明:")
        print(f"   - 将使用Google Translate")
        print(f"   - 预计耗时: {len(need_translation) / 100:.0f} 分钟")
        print(f"   - 需要网络连接")

        confirm = input(f"\n继续? (y/n, 默认n): ").strip().lower()
        if confirm != 'y':
            use_network = False
            print("使用仅离线字典模式")

    # 执行翻译
    print(f"\n{'='*85}")
    translated, failed = batch_translate_positions(positions, use_network=use_network)

    # 统计翻译结果
    fully_translated = [p for p in translated if 'name_cn' in p and p['name_cn'] != p.get('name_en', '')]
    print(f"\n📊 翻译结果统计:")
    print(f"   完全翻译: {len(fully_translated)} 个")
    print(f"   保留英文: {len(failed)} 个")
    print(f"   总覆盖率: {(len(fully_translated) / len(translated) * 100):.1f}%")

    # 生成SQL
    print(f"\n📝 生成中英文SQL脚本...")
    sql_script = generate_sql_with_bilingual(translated)

    sql_file = '/Users/zhangrui/Claude工作/企业职工认证/positions-database-bilingual.sql'
    with open(sql_file, 'w', encoding='utf-8') as f:
        f.write(sql_script)
    print(f"✅ SQL已保存: {sql_file}")
    print(f"   大小: {len(sql_script) / 1024 / 1024:.1f} MB")

    # 保存JSON
    print(f"\n📝 生成中英文JSON...")
    json_output = {
        'total': len(translated),
        'translated': len(fully_translated),
        'description': '中英文双语岗位库',
        'positions': translated
    }

    json_file = '/Users/zhangrui/Claude工作/企业职工认证/positions-bilingual.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(json_output, f, ensure_ascii=False, indent=2)
    print(f"✅ JSON已保存: {json_file}")
    print(f"   大小: {len(json.dumps(json_output)) / 1024 / 1024:.1f} MB")

    # 显示样本
    show_samples(translated)

    # 保存失败列表
    if failed:
        print(f"\n⚠️  无法翻译的岗位 ({len(failed)} 个):")
        print("   (这些岗位保留了英文，可稍后手动翻译)")
        for job in failed[:10]:
            print(f"   - {job}")
        if len(failed) > 10:
            print(f"   ... 还有 {len(failed) - 10} 个")

    print(f"\n{'='*85}")
    print(f"✨ 翻译完成！")
    print(f"   SQL: {sql_file}")
    print(f"   JSON: {json_file}")
    print(f"{'='*85}\n")

if __name__ == '__main__':
    main()
