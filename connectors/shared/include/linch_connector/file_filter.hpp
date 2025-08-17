#pragma once

#include <string>
#include <vector>
#include <set>
#include <regex>
#include <unordered_set>
#include <filesystem>

namespace linch_connector {

/**
 * 跨平台文件过滤器
 * 提供全面的文件过滤功能，包括：
 * - 跨平台通用过滤规则
 * - 平台特定过滤规则  
 * - 文件类型过滤
 * - 路径验证和清理
 */
class FileFilter {
public:
    /**
     * 构造函数
     * @param enablePlatformSpecific 是否启用平台特定过滤
     */
    explicit FileFilter(bool enablePlatformSpecific = true);

    /**
     * 检查文件是否应该被过滤掉
     * @param path 文件路径
     * @return true表示应该过滤掉，false表示应该保留
     */
    bool shouldFilter(const std::string& path) const;

    /**
     * 检查文件扩展名是否在包含列表中
     * @param path 文件路径
     * @return true表示包含，false表示不包含
     */
    bool isIncludedExtension(const std::string& path) const;

    /**
     * 验证文件路径是否安全有效
     * @param path 文件路径
     * @return true表示有效，false表示无效
     */
    bool isValidPath(const std::string& path) const;

    /**
     * 清理文件路径
     * @param path 原始路径
     * @return 清理后的路径
     */
    std::string cleanPath(const std::string& path) const;

    /**
     * 设置包含的文件扩展名
     * @param extensions 扩展名集合
     */
    void setIncludeExtensions(const std::set<std::string>& extensions);

    /**
     * 添加自定义排除模式
     * @param pattern 正则表达式模式
     */
    void addExcludePattern(const std::string& pattern);

    /**
     * 设置排除模式
     * @param patterns 正则表达式模式集合
     */
    void setExcludePatterns(const std::vector<std::string>& patterns);

    /**
     * 设置最大文件大小限制（字节）
     * @param maxSize 最大文件大小
     */
    void setMaxFileSize(size_t maxSize);

    /**
     * 获取统计信息
     */
    struct Statistics {
        size_t totalChecked = 0;
        size_t filtered = 0;
        size_t invalidPaths = 0;
        size_t oversizedFiles = 0;
        size_t extensionFiltered = 0;
        size_t patternFiltered = 0;
    };

    Statistics getStatistics() const;
    void resetStatistics();

private:
    // 配置选项
    bool m_enablePlatformSpecific;
    std::set<std::string> m_includeExtensions;
    std::vector<std::regex> m_excludePatterns;
    size_t m_maxFileSize;

    // 统计信息
    mutable Statistics m_stats;

    // 预定义过滤规则
    std::unordered_set<std::string> m_commonExcludeDirs;
    std::unordered_set<std::string> m_commonExcludeFiles;
    std::unordered_set<std::string> m_binaryExtensions;
    std::unordered_set<std::string> m_temporaryExtensions;

    // 平台特定规则
    std::unordered_set<std::string> m_macosSpecificExcludes;
    std::unordered_set<std::string> m_windowsSpecificExcludes;
    std::unordered_set<std::string> m_linuxSpecificExcludes;

    /**
     * 初始化预定义规则
     */
    void initializePredefinedRules();

    /**
     * 检查是否为常见排除目录
     */
    bool isCommonExcludeDir(const std::string& dirName) const;

    /**
     * 检查是否为常见排除文件
     */
    bool isCommonExcludeFile(const std::string& fileName) const;

    /**
     * 检查是否为二进制文件
     */
    bool isBinaryFile(const std::string& path) const;

    /**
     * 检查是否为临时文件
     */
    bool isTemporaryFile(const std::string& path) const;

    /**
     * 检查平台特定排除规则
     */
    bool isPlatformSpecificExclude(const std::string& path) const;

    /**
     * 检查文件大小是否超限
     */
    bool isOversized(const std::string& path) const;

    /**
     * 匹配排除模式
     */
    bool matchesExcludePattern(const std::string& path) const;

    /**
     * 获取文件扩展名
     */
    std::string getExtension(const std::string& path) const;

    /**
     * 获取文件名
     */
    std::string getFileName(const std::string& path) const;
};

/**
 * 快速文件过滤器配置结构
 */
struct FileFilterConfig {
    bool enablePlatformSpecific = true;
    std::set<std::string> includeExtensions;
    std::vector<std::string> excludePatterns;
    size_t maxFileSize = 100 * 1024 * 1024; // 100MB

    /**
     * 创建默认配置
     */
    static FileFilterConfig createDefault();

    /**
     * 创建开发环境配置
     */
    static FileFilterConfig createDevelopment();

    /**
     * 创建文档环境配置
     */
    static FileFilterConfig createDocuments();
};

} // namespace linch_connector