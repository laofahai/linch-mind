#pragma once

#include <string>

namespace linch_connector {

/**
 * 通用工具函数
 */
namespace utils {

/**
 * 生成UUID字符串
 * @return UUID字符串（小写，无连字符）
 */
std::string generateUUID();

/**
 * 获取当前时间戳（ISO格式）
 * @return ISO格式时间戳字符串
 */
std::string getCurrentTimestamp();

/**
 * 检测内容类型
 * @param content 内容字符串
 * @return 内容类型字符串
 */
std::string detectContentType(const std::string& content);

/**
 * 创建数据项JSON字符串
 * @param id 数据项ID
 * @param content 内容
 * @param sourceConnector 源连接器名称
 * @param metadata 元数据JSON对象（可选）
 * @return JSON字符串
 */
std::string createDataItem(
    const std::string& id,
    const std::string& content,
    const std::string& sourceConnector,
    const std::string& metadata = "{}"
);

} // namespace utils

} // namespace linch_connector