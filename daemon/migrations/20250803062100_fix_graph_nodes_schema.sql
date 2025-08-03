-- Migration: 修复graph_nodes表字段名
-- Created: 2025-08-03T06:21:00
-- Version: 20250803062100

-- 重命名 type 字段为 node_type 以匹配数据模型
ALTER TABLE graph_nodes RENAME COLUMN type TO node_type;