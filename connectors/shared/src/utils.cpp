#include "linch_connector/utils.hpp"
#include <chrono>
#include <sstream>
#include <iomanip>
#include <algorithm>
#include <nlohmann/json.hpp>

#ifdef _WIN32
#include <objbase.h>
#else
#include <uuid/uuid.h>
#endif

using json = nlohmann::json;

namespace linch_connector {
namespace utils {

std::string generateUUID() {
#ifdef _WIN32
    GUID guid;
    if (SUCCEEDED(CoCreateGuid(&guid))) {
        std::ostringstream oss;
        oss << std::hex << std::setfill('0');
        oss << std::setw(8) << guid.Data1;
        oss << std::setw(4) << guid.Data2;
        oss << std::setw(4) << guid.Data3;
        for (int i = 0; i < 8; ++i) {
            oss << std::setw(2) << static_cast<int>(guid.Data4[i]);
        }
        return oss.str();
    }
    return "00000000000000000000000000000000";
#else
    uuid_t uuid;
    uuid_generate(uuid);
    char uuid_str[37];
    uuid_unparse_lower(uuid, uuid_str);
    
    // 移除连字符
    std::string result = uuid_str;
    result.erase(std::remove(result.begin(), result.end(), '-'), result.end());
    return result;
#endif
}

std::string getCurrentTimestamp() {
    auto now = std::chrono::system_clock::now();
    auto time_t = std::chrono::system_clock::to_time_t(now);
    
    std::ostringstream oss;
    oss << std::put_time(std::gmtime(&time_t), "%Y-%m-%dT%H:%M:%S");
    
    // 添加毫秒
    auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(
        now.time_since_epoch()).count() % 1000;
    oss << "." << std::setfill('0') << std::setw(3) << ms << "Z";
    
    return oss.str();
}

std::string detectContentType(const std::string& content) {
    std::string content_lower = content;
    std::transform(content_lower.begin(), content_lower.end(), content_lower.begin(), ::tolower);
    
    // URL检测
    if (content_lower.find("http://") == 0 || content_lower.find("https://") == 0) {
        return "url";
    }
    
    // 代码检测
    if (content_lower.find("def ") == 0 || content_lower.find("function ") == 0 || 
        content_lower.find("class ") == 0 || content_lower.find("import ") == 0) {
        return "code";
    }
    
    // Markdown检测
    if (content_lower.find("# ") == 0 || content_lower.find("## ") == 0) {
        return "markdown";
    }
    
    // JSON/配置文件检测
    if (content.find("{") != std::string::npos && content.find("}") != std::string::npos) {
        return "json_or_config";
    }
    
    // 邮件/联系人检测
    if (content.find("@") != std::string::npos && content.find(".") != std::string::npos) {
        return "email_or_contact";
    }
    
    // 任务/提醒检测
    if (content_lower.find("todo") != std::string::npos || 
        content_lower.find("task") != std::string::npos ||
        content_lower.find("deadline") != std::string::npos ||
        content_lower.find("fixme") != std::string::npos ||
        content_lower.find("note") != std::string::npos) {
        return "task_or_reminder";
    }
    
    return "text";
}

std::string createDataItem(
    const std::string& id,
    const std::string& content,
    const std::string& sourceConnector,
    const std::string& metadata) {
    
    try {
        json item;
        item["id"] = id;
        item["content"] = content;
        item["source_connector"] = sourceConnector;
        item["timestamp"] = getCurrentTimestamp();
        
        // 解析并合并元数据
        json metadataJson = json::parse(metadata);
        metadataJson["content_length"] = content.length();
        metadataJson["content_type"] = detectContentType(content);
        
        item["metadata"] = metadataJson;
        
        return item.dump();
    } catch (const std::exception& e) {
        // 如果JSON解析失败，创建基础数据项
        json item;
        item["id"] = id;
        item["content"] = content;
        item["source_connector"] = sourceConnector;
        item["timestamp"] = getCurrentTimestamp();
        item["metadata"] = {
            {"content_length", content.length()},
            {"content_type", detectContentType(content)}
        };
        
        return item.dump();
    }
}

} // namespace utils
} // namespace linch_connector