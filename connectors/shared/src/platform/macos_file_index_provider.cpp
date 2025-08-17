#ifdef __APPLE__

#include "linch_connector/platform/macos_file_index_provider.hpp"
#include <iostream>
#include <sstream>
#include <filesystem>
#include <cstdio>
#include <memory>
#include <regex>
#include <sys/stat.h>

namespace linch_connector {

MacOSFileIndexProvider::MacOSFileIndexProvider() {
    std::cout << "🍎 初始化 macOS 文件索引提供者" << std::endl;
    m_spotlightAvailable = checkSpotlightAvailability();
}

MacOSFileIndexProvider::~MacOSFileIndexProvider() {
    std::cout << "🍎 销毁 macOS 文件索引提供者" << std::endl;
}

std::vector<FileRecord> MacOSFileIndexProvider::queryAllFiles(size_t maxResults) {
    std::cout << "🔍 查询所有文件 (限制: " << (maxResults ? std::to_string(maxResults) : "无限制") << ")" << std::endl;
    
    if (!isIndexServiceAvailable()) {
        std::cout << "❌ Spotlight 索引服务不可用" << std::endl;
        return {};
    }
    
    return executeSpotlightQuery(SPOTLIGHT_QUERY_ALL_FILES, maxResults);
}

std::vector<FileRecord> MacOSFileIndexProvider::queryByExtensions(
    const std::vector<std::string>& extensions,
    size_t maxResults) {
    
    std::cout << "🔍 按扩展名查询文件: ";
    for (const auto& ext : extensions) {
        std::cout << ext << " ";
    }
    std::cout << std::endl;
    
    if (!isIndexServiceAvailable()) {
        std::cout << "❌ Spotlight 索引服务不可用" << std::endl;
        return {};
    }
    
    std::string query = buildExtensionsQuery(extensions);
    return executeSpotlightQuery(query, maxResults);
}

std::vector<FileRecord> MacOSFileIndexProvider::queryByPattern(
    const std::string& pattern,
    size_t maxResults) {
    
    std::cout << "🔍 按模式查询文件: " << pattern << std::endl;
    
    if (!isIndexServiceAvailable()) {
        std::cout << "❌ Spotlight 索引服务不可用" << std::endl;
        return {};
    }
    
    std::string query = buildPatternQuery(pattern);
    return executeSpotlightQuery(query, maxResults);
}

std::vector<FileRecord> MacOSFileIndexProvider::queryByDirectory(
    const std::string& directory,
    bool recursive,
    size_t maxResults) {
    
    std::cout << "🔍 按目录查询文件: " << directory 
              << " (递归: " << (recursive ? "是" : "否") << ")" << std::endl;
    
    if (!isIndexServiceAvailable()) {
        std::cout << "❌ Spotlight 索引服务不可用" << std::endl;
        return {};
    }
    
    std::string query = buildDirectoryQuery(directory, recursive);
    return executeSpotlightQuery(query, maxResults);
}

bool MacOSFileIndexProvider::isIndexServiceAvailable() {
    return m_spotlightAvailable.load();
}

nlohmann::json MacOSFileIndexProvider::getIndexStatistics() {
    std::lock_guard<std::mutex> lock(m_statsMutex);
    
    nlohmann::json stats;
    stats["platform"] = "macOS";
    stats["service"] = "Spotlight";
    stats["available"] = m_spotlightAvailable.load();
    stats["status"] = getSpotlightStatus();
    
    // 尝试获取索引文件数量（简单估算）
    try {
        auto result = executeSpotlightQuery("kMDItemKind != 'Folder'", 1);
        stats["has_files"] = !result.empty();
    } catch (...) {
        stats["has_files"] = false;
    }
    
    return stats;
}

bool MacOSFileIndexProvider::refreshIndex() {
    std::cout << "🔄 尝试刷新 Spotlight 索引..." << std::endl;
    
    // Spotlight 索引由系统自动维护，无法手动强制刷新
    // 但可以重新检查可用性
    m_spotlightAvailable = checkSpotlightAvailability();
    
    std::cout << "✅ Spotlight 索引状态已更新: " 
              << (m_spotlightAvailable ? "可用" : "不可用") << std::endl;
    
    return m_spotlightAvailable;
}

// 私有方法实现

std::vector<FileRecord> MacOSFileIndexProvider::executeSpotlightQuery(
    const std::string& query, 
    size_t maxResults) {
    
    std::vector<FileRecord> results;
    
    // 构建 mdfind 命令
    std::ostringstream cmd;
    cmd << "mdfind ";
    
    // 添加结果限制
    if (maxResults > 0) {
        cmd << "-c " << maxResults << " ";
    }
    
    // 添加查询条件
    cmd << "'" << query << "'";
    
    std::cout << "🔍 执行查询: " << cmd.str() << std::endl;
    
    try {
        std::string output = executeCommand(cmd.str());
        
        if (output.empty()) {
            std::cout << "ℹ️ 查询无结果" << std::endl;
            return results;
        }
        
        // 解析输出
        std::istringstream stream(output);
        std::string line;
        
        while (std::getline(stream, line) && 
               (maxResults == 0 || results.size() < maxResults)) {
            
            if (!line.empty() && isValidPath(line)) {
                FileRecord record = createFileRecordFromPath(line);
                if (!record.path.empty()) {
                    results.push_back(std::move(record));
                }
            }
        }
        
        std::cout << "✅ 查询完成，找到 " << results.size() << " 个文件" << std::endl;
        
    } catch (const std::exception& e) {
        std::cout << "❌ 查询执行失败: " << e.what() << std::endl;
    }
    
    return results;
}

FileRecord MacOSFileIndexProvider::createFileRecordFromPath(const std::string& path) {
    FileRecord record;
    
    try {
        // 获取文件信息
        struct stat statBuf;
        if (stat(path.c_str(), &statBuf) != 0) {
            return record; // 文件不存在或无法访问
        }
        
        record.path = path;
        record.size = static_cast<uint64_t>(statBuf.st_size);
        record.modified_time = static_cast<uint64_t>(statBuf.st_mtime);
        record.is_directory = S_ISDIR(statBuf.st_mode);
        
        // 提取文件名
        auto pos = path.find_last_of('/');
        if (pos != std::string::npos) {
            record.name = path.substr(pos + 1);
            record.directory = path.substr(0, pos);
        } else {
            record.name = path;
        }
        
        // 提取扩展名
        auto dotPos = record.name.find_last_of('.');
        if (dotPos != std::string::npos && dotPos > 0) {
            record.extension = record.name.substr(dotPos);
        }
        
    } catch (const std::exception& e) {
        std::cout << "⚠️ 解析文件路径失败: " << path << " - " << e.what() << std::endl;
        return FileRecord{}; // 返回空记录
    }
    
    return record;
}

std::string MacOSFileIndexProvider::executeCommand(const std::string& command) const {
    std::string result;
    
    std::unique_ptr<FILE, decltype(&pclose)> pipe(
        popen(command.c_str(), "r"), pclose);
    
    if (!pipe) {
        throw std::runtime_error("执行命令失败: " + command);
    }
    
    char buffer[128];
    while (fgets(buffer, sizeof(buffer), pipe.get()) != nullptr) {
        result += buffer;
    }
    
    return result;
}

bool MacOSFileIndexProvider::checkSpotlightAvailability() const {
    try {
        // 尝试执行简单的 mdfind 查询
        std::string output = executeCommand("mdfind -c 1 'kMDItemKind != \"\"' 2>/dev/null");
        return !output.empty();
    } catch (...) {
        return false;
    }
}

std::string MacOSFileIndexProvider::getSpotlightStatus() const {
    try {
        // 获取 Spotlight 状态
        std::string output = executeCommand("mdutil -s / 2>/dev/null");
        if (output.find("Indexing enabled") != std::string::npos) {
            return "indexing_enabled";
        } else if (output.find("Indexing disabled") != std::string::npos) {
            return "indexing_disabled";
        } else {
            return "unknown";
        }
    } catch (...) {
        return "error";
    }
}

std::string MacOSFileIndexProvider::buildExtensionsQuery(const std::vector<std::string>& extensions) {
    if (extensions.empty()) {
        return SPOTLIGHT_QUERY_ALL_FILES;
    }
    
    std::ostringstream query;
    query << "(";
    
    for (size_t i = 0; i < extensions.size(); ++i) {
        if (i > 0) {
            query << " OR ";
        }
        
        std::string ext = extensions[i];
        // 确保扩展名以点开头
        if (!ext.empty() && ext[0] != '.') {
            ext = "." + ext;
        }
        
        query << "kMDItemFSName LIKE \"*" << escapeForSpotlight(ext) << "\"";
    }
    
    query << ") AND kMDItemKind != 'Folder'";
    return query.str();
}

std::string MacOSFileIndexProvider::buildPatternQuery(const std::string& pattern) {
    std::string sanitized = sanitizePattern(pattern);
    std::ostringstream query;
    query << "kMDItemFSName LIKE \"" << escapeForSpotlight(sanitized) << "\" AND kMDItemKind != 'Folder'";
    return query.str();
}

std::string MacOSFileIndexProvider::buildDirectoryQuery(const std::string& directory, bool recursive) {
    std::ostringstream query;
    
    if (recursive) {
        query << "kMDItemFSName != \"\" AND kMDItemPath LIKE \"" 
              << escapeForSpotlight(directory) << "*\" AND kMDItemKind != 'Folder'";
    } else {
        query << "kMDItemFSName != \"\" AND kMDItemPath LIKE \"" 
              << escapeForSpotlight(directory) << "/*\" AND kMDItemPath != LIKE \"" 
              << escapeForSpotlight(directory) << "/*/*\" AND kMDItemKind != 'Folder'";
    }
    
    return query.str();
}

std::string MacOSFileIndexProvider::sanitizePattern(const std::string& pattern) {
    std::string result = pattern;
    
    // 如果模式不包含通配符，添加通配符以实现部分匹配
    if (result.find('*') == std::string::npos && result.find('?') == std::string::npos) {
        result = "*" + result + "*";
    }
    
    return result;
}

std::string MacOSFileIndexProvider::escapeForSpotlight(const std::string& text) {
    std::string escaped = text;
    
    // 替换可能导致查询问题的字符
    std::regex specialChars(R"(["])");
    escaped = std::regex_replace(escaped, specialChars, "\\$&");
    
    return escaped;
}

bool MacOSFileIndexProvider::isValidPath(const std::string& path) const {
    return !path.empty() && path[0] == '/' && path.find('\0') == std::string::npos;
}

} // namespace linch_connector

#endif // __APPLE__