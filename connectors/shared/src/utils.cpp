#include "linch_connector/utils.hpp"
#include <chrono>
#include <sstream>
#include <iomanip>
#include <algorithm>
#include <functional>
#include <vector>
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
        item["id"] = cleanString(id);
        item["content"] = cleanString(content);
        item["source_connector"] = cleanString(sourceConnector);
        item["timestamp"] = getCurrentTimestamp();
        
        // 解析并合并元数据
        json metadataJson = json::parse(metadata);
        metadataJson["content_length"] = content.length();
        metadataJson["content_type"] = detectContentType(content);
        
        item["metadata"] = metadataJson;
        
        return safeJsonDump(item);
    } catch (const std::exception& e) {
        // 如果JSON解析失败，创建基础数据项
        json item;
        item["id"] = cleanString(id);
        item["content"] = cleanString(content);
        item["source_connector"] = cleanString(sourceConnector);
        item["timestamp"] = getCurrentTimestamp();
        item["metadata"] = {
            {"content_length", content.length()},
            {"content_type", detectContentType(content)}
        };
        
        return safeJsonDump(item);
    }
}

std::string cleanString(const std::string& input) {
    std::string result;
    result.reserve(input.size());
    
    for (char c : input) {
        unsigned char uc = static_cast<unsigned char>(c);
        // 移除控制字符 (0x00-0x1F 和 0x7F-0x9F)，但保留常见的空白字符
        if (uc >= 32 && uc <= 126) {
            // 可打印ASCII字符
            result += c;
        } else if (c == '\t' || c == '\n' || c == '\r') {
            // 保留常见的空白字符，但替换为空格
            result += ' ';
        } else if (uc >= 160) {
            // 保留扩展ASCII字符（如UTF-8字符）
            result += c;
        }
        // 其他控制字符被移除
    }
    
    return result;
}

bool isValidFilePath(const std::string& path) {
    if (path.empty()) {
        return false;
    }
    
    // 检查是否包含控制字符
    if (hasControlCharacters(path)) {
        return false;
    }
    
    // 检查路径长度
    if (path.length() > 4096) {  // 大多数系统的路径长度限制
        return false;
    }
    
    // 检查危险字符序列
    const std::vector<std::string> dangerousPatterns = {
        "../",    // 路径遍历
        "..\\",   // Windows路径遍历
        "\0",     // NULL字符
        "\x01",   // 开始文本
        "\x02",   // 开始文本
        "\x03",   // 结束文本
        "\x04",   // 传输结束
        "\x05",   // 询问
        "\x06",   // 确认
        "\x07",   // 响铃
    };
    
    for (const auto& pattern : dangerousPatterns) {
        if (path.find(pattern) != std::string::npos) {
            return false;
        }
    }
    
    return true;
}

std::string escapeJsonString(const std::string& input) {
    std::ostringstream result;
    
    for (char c : input) {
        unsigned char uc = static_cast<unsigned char>(c);
        switch (c) {
            case '"':  result << "\\\""; break;
            case '\\': result << "\\\\"; break;
            case '\b': result << "\\b"; break;
            case '\f': result << "\\f"; break;
            case '\n': result << "\\n"; break;
            case '\r': result << "\\r"; break;
            case '\t': result << "\\t"; break;
            default:
                if (uc <= 0x1f) {
                    // 控制字符转义为Unicode
                    result << "\\u" << std::hex << std::setw(4) << std::setfill('0') << static_cast<int>(uc);
                } else {
                    result << c;
                }
                break;
        }
    }
    
    return result.str();
}

std::string safeJsonDump(const nlohmann::json& jsonObj) {
    try {
        // 创建安全的JSON副本，清理所有字符串值
        json safeCopy = jsonObj;
        
        std::function<void(json&)> cleanJsonRecursive = [&](json& j) {
            if (j.is_string()) {
                j = cleanString(j.get<std::string>());
            } else if (j.is_object()) {
                for (auto& [key, value] : j.items()) {
                    cleanJsonRecursive(value);
                }
            } else if (j.is_array()) {
                for (auto& item : j) {
                    cleanJsonRecursive(item);
                }
            }
        };
        
        cleanJsonRecursive(safeCopy);
        
        // 使用安全设置序列化
        return safeCopy.dump(-1, ' ', false, json::error_handler_t::replace);
    } catch (const std::exception& e) {
        // 如果序列化失败，返回错误信息的JSON
        json errorJson = {
            {"error", "JSON serialization failed"},
            {"message", std::string(e.what())},
            {"timestamp", getCurrentTimestamp()}
        };
        return errorJson.dump();
    }
}

bool hasControlCharacters(const std::string& input) {
    for (char c : input) {
        unsigned char uc = static_cast<unsigned char>(c);
        // 检查控制字符 (0x00-0x1F 和 0x7F-0x9F)，排除常见空白字符
        if ((uc <= 31 && c != '\t' && c != '\n' && c != '\r') || 
            (uc >= 127 && uc <= 159)) {
            return true;
        }
    }
    return false;
}

} // namespace utils
} // namespace linch_connector