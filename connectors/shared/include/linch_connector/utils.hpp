#pragma once

#include <string>
#include <nlohmann/json.hpp>

namespace linch_connector {
    using json = nlohmann::json;

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

/**
 * 清理字符串中的控制字符和非打印字符
 * @param input 输入字符串
 * @return 清理后的字符串
 */
std::string cleanString(const std::string& input);

/**
 * 验证文件路径是否安全和有效
 * @param path 文件路径
 * @return 是否为有效路径
 */
bool isValidFilePath(const std::string& path);

/**
 * 转义JSON字符串中的特殊字符
 * @param input 输入字符串
 * @return 转义后的字符串
 */
std::string escapeJsonString(const std::string& input);

/**
 * 安全的JSON序列化，处理控制字符和特殊字符
 * @param jsonObj JSON对象
 * @return 安全序列化的JSON字符串
 */
std::string safeJsonDump(const nlohmann::json& jsonObj);

/**
 * 检查字符串是否包含控制字符
 * @param input 输入字符串
 * @return 是否包含控制字符
 */
bool hasControlCharacters(const std::string& input);

} // namespace utils

} // namespace linch_connector