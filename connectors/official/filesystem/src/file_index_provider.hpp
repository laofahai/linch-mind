#pragma once

#include <string>
#include <vector>
#include <memory>
#include <functional>
#include <chrono>

namespace linch_connector {

/**
 * 轻量级文件信息结构
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
};

/**
 * 回调函数定义
 */
using InitialBatchCallback = std::function<void(const std::vector<FileInfo>&)>;
using FileEventCallback = std::function<void(const FileEvent&)>;
using ProgressCallback = std::function<void(uint64_t indexed, uint64_t total)>;

/**
 * 统一文件索引提供者接口
 * 
 * 设计原则：
 * 1. 避免全盘扫描 - 利用操作系统已有索引
 * 2. 最小权限要求 - 在用户权限下运行
 * 3. 流式数据传输 - 避免大块内存占用
 * 4. 实时变更监控 - 低延迟事件通知
 */
class FileIndexProvider {
public:
    virtual ~FileIndexProvider() = default;
    
    /**
     * 初始化索引提供者
     * 
     * @return true 如果成功初始化
     * 
     * 实现策略：
     * - Windows: 读取MFT或Windows Search Index
     * - macOS: 查询Spotlight索引 (mdfind)
     * - Linux: 读取locate数据库
     */
    virtual bool initialize() = 0;
    
    /**
     * 开始监控文件变更
     * 
     * @return true 如果成功启动监控
     * 
     * 实现策略：
     * - Windows: USN Journal或ReadDirectoryChanges
     * - macOS: FSEvents API
     * - Linux: inotify或fanotify
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
     * (例如检查系统索引服务状态)
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
     * 默认监控用户主目录，可以添加额外目录
     */
    virtual void setWatchDirectories(const std::vector<std::string>& directories) = 0;
    
    /**
     * 设置排除模式
     */
    virtual void setExcludePatterns(const std::vector<std::string>& patterns) = 0;
};

/**
 * 文件索引提供者工厂
 */
class FileIndexProviderFactory {
public:
    /**
     * 创建适合当前平台的提供者
     */
    static std::unique_ptr<FileIndexProvider> createProvider();
    
    /**
     * 获取当前平台名称
     */
    static std::string getPlatformName();
    
    /**
     * 检查当前平台是否支持零扫描索引
     */
    static bool isZeroScanSupported();
};

} // namespace linch_connector