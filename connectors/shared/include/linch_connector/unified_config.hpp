#pragma once

#include <nlohmann/json.hpp>
#include <string>
#include <vector>
#include <set>
#include <chrono>
#include <memory>
#include <type_traits>

namespace linch_connector {
namespace config {

using json = nlohmann::json;

/**
 * 统一连接器配置基类
 * 所有连接器都应继承此类来实现类型安全的配置
 */
class IConnectorConfig {
public:
    virtual ~IConnectorConfig() = default;
    
    /**
     * 从JSON配置加载
     */
    virtual void loadFromJson(const json& config) = 0;
    
    /**
     * 转换为JSON配置
     */
    virtual json toJson() const = 0;
    
    /**
     * 验证配置有效性
     */
    virtual bool validate(std::string& errorMessage) const = 0;
    
    /**
     * 获取配置描述信息
     */
    virtual std::string getDescription() const = 0;
};

/**
 * 配置验证器模板
 */
template<typename T>
class ConfigValidator {
public:
    static bool validateRange(const T& value, const T& min, const T& max) {
        return value >= min && value <= max;
    }
    
    static bool validateNonEmpty(const std::string& value) {
        return !value.empty();
    }
    
    static bool validatePath(const std::string& path) {
        return !path.empty() && path.find_first_of("<>:\"|?*") == std::string::npos;
    }
};

/**
 * 文件系统连接器配置 - 统一版本
 */
class FilesystemConfig : public IConnectorConfig {
public:
    struct PathConfig {
        std::string path;
        bool recursive = true;
        int maxDepth = -1;  // -1表示无限制
        std::set<std::string> includeExtensions;
        std::set<std::string> excludePatterns;
        
        // 性能优化配置
        size_t maxFileSize = 50 * 1024 * 1024;  // 50MB
        bool watchDirectories = true;
        bool watchFiles = true;
        
        json toJson() const {
            return json{
                {"path", path},
                {"recursive", recursive},
                {"max_depth", maxDepth},
                {"include_extensions", includeExtensions},
                {"exclude_patterns", excludePatterns},
                {"max_file_size", maxFileSize},
                {"watch_directories", watchDirectories},
                {"watch_files", watchFiles}
            };
        }
        
        void fromJson(const json& j) {
            path = j.value("path", "");
            recursive = j.value("recursive", true);
            maxDepth = j.value("max_depth", -1);
            
            if (j.contains("include_extensions") && j["include_extensions"].is_array()) {
                for (const auto& ext : j["include_extensions"]) {
                    if (ext.is_string()) {
                        includeExtensions.insert(ext.get<std::string>());
                    }
                }
            }
            
            if (j.contains("exclude_patterns") && j["exclude_patterns"].is_array()) {
                for (const auto& pattern : j["exclude_patterns"]) {
                    if (pattern.is_string()) {
                        excludePatterns.insert(pattern.get<std::string>());
                    }
                }
            }
            
            maxFileSize = j.value("max_file_size", 50 * 1024 * 1024);
            watchDirectories = j.value("watch_directories", true);
            watchFiles = j.value("watch_files", true);
        }
    };
    
    // 监控路径配置
    std::vector<PathConfig> paths;
    
    // 批处理配置
    std::chrono::milliseconds batchInterval{300};
    std::chrono::milliseconds debounceTime{500};
    size_t maxBatchSize{50};
    
    // 默认排除目录
    std::set<std::string> globalExcludeDirectories = {
        ".git", ".svn", ".hg", ".bzr",
        "node_modules", "__pycache__", ".pytest_cache",
        "build", "dist", "target", "out",
        ".idea", ".vscode", ".vs", ".DS_Store"
    };
    
    void loadFromJson(const json& config) override {
        paths.clear();
        
        if (config.contains("paths") && config["paths"].is_array()) {
            for (const auto& pathJson : config["paths"]) {
                PathConfig pathConfig;
                pathConfig.fromJson(pathJson);
                paths.push_back(pathConfig);
            }
        }
        
        batchInterval = std::chrono::milliseconds(config.value("batch_interval", 300));
        debounceTime = std::chrono::milliseconds(config.value("debounce_time", 500));
        maxBatchSize = config.value("max_batch_size", 50);
        
        if (config.contains("global_exclude_directories") && config["global_exclude_directories"].is_array()) {
            globalExcludeDirectories.clear();
            for (const auto& dir : config["global_exclude_directories"]) {
                if (dir.is_string()) {
                    globalExcludeDirectories.insert(dir.get<std::string>());
                }
            }
        }
    }
    
    json toJson() const override {
        json pathsJson = json::array();
        for (const auto& path : paths) {
            pathsJson.push_back(path.toJson());
        }
        
        return json{
            {"type", "filesystem"},
            {"paths", pathsJson},
            {"batch_interval", batchInterval.count()},
            {"debounce_time", debounceTime.count()},
            {"max_batch_size", maxBatchSize},
            {"global_exclude_directories", globalExcludeDirectories}
        };
    }
    
    bool validate(std::string& errorMessage) const override {
        if (paths.empty()) {
            errorMessage = "至少需要配置一个监控路径";
            return false;
        }
        
        for (const auto& path : paths) {
            if (!ConfigValidator<std::string>::validatePath(path.path)) {
                errorMessage = "路径格式无效: " + path.path;
                return false;
            }
        }
        
        if (!ConfigValidator<size_t>::validateRange(maxBatchSize, 1, 1000)) {
            errorMessage = "批处理大小必须在1-1000之间";
            return false;
        }
        
        return true;
    }
    
    std::string getDescription() const override {
        return "文件系统监控配置 - 监控路径: " + std::to_string(paths.size()) + 
               ", 批处理间隔: " + std::to_string(batchInterval.count()) + "ms";
    }
    
    /**
     * 创建默认配置
     */
    static FilesystemConfig createDefault() {
        FilesystemConfig config;
        PathConfig defaultPath;
        defaultPath.path = ".";
        defaultPath.recursive = true;
        defaultPath.includeExtensions = {".txt", ".md", ".cpp", ".hpp", ".py", ".js", ".ts"};
        config.paths.push_back(defaultPath);
        return config;
    }
};

/**
 * 剪贴板连接器配置 - 极简版本
 */
class ClipboardConfig : public IConnectorConfig {
public:
    // 基础配置 - 只保留必要的
    size_t maxContentLength = 50000;
    
    void loadFromJson(const json& config) override {
        maxContentLength = config.value("max_content_length", 50000);
    }
    
    json toJson() const override {
        return json{
            {"type", "clipboard"},
            {"max_content_length", maxContentLength}
        };
    }
    
    bool validate(std::string& errorMessage) const override {
        if (!ConfigValidator<size_t>::validateRange(maxContentLength, 1000, 1000000)) {
            errorMessage = "最大内容长度必须在1000-1000000之间";
            return false;
        }
        return true;
    }
    
    std::string getDescription() const override {
        return "剪贴板监控 - 最大长度: " + std::to_string(maxContentLength);
    }
    
    /**
     * 创建默认配置 - 极简版本
     */
    static ClipboardConfig createDefault() {
        return ClipboardConfig{}; // 使用默认值
    }
};

/**
 * 配置工厂 - 根据连接器类型创建配置
 */
class ConfigFactory {
public:
    enum class ConnectorType {
        FILESYSTEM,
        CLIPBOARD,
        UNKNOWN
    };
    
    static std::unique_ptr<IConnectorConfig> createConfig(ConnectorType type) {
        switch (type) {
            case ConnectorType::FILESYSTEM:
                return std::make_unique<FilesystemConfig>(FilesystemConfig::createDefault());
            case ConnectorType::CLIPBOARD:
                return std::make_unique<ClipboardConfig>(ClipboardConfig::createDefault());
            default:
                return nullptr;
        }
    }
    
    static ConnectorType parseType(const std::string& typeStr) {
        if (typeStr == "filesystem") return ConnectorType::FILESYSTEM;
        if (typeStr == "clipboard") return ConnectorType::CLIPBOARD;
        return ConnectorType::UNKNOWN;
    }
};

} // namespace config
} // namespace linch_connector