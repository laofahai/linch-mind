#pragma once

#ifdef __APPLE__

#include "../file_index_provider.hpp"
#include <thread>
#include <atomic>

namespace linch_connector {

/**
 * macOS 文件索引查询提供者 - 用于System Info连接器
 * 
 * 利用Spotlight索引实现文件查询：
 * 1. queryAllFiles() - 使用mdfind查询所有文件
 * 2. queryByExtensions() - 按扩展名查询
 * 3. queryByPattern() - 按模式查询
 * 4. queryByDirectory() - 按目录查询
 * 
 * 优势：
 * - 零扫描：完全利用系统已有索引
 * - 无需特殊权限：运行在用户权限下
 * - 快速查询：毫秒级响应
 */
class MacOSFileIndexProvider : public IFileIndexProvider {
public:
    MacOSFileIndexProvider();
    ~MacOSFileIndexProvider() override;
    
    // IFileIndexProvider接口实现
    std::vector<FileRecord> queryAllFiles(size_t maxResults = 0) override;
    
    std::vector<FileRecord> queryByExtensions(
        const std::vector<std::string>& extensions,
        size_t maxResults = 0) override;
    
    std::vector<FileRecord> queryByPattern(
        const std::string& pattern,
        size_t maxResults = 0) override;
    
    std::vector<FileRecord> queryByDirectory(
        const std::string& directory,
        bool recursive = true,
        size_t maxResults = 0) override;
    
    bool isIndexServiceAvailable() override;
    nlohmann::json getIndexStatistics() override;
    bool refreshIndex() override;

private:
    // Spotlight查询执行
    std::vector<FileRecord> executeSpotlightQuery(
        const std::string& query, 
        size_t maxResults = 0);
    
    // 路径解析和文件信息获取
    FileRecord createFileRecordFromPath(const std::string& path);
    std::string executeCommand(const std::string& command) const;
    
    // Spotlight可用性检查
    bool checkSpotlightAvailability() const;
    std::string getSpotlightStatus() const;
    
    // 查询构建辅助方法
    std::string buildExtensionsQuery(const std::vector<std::string>& extensions);
    std::string buildPatternQuery(const std::string& pattern);
    std::string buildDirectoryQuery(const std::string& directory, bool recursive);
    
    // 辅助工具
    std::string sanitizePattern(const std::string& pattern);
    std::string escapeForSpotlight(const std::string& text);
    bool isValidPath(const std::string& path) const;
    
    // 状态管理
    mutable std::mutex m_statsMutex;
    std::atomic<bool> m_spotlightAvailable{false};
    
    // 默认查询限制
    static constexpr size_t DEFAULT_MAX_RESULTS = 10000;
    static constexpr const char* SPOTLIGHT_QUERY_ALL_FILES = 
        "kMDItemKind != 'Folder'";  // 查询所有非目录文件
};

} // namespace linch_connector

#endif // __APPLE__