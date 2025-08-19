#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import timedelta

import pymysql
import json  # 导入 json 模块
from decimal import Decimal


class DatabaseManager:
    def __init__(self, host, user, password, db, port=3306, charset="utf8mb4"):
        self.host = host
        self.user = user
        self.password = password
        self.db = db
        self.port = port
        self.charset = charset
        self.connection = None
        self.miscarry_calc_data_table = "miscarry_calc_data"

    def connect(self):
        """建立数据库连接。"""
        try:
            self.connection = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                db=self.db,
                port=self.port,
                charset=self.charset,
                cursorclass=pymysql.cursors.DictCursor,
            )
            # print("数据库连接已建立。")
        except Exception as e:
            print(f"连接数据库失败：{e}")

    def close(self):
        """关闭数据库连接。"""
        if self.connection:
            self.connection.close()
            # print("数据库连接已关闭。")

    def execute_query(self, query, params=None):
        """执行SQL查询或修改操作，并使用with管理游标。"""
        with self.connection.cursor() as cursor:
            cursor.execute(query, params)
            # print("查询执行成功。")

    def execute_batch(self, query, params_list):
        """
        批量执行SQL查询或更新操作。用于在一条语句中执行多组参数。

        :param query: SQL查询语句，通常包含占位符（如 %s）
        :param params_list: 参数列表，列表中的每一项是一个元组，包含一组参数
        """
        with self.connection.cursor() as cursor:
            for params in params_list:
                cursor.execute(query, params)
            # print("批量查询执行成功。")

    def fetch_all(self, query, params=None):
        """执行查询并返回所有结果。"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                results = cursor.fetchall()
                # 自动反序列化 JSON 字段
                for result in results:
                    self._deserialize_json_fields(result)
                return results
        except Exception as e:
            print(f"获取所有结果失败：{e}")
            return []

    def fetch_one(self, query, params=None):
        """执行查询并返回单条结果。"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                result = cursor.fetchone()
                if result:
                    self._deserialize_json_fields(result)
                return result
        except Exception as e:
            print(f"获取单条结果失败：{e}")
            return None

    def commit(self):
        """提交事务。"""
        self.connection.commit()

    def rollback(self):
        """回滚事务。"""
        self.connection.rollback()

    def insert_data(self, table, data):
        """
        插入数据的方法，仅进行插入操作，不更新已有数据。
        :param table: 要操作的表名
        :param data: 数据字典，包含字段和值
        """
        fields = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))

        sql = f"""
        INSERT INTO {table} ({fields})
        VALUES ({placeholders});
        """
        # 序列化字典和列表
        params = [
            json.dumps(value) if isinstance(value, (dict, list)) else value
            for value in data.values()
        ]

        self.execute_query(sql, params)

    def insert_or_update_data(self, table, data):
        """
        插入或更新数据的方法。
        :param table: 要操作的表名
        :param data: 数据字典，包含字段和值
        """
        fields = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        updates = ", ".join([f"{key} = VALUES({key})" for key in data.keys()])

        sql = f"""
        INSERT INTO {table} ({fields})
        VALUES ({placeholders})
        ON DUPLICATE KEY UPDATE
            {updates};
        """
        # 序列化字典和列表
        params = [
            json.dumps(value) if isinstance(value, (dict, list)) else value
            for value in data.values()
        ]

        self.execute_query(sql, params)

    def insert_or_addup_data(self, table, data):
        """
        插入或更新数据的方法，更新时在原记录基础上累加。
        :param table: 要操作的表名
        :param data: 数据字典，包含字段和值
        """
        fields = ", ".join([f"`{key}`" for key in data.keys()])
        placeholders = ", ".join(["%s"] * len(data))

        # Qualify column names to avoid ambiguity
        updates = ", ".join(
            [
                (
                    f"`{key}` = `{key}` + VALUES(`{key}`)"
                    if isinstance(data[key], (int, float, Decimal))
                    else f"`{key}` = VALUES(`{key}`)"
                )
                for key in data.keys()
            ]
        )

        sql = f"""
        INSERT INTO `{table}` ({fields})
        VALUES ({placeholders})
        ON DUPLICATE KEY UPDATE
            {updates};
        """
        # 序列化字典和列表
        params = [
            json.dumps(value) if isinstance(value, (dict, list)) else value
            for value in data.values()
        ]

        self.execute_query(sql, params)

    def create_miscarry_calc_data_table_if_not_exist(self):
        # 新版：存储图片及其元数据。hash 建议使用 SHA-256 十六进制(64字符)；
        # 如果后续要做内容去重与快速查询，可在 hash 上建唯一索引。
        # last_used_at 用于命中/访问时更新，便于做缓存或淘汰策略。
        sql = f"""
        CREATE TABLE IF NOT EXISTS `{self.miscarry_calc_data_table}` (
            `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '自增主键',
            `json` JSON NOT NULL COMMENT '分析结果的JSON数据',
            `gs_mm` INT UNSIGNED NULL COMMENT '孕囊大小 mm',
            `crl_mm` INT UNSIGNED NULL COMMENT '胚芽长 mm',
            `miscarry` TINYINT(1) NULL COMMENT '是否停育 1=是 0=否',
            `exam_date` DATE NULL COMMENT '检查日期 YYYY-MM-DD',
            `hash` CHAR(64) NOT NULL COMMENT '图片内容SHA-256十六进制',
            `ext` VARCHAR(10) NOT NULL COMMENT '文件扩展名(统一存不含点例如 jpg)',
            `mime` VARCHAR(64) NOT NULL COMMENT 'MIME类型，例如 image/jpeg',
            `size` INT UNSIGNED NOT NULL COMMENT '文件字节大小',
            `width` INT UNSIGNED NULL COMMENT '像素宽度',
            `height` INT UNSIGNED NULL COMMENT '像素高度',
            `stored_path` VARCHAR(255) NOT NULL COMMENT '相对或绝对存储路径',
            `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间(UTC或服务器时间)',
            `last_used_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最近使用/访问时间',
            PRIMARY KEY (`id`),
            UNIQUE KEY `uniq_hash` (`hash`),
            KEY `idx_created_at` (`created_at`),
            KEY `idx_last_used_at` (`last_used_at`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='流产计算图片元数据表';
        """
        self.execute_query(sql)

    def get_data_by_hash(self, hash):
        sql = f"SELECT * FROM {self.miscarry_calc_data_table} WHERE hash = %s"
        result = self.fetch_one(sql, (hash,))
        return result

    @staticmethod
    def _deserialize_json_fields(result):
        """辅助方法，反序列化 JSON 字段。"""
        json_fields = ["genes", "qualities", "mysteries", "trait"]
        for field in json_fields:
            if field in result and result[field]:
                result[field] = json.loads(result[field])


if __name__ == "__main__":
    pass
