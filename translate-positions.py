#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
岗位库英文翻译脚本
将73k英文岗位自动翻译成中文

使用 google-trans-new 库（免费，无API密钥）
"""

import json
import time
from pathlib import Path
from collections import defaultdict

# 首先尝试导入翻译库，如果没有则提示安装
try:
    from google_trans_new import google_translator
    TRANSLATOR = google_translator()
except ImportError:
    print("❌ 缺少翻译库，请先安装:")
    print("   pip install google-trans-new")
    exit(1)

def load_positions(json_file):
    """加载岗位JSON文件"""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('positions', [])
    except Exception as e:
        print(f"❌ 加载文件失败: {e}")
        return []

def translate_text(text, retries=3):
    """翻译文本，带重试机制"""
    for attempt in range(retries):
        try:
            result = TRANSLATOR.translate(text, lang_src='en', lang_tgt='zh-CN')
            return result
        except Exception as e:
            if attempt < retries - 1:
                print(f"  ⚠️  翻译失败 (重试 {attempt+1}/{retries-1}): {str(e)[:50]}")
                time.sleep(2)  # 等待后重试
            else:
                print(f"  ❌ 翻译失败 (放弃): {text}")
                return None
    return None

def translate_positions(positions, start_from=0):
    """批量翻译岗位"""
    print(f"\n📝 开始翻译岗位... (共 {len(positions)} 个)")
    print(f"   从第 {start_from + 1} 个开始")
    print(f"   ⏱️  预计耗时: {len(positions) / 10:.0f} 分钟\n")

    translated = []
    failed = []

    for idx, pos in enumerate(positions):
        if idx < start_from:
            continue

        # 每处理10个显示进度
        if (idx - start_from) % 10 == 0:
            progress = ((idx - start_from) / len(positions)) * 100
            print(f"  [{(idx - start_from):6d}/{len(positions)}] {progress:5.1f}% ", end='')
            if 'name_en' in pos and pos['name_en']:
                print(f"正在翻译: {pos['name_en'][:30]}")
            else:
                print()

        # 翻译英文岗位名
        if 'name_en' in pos and pos['name_en'] and 'name_cn' not in pos:
            cn_name = translate_text(pos['name_en'])
            if cn_name:
                pos['name_cn'] = cn_name
            else:
                pos['name_cn'] = pos['name_en']  # 翻译失败则保留英文
                failed.append(pos['name_en'])

        translated.append(pos)

        # 每翻译50个暂停一下，避免请求过快
        if (idx - start_from) % 50 == 0 and idx > start_from:
            time.sleep(1)

    print(f"\n✅ 翻译完成!")
    print(f"   成功: {len([p for p in translated if 'name_cn' in p])} 个")
    print(f"   失败/保留英文: {len(failed)} 个")

    return translated, failed

def generate_bilingual_sql(positions):
    """生成中英文双语SQL脚本"""
    sql_lines = []

    sql_lines.append("""-- ============================================================
-- 中英文双语岗位库 - 扩展版
-- ============================================================

-- 清空现有数据
TRUNCATE TABLE standard_positions;

-- 导入中英文双语岗位
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
    for pos in positions:
        category_id = categories_map.get(pos.get('category', 'Other'), 12)

        # 使用翻译后的中文名称
        cn_name = pos.get('name_cn', pos.get('name', ''))
        en_name = pos.get('name_en', '')

        # 避免SQL注入
        cn_name = cn_name.replace("'", "\\'")
        en_name = en_name.replace("'", "\\'")

        # 生成关键词
        keywords_list = []
        if cn_name:
            keywords_list.append(cn_name)
        if en_name:
            keywords_list.extend(en_name.split()[:2])

        keywords = json.dumps(keywords_list, ensure_ascii=False)

        sql_values.append(
            f"('{cn_name}', '{en_name}', {category_id}, '{keywords}', TRUE)"
        )

    sql_lines.append(',\n'.join(sql_values) + ';')

    # 添加验证查询
    sql_lines.append("""
-- ============================================================
-- 中英文双语岗位库统计
-- ============================================================

SELECT '中英文双语岗位库统计' AS metric;
SELECT COUNT(*) as 总岗位数 FROM standard_positions;
SELECT COUNT(DISTINCT category_id) as 职位分类数 FROM standard_positions;

-- 验证中文翻译效果
SELECT name as 中文岗位, en_name as 英文岗位, category_id
FROM standard_positions
WHERE name != en_name
LIMIT 20;
""")

    return '\n'.join(sql_lines)

def generate_bilingual_json(positions):
    """生成中英文双语JSON"""
    return {
        'total': len(positions),
        'description': '中英文双语岗位库 (73,358个岗位)',
        'update_date': '2026-04-15',
        'positions': positions
    }

def main():
    print("=" * 75)
    print("🌍 英文岗位中文翻译工具")
    print("=" * 75)

    # 检查是否需要安装翻译库
    try:
        import google_trans_new
    except ImportError:
        print("\n❌ 需要安装翻译库:")
        print("   pip install google-trans-new\n")
        print("或使用其他翻译方法:")
        print("   1. 手动翻译\n")
        print("   2. 使用在线翻译API (百度、阿里等)")
        print("   3. 使用本地翻译模型 (LibreTranslate)\n")
        exit(1)

    # 加载岗位数据
    json_file = '/Users/zhangrui/Claude工作/企业职工认证/positions-all.json'
    print(f"\n📂 加载岗位数据: {json_file}")
    positions = load_positions(json_file)

    if not positions:
        print("❌ 无法加载岗位数据")
        exit(1)

    print(f"✅ 已加载 {len(positions)} 个岗位")

    # 统计需要翻译的岗位
    need_translation = [p for p in positions if 'name_cn' not in p]
    already_translated = [p for p in positions if 'name_cn' in p]

    print(f"\n📊 翻译统计:")
    print(f"   已有中文: {len(already_translated)} 个")
    print(f"   需要翻译: {len(need_translation)} 个")

    if not need_translation:
        print("\n✅ 所有岗位都已有中文翻译！")
        return

    # 确认开始翻译
    print(f"\n⚠️  注意:")
    print(f"   - 翻译 {len(need_translation)} 个英文岗位")
    print(f"   - 预计耗时: {len(need_translation) / 10:.0f} 分钟")
    print(f"   - 需要网络连接")
    print(f"   - 某些岗位可能翻译不准确\n")

    response = input("确认开始翻译？(y/n): ").lower()
    if response != 'y':
        print("取消翻译")
        return

    # 开始翻译
    try:
        translated, failed = translate_positions(need_translation)

        # 合并翻译结果
        all_positions = already_translated + translated

        print(f"\n📊 翻译结果:")
        print(f"   总岗位: {len(all_positions)}")
        print(f"   中文岗位: {len([p for p in all_positions if 'name_cn' in p])}")

        if failed:
            print(f"   翻译失败（保留英文）: {len(failed)}")
            print(f"   失败示例: {failed[:5]}")

        # 生成SQL脚本
        print(f"\n📝 生成中英文双语SQL脚本...")
        sql_script = generate_bilingual_sql(all_positions)

        sql_file = '/Users/zhangrui/Claude工作/企业职工认证/positions-database-bilingual.sql'
        with open(sql_file, 'w', encoding='utf-8') as f:
            f.write(sql_script)
        print(f"✅ SQL脚本已保存: {sql_file}")

        # 生成JSON文件
        print(f"\n📝 生成中英文双语JSON...")
        json_data = generate_bilingual_json(all_positions)

        json_file = '/Users/zhangrui/Claude工作/企业职工认证/positions-bilingual.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        print(f"✅ JSON已保存: {json_file}")

        # 显示样本
        print(f"\n📋 翻译样本 (前20个):")
        print(f"{'#':<4} {'中文':<30} {'英文':<40}")
        print("─" * 75)

        for idx, pos in enumerate(all_positions[:20], 1):
            cn = pos.get('name_cn', '')[:28]
            en = pos.get('name_en', '')[:38]
            print(f"{idx:<4} {cn:<30} {en:<40}")

        print(f"\n✨ 翻译完成！")
        print(f"   SQL: {sql_file}")
        print(f"   JSON: {json_file}")

    except Exception as e:
        print(f"\n❌ 翻译过程出错: {e}")
        print(f"   建议: 使用其他翻译方法或工具")

if __name__ == '__main__':
    main()
