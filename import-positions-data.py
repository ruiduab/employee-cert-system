#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
企业职工认证系统 - 岗位和行业分类数据导入脚本
导入 positions-database-init.sql 中的数据到 MySQL 数据库

使用方式：
    python3 import-positions-data.py
    或
    python3 import-positions-data.py --host localhost --user root --password yourpwd --database dbname
"""

import argparse
import sys
import os
from pathlib import Path

try:
    import mysql.connector
    from mysql.connector import Error
except ImportError:
    print("❌ 错误: 未安装 mysql-connector-python")
    print("请运行: pip install mysql-connector-python")
    sys.exit(1)


class PositionsDataImporter:
    def __init__(self, host='localhost', user='root', password='', database='employee_cert'):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None

    def connect(self):
        """连接到 MySQL 数据库"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            self.cursor = self.connection.cursor()
            print(f"✅ 成功连接到数据库: {self.database}")
            return True
        except Error as e:
            print(f"❌ 数据库连接失败: {e}")
            return False

    def load_sql_file(self, sql_file_path):
        """加载 SQL 文件"""
        try:
            with open(sql_file_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            return sql_content
        except FileNotFoundError:
            print(f"❌ 错误: 文件不存在 - {sql_file_path}")
            return None
        except Exception as e:
            print(f"❌ 读取文件失败: {e}")
            return None

    def execute_sql(self, sql_content):
        """执行 SQL 脚本"""
        if not self.connection or not self.cursor:
            print("❌ 错误: 数据库连接未建立")
            return False

        # 分割 SQL 语句（简单处理，按 ; 分割）
        statements = [s.strip() for s in sql_content.split(';') if s.strip()]

        success_count = 0
        error_count = 0

        for i, statement in enumerate(statements, 1):
            # 跳过注释行
            if statement.startswith('--'):
                continue

            try:
                print(f"执行 [{i}/{len(statements)}] ...", end=' ')
                self.cursor.execute(statement)

                # 对于 SELECT 语句，显示结果
                if statement.strip().upper().startswith('SELECT'):
                    results = self.cursor.fetchall()
                    print(f"✅ 查询完成")
                    if results:
                        for row in results:
                            print(f"  {row}")
                else:
                    self.connection.commit()
                    print(f"✅")
                success_count += 1

            except Error as e:
                print(f"⚠️  ({e})")
                error_count += 1
                self.connection.rollback()
                # 继续执行下一条语句
                continue

        print(f"\n📊 执行结果:")
        print(f"  ✅ 成功: {success_count}")
        print(f"  ⚠️  失败/警告: {error_count}")
        return error_count == 0 or error_count <= 2  # 允许少量警告

    def verify_data(self):
        """验证导入的数据"""
        try:
            queries = [
                ("行业分类", "SELECT COUNT(*) FROM industries"),
                ("职位分类", "SELECT COUNT(*) FROM position_categories"),
                ("标准岗位", "SELECT COUNT(*) FROM standard_positions"),
                ("启用的岗位", "SELECT COUNT(*) FROM standard_positions WHERE is_active = TRUE"),
            ]

            print("\n📋 数据验证:")
            for label, query in queries:
                self.cursor.execute(query)
                result = self.cursor.fetchone()
                count = result[0] if result else 0
                print(f"  {label}: {count}")

            # 显示样本数据
            print("\n🎯 样本岗位数据:")
            self.cursor.execute(
                "SELECT name, category_id FROM standard_positions LIMIT 5"
            )
            for row in self.cursor.fetchall():
                print(f"  - {row[0]}")

        except Error as e:
            print(f"❌ 数据验证失败: {e}")

    def close(self):
        """关闭数据库连接"""
        if self.connection and self.connection.is_connected():
            self.cursor.close()
            self.connection.close()
            print("\n✅ 数据库连接已关闭")


def main():
    parser = argparse.ArgumentParser(
        description='企业职工认证系统 - 岗位数据导入工具'
    )
    parser.add_argument(
        '--host',
        default='localhost',
        help='MySQL 主机地址 (默认: localhost)'
    )
    parser.add_argument(
        '--user',
        default='root',
        help='MySQL 用户名 (默认: root)'
    )
    parser.add_argument(
        '--password',
        default='',
        help='MySQL 密码 (默认: 空)'
    )
    parser.add_argument(
        '--database',
        default='employee_cert',
        help='数据库名称 (默认: employee_cert)'
    )
    parser.add_argument(
        '--file',
        default='positions-database-init.sql',
        help='SQL 文件路径 (默认: positions-database-init.sql)'
    )

    args = parser.parse_args()

    # 如果使用相对路径，转换为绝对路径
    sql_file = Path(args.file)
    if not sql_file.is_absolute():
        sql_file = Path(__file__).parent / sql_file

    print("=" * 60)
    print("企业职工认证系统 - 岗位数据导入工具")
    print("=" * 60)
    print(f"\n📝 配置信息:")
    print(f"  主机: {args.host}")
    print(f"  用户: {args.user}")
    print(f"  数据库: {args.database}")
    print(f"  SQL 文件: {sql_file}")

    importer = PositionsDataImporter(
        host=args.host,
        user=args.user,
        password=args.password,
        database=args.database
    )

    # 连接数据库
    if not importer.connect():
        print("\n❌ 导入失败: 无法连接到数据库")
        sys.exit(1)

    # 加载 SQL 文件
    print(f"\n📂 加载 SQL 文件...")
    sql_content = importer.load_sql_file(str(sql_file))
    if not sql_content:
        print("❌ 导入失败: 无法加载 SQL 文件")
        importer.close()
        sys.exit(1)

    # 执行 SQL
    print(f"\n⚙️  执行 SQL 脚本...")
    if not importer.execute_sql(sql_content):
        print("\n⚠️  导入过程中出现错误，但继续完成")

    # 验证数据
    importer.verify_data()

    # 关闭连接
    importer.close()

    print("\n" + "=" * 60)
    print("✅ 岗位数据导入完成！")
    print("=" * 60)


if __name__ == '__main__':
    main()
