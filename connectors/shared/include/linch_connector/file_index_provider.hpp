#pragma once

#include <string>
#include <vector>
#include <memory>
#include <functional>
#include <chrono>
#include <nlohmann/json.hpp>

namespace linch_connector {

/**
 * 轻量级文件信息结构 - 用于实时监控
 * 避免全盘扫描，只存储必要的元数据
 */
struct FileInfo {
    std::string path;           // 完整路径
    std::string name;           // 文件名
    std::string extension;      // 扩展名 (如 .txt)
    uint64_t size;             // 文件大小 (字节)
    std::chrono::system_clock::time_point modified_time;  // 修改时间
    bool is_directory;         // 是否为目录
    
    FileInfo() : size(0), is_directory(false) {}
};

/**
 * 文件记录结构 - 用于索引查询
 * 兼容不同平台的索引系统
 */
struct FileRecord {
    std::string path;           // 文件完整路径
    std::string name;           // 文件名
    std::string extension;      // 文件扩展名
    uint64_t size;              // 文件大小（字节）
    uint64_t modified_time;     // 修改时间（Unix时间戳）
    std::string directory;      // 所在目录
    bool is_directory;          // 是否为目录
    
    FileRecord() : size(0), modified_time(0), is_directory(false) {}
    
    // 转换构造函数：从 FileInfo 转换到 FileRecord
    explicit FileRecord(const FileInfo& info) {
        path = info.path;
        name = info.name;
        extension = info.extension;
        size = info.size;
        auto time_t = std::chrono::system_clock::to_time_t(info.modified_time);
        modified_time = static_cast<uint64_t>(time_t);
        
        // 提取目录路径
        auto pos = path.find_last_of("/\\");
        if (pos != std::string::npos) {
            directory = path.substr(0, pos);
        }
        
        is_directory = info.is_directory;
    }
};

/**
 * 文件变更事件类型
 */
enum class FileEventType {
    CREATED,     // 文件创建
    MODIFIED,    // 文件修改
    DELETED,     // 文件删除
    RENAMED,     // 文件重命名
    MOVED        // 文件移动
};

/**
 * 文件变更事件
 */
struct FileEvent {
    FileEventType type;
    std::string path;              // 当前路径
    std::string old_path;          // 旧路径(仅用于RENAMED/MOVED)
    FileInfo file_info;           // 文件信息(仅用于CREATED/MODIFIED)
    std::chrono::system_clock::time_point timestamp;
    
    FileEvent(FileEventType t, const std::string& p) 
        : type(t), path(p), timestamp(std::chrono::system_clock::now()) {}
};

/**
 * 索引统计信息
 */
struct IndexStats {
    uint64_t total_files = 0;      // 总文件数
    uint64_t indexed_files = 0;    // 已索引文件数
    uint64_t memory_usage_mb = 0;  // 内存使用(MB)
    bool is_initialized = false;   // 是否完成初始化
    bool is_watching = false;      // 是否在监控变更
    std::string platform_info;     // 平台信息
    std::string last_error;        // 最后的错误信息
    
    // 转换为JSON格式
    nlohmann::json toJson() const {
        return nlohmann::json{
            {"total_files", total_files},
            {"indexed_files", indexed_files},
            {"memory_usage_mb", memory_usage_mb},
            {"is_initialized", is_initialized},
            {"is_watching", is_watching},
            {"platform_info", platform_info},
            {"last_error", last_error}
        };
    }
};

/**
 * 回调函数定义
 */
using InitialBatchCallback = std::function<void(const std::vector<FileInfo>&)>;
using FileEventCallback = std::function<void(const FileEvent&)>;
using ProgressCallback = std::function<void(uint64_t indexed, uint64_t total)>;

/**
 * 实时文件监控提供者接口 - 用于Filesystem连接器
 * 
 * 设计原则：
 * 1. 避免全盘扫描 - 利用操作系统已有索引
 * 2. 最小权限要求 - 在用户权限下运行
 * 3. 流式数据传输 - 避免大块内存占用
 * 4. 实时变更监控 - 低延迟事件通知
 */
class IFileMonitorProvider {
public:
    virtual ~IFileMonitorProvider() = default;
    
    /**
     * 初始化监控提供者
     * @return true 如果成功初始化
     */
    virtual bool initialize() = 0;
    
    /**
     * 开始监控文件变更
     * @return true 如果成功启动监控
     */
    virtual bool watchChanges() = 0;
    
    /**
     * 停止所有操作
     */
    virtual void stop() = 0;
    
    /**
     * 获取统计信息
     */
    virtual IndexStats getStats() const = 0;
    
    /**
     * 检查提供者是否可用
     */
    virtual bool isAvailable() const = 0;
    
    /**
     * 获取平台信息
     */
    virtual std::string getPlatformInfo() const = 0;
    
    // 设置回调函数
    virtual void setInitialBatchCallback(InitialBatchCallback callback) = 0;
    virtual void setFileEventCallback(FileEventCallback callback) = 0;
    virtual void setProgressCallback(ProgressCallback callback) = 0;
    
    /**
     * 设置监控的根目录列表
     */
    virtual void setWatchDirectories(const std::vector<std::string>& directories) = 0;
    
    /**
     * 设置排除模式
     */
    virtual void setExcludePatterns(const std::vector<std::string>& patterns) = 0;
};

/**
 * 文件索引查询提供者接口 - 用于System Info连接器
 * 
 * 用于从不同的系统索引服务中查询文件信息：
 * - macOS: Spotlight (mdfind)
 * - Linux: locate/updatedb
 * - Windows: Windows Search Index
 */
class IFileIndexProvider {
public:
    virtual ~IFileIndexProvider() = default;
    
    /**
     * 查询所有文件
     * @param maxResults 最大结果数量（0表示无限制）
     * @return 文件记录列表
     */
    virtual std::vector<FileRecord> queryAllFiles(size_t maxResults = 0) = 0;
    
    /**
     * 按文件扩展名查询
     * @param extensions 文件扩展名列表（如{".txt", ".pdf"}）
     * @param maxResults 最大结果数量
     * @return 匹配的文件记录列表
     */
    virtual std::vector<FileRecord> queryByExtensions(
        const std::vector<std::string>& extensions,
        size_t maxResults = 0) = 0;
    
    /**
     * 按文件名模式查询
     * @param pattern 文件名模式（支持通配符）
     * @param maxResults 最大结果数量
     * @return 匹配的文件记录列表
     */
    virtual std::vector<FileRecord> queryByPattern(
        const std::string& pattern,
        size_t maxResults = 0) = 0;
    
    /**
     * 按目录查询
     * @param directory 目录路径
     * @param recursive 是否递归查询子目录
     * @param maxResults 最大结果数量
     * @return 目录中的文件记录列表
     */
    virtual std::vector<FileRecord> queryByDirectory(
        const std::string& directory,
        bool recursive = true,
        size_t maxResults = 0) = 0;
    
    /**
     * 检查索引服务是否可用
     * @return true表示可用，false表示不可用
     */
    virtual bool isIndexServiceAvailable() = 0;
    
    /**
     * 获取索引统计信息
     * @return 包含文件总数等统计信息的JSON对象
     */
    virtual nlohmann::json getIndexStatistics() = 0;
    
    /**
     * 刷新索引（如果支持）
     * @return true表示成功，false表示失败或不支持
     */
    virtual bool refreshIndex() = 0;
};

/**
 * 文件监控提供者工厂 - 为Filesystem连接器使用
 */
class FileMonitorProviderFactory {
public:
    /**
     * 创建适合当前平台的监控提供者
     */
    static std::unique_ptr<IFileMonitorProvider> createProvider();
    
    /**
     * 获取当前平台名称
     */
    static std::string getPlatformName();
    
    /**
     * 检查当前平台是否支持零扫描索引
     */
    static bool isZeroScanSupported();
};

/**
 * 文件索引提供者工厂 - 为System Info连接器使用
 */
class FileIndexProviderFactory {
public:
    /**
     * 创建适合当前平台的文件索引提供者
     * @return 文件索引提供者实例
     */
    static std::unique_ptr<IFileIndexProvider> createForCurrentPlatform();
    
private:
    FileIndexProviderFactory() = default;
};

} // namespace linch_connector