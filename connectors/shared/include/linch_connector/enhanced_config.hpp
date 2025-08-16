#pragma once

#include "config_manager.hpp"
#include <nlohmann/json.hpp>
#include <set>
#include <vector>
#include <sstream>
#include <filesystem>
#include <cstdlib>
#include <iostream>

namespace linch_connector {

using json = nlohmann::json;

/**
 * 增强的配置管理器
 * 简化配置解析，支持类型安全的配置访问
 */
class EnhancedConfig {
public:
    EnhancedConfig(ConfigManager& configManager) : m_configManager(configManager) {}

    /**
     * 获取字符串数组配置 (支持JSON数组和逗号分隔)
     */
    std::vector<std::string> getStringArray(const std::string& key, 
                                           const std::vector<std::string>& defaultValue = {}) {
        std::string value = m_configManager.getConfigValue(key, "");
        
        if (value.empty()) {
            return defaultValue;
        }

        std::vector<std::string> result;

        // 尝试解析JSON数组
        if (value.front() == '[' && value.back() == ']') {
            try {
                json jsonArray = json::parse(value);
                if (jsonArray.is_array()) {
                    for (const auto& item : jsonArray) {
                        if (item.is_string()) {
                            result.push_back(item.get<std::string>());
                        }
                    }
                    return result;
                }
            } catch (const std::exception&) {
                // 继续使用逗号分隔解析
            }
        }

        // 逗号分隔解析
        std::stringstream ss(value);
        std::string item;
        while (std::getline(ss, item, ',')) {
            item = trim(item);
            if (!item.empty()) {
                result.push_back(item);
            }
        }

        return result.empty() ? defaultValue : result;
    }

    /**
     * 获取字符串集合配置
     */
    std::set<std::string> getStringSet(const std::string& key, 
                                      const std::set<std::string>& defaultValue = {}) {
        auto vec = getStringArray(key);
        if (vec.empty()) {
            return defaultValue;
        }
        return std::set<std::string>(vec.begin(), vec.end());
    }

    /**
     * 获取整数配置
     */
    int getInt(const std::string& key, int defaultValue = 0) {
        std::string value = m_configManager.getConfigValue(key, std::to_string(defaultValue));
        try {
            return std::stoi(value);
        } catch (const std::exception&) {
            return defaultValue;
        }
    }

    /**
     * 获取布尔配置
     */
    bool getBool(const std::string& key, bool defaultValue = false) {
        std::string value = m_configManager.getConfigValue(key, defaultValue ? "true" : "false");
        return value == "true" || value == "1" || value == "yes" || value == "on";
    }

    /**
     * 获取字符串配置
     */
    std::string getString(const std::string& key, const std::string& defaultValue = "") {
        return m_configManager.getConfigValue(key, defaultValue);
    }

    /**
     * 获取展开的路径列表 (支持 ~ 展开)
     */
    std::vector<std::string> getExpandedPaths(const std::string& key, 
                                             const std::vector<std::string>& defaultValue = {}) {
        auto paths = getStringArray(key, defaultValue);
        std::vector<std::string> expandedPaths;

        for (auto path : paths) {
            path = trim(path);
            
            // 展开 ~ 为用户主目录
            if (path.substr(0, 2) == "~/") {
                const char* homeDir = std::getenv("HOME");
                if (!homeDir) homeDir = std::getenv("USERPROFILE"); // Windows
                if (homeDir) {
                    path = std::string(homeDir) + path.substr(1);
                }
            }

            // 验证路径是否存在
            if (!path.empty() && std::filesystem::exists(path) && std::filesystem::is_directory(path)) {
                expandedPaths.push_back(path);
            }
        }

        return expandedPaths;
    }

    /**
     * 简化的文件系统监控配置
     * 🔧 配置简化：减少复杂配置选项，提供合理默认值
     */
    struct FileSystemConfig {
        std::vector<std::string> watchDirectories;
        std::set<std::string> includeExtensions;
        std::set<std::string> excludePatterns;
        int maxFileSize;          // MB
        int batchInterval;        // ms
        bool enableContentIndexing;
        bool recursive;
        
        // 简化的索引配置 - 移除过度配置
        bool enableFastIndexing;

        void print() const {
            std::cout << "📋 简化配置:" << std::endl;
            std::cout << "   监控目录: " << watchDirectories.size() << std::endl;
            std::cout << "   包含扩展名: " << includeExtensions.size() << std::endl;
            std::cout << "   排除模式: " << excludePatterns.size() << std::endl;
            std::cout << "   最大文件大小: " << maxFileSize << "MB" << std::endl;
            std::cout << "   批处理间隔: " << batchInterval << "ms" << std::endl;
            std::cout << "   启用索引: " << (enableFastIndexing ? "是" : "否") << std::endl;
        }
    };

    FileSystemConfig getFileSystemConfig() {
        FileSystemConfig config;
        
        // 🔧 简化配置：使用合理默认值，减少配置复杂度
        config.watchDirectories = getExpandedPaths("watch_directories", {});
        config.includeExtensions = getStringSet("include_extensions", 
            {".txt", ".md", ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx"});
        config.excludePatterns = getStringSet("exclude_patterns",
            {"^\\..*", ".*\\.tmp$", ".*\\.log$", "__pycache__", "node_modules",
             ".*\\.cache$", ".*~$", ".*\\.swp$", ".*\\.DS_Store$"});
        config.maxFileSize = getInt("max_file_size", 50);
        config.batchInterval = getInt("batch_interval", 1000);  // 默认1秒批处理
        config.enableContentIndexing = getBool("enable_content_indexing", true);
        config.recursive = getBool("recursive", true);  // 简化为布尔值
        
        // 简化索引配置
        config.enableFastIndexing = getBool("enable_fast_indexing", true);
        
        return config;
    }

    /**
     * 创建剪贴板监控配置
     */
    struct ClipboardConfig {
        int pollInterval;
        int maxContentLength;
        bool enableContentFilter;
        std::set<std::string> excludePatterns;
        bool enableHistory;
        int historySize;

        void print() const {
            std::cout << "📋 剪贴板配置:" << std::endl;
            std::cout << "   轮询间隔: " << pollInterval << "ms" << std::endl;
            std::cout << "   最大内容长度: " << maxContentLength << std::endl;
            std::cout << "   启用内容过滤: " << (enableContentFilter ? "是" : "否") << std::endl;
            std::cout << "   启用历史记录: " << (enableHistory ? "是" : "否") << std::endl;
        }
    };

    ClipboardConfig getClipboardConfig() {
        ClipboardConfig config;
        
        config.pollInterval = getInt("poll_interval", 1000);
        config.maxContentLength = getInt("max_content_length", 10000);
        config.enableContentFilter = getBool("enable_content_filter", true);
        config.excludePatterns = getStringSet("exclude_patterns", {"password", "secret", "token"});
        config.enableHistory = getBool("enable_history", false);
        config.historySize = getInt("history_size", 100);
        
        return config;
    }

private:
    ConfigManager& m_configManager;

    static std::string trim(const std::string& str) {
        size_t start = str.find_first_not_of(" \t\r\n");
        if (start == std::string::npos) return "";
        size_t end = str.find_last_not_of(" \t\r\n");
        return str.substr(start, end - start + 1);
    }
};

} // namespace linch_connector