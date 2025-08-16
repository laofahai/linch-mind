#pragma once

#include <string>
#include <vector>
#include <functional>
#include <memory>
#include <chrono>
#include <optional>

namespace linch_connector {
namespace zero_scan {

/**
 * 文件记录 - 跨平台统一结构
 */
struct UnifiedFileRecord {
    // 基础信息
    std::string path;                  // 完整路径
    std::string name;                  // 文件名
    std::string extension;             // 扩展名
    
    // 元数据
    uint64_t size = 0;                // 文件大小（字节）
    uint64_t inode = 0;                // inode/文件ID
    std::chrono::system_clock::time_point modified_time;  // 修改时间
    std::chrono::system_clock::time_point created_time;   // 创建时间
    std::chrono::system_clock::time_point accessed_time;  // 访问时间
    
    // 属性
    bool is_directory = false;        // 是否目录
    bool is_hidden = false;           // 是否隐藏
    bool is_system = false;           // 是否系统文件
    
    // 平台特定（可选）
    std::optional<std::string> content_type;  // MIME 类型
    std::optional<uint64_t> parent_id;        // 父目录 ID
};

/**
 * 扫描配置 - 控制扫描行为
 */
struct ScanConfiguration {
    // 范围控制
    std::vector<std::string> include_paths;    // 包含路径
    std::vector<std::string> exclude_paths;    // 排除路径
    std::vector<std::string> exclude_patterns; // 排除模式（正则）
    
    // 性能控制
    size_t batch_size = 1000;                 // 批处理大小
    size_t max_results = 0;                   // 最大结果数（0=无限）
    std::chrono::milliseconds timeout{0};     // 超时时间（0=无限）
    
    // 过滤选项
    bool include_hidden = false;              // 包含隐藏文件
    bool include_system = false;              // 包含系统文件
    bool directories_only = false;            // 仅目录
    bool files_only = false;                  // 仅文件
    
    // 优化选项
    bool use_cache = true;                    // 使用缓存
    bool parallel_processing = true;          // 并行处理
    size_t thread_count = 0;                  // 线程数（0=自动）
};

/**
 * 扫描统计 - 性能指标
 */
struct ScanStatistics {
    // 数量统计
    size_t total_files = 0;                   // 文件总数
    size_t total_directories = 0;             // 目录总数
    size_t filtered_count = 0;                // 过滤数量
    size_t error_count = 0;                   // 错误数量
    
    // 性能指标
    uint64_t scan_duration_ms = 0;            // 扫描耗时
    uint64_t files_per_second = 0;            // 处理速度
    size_t memory_usage_mb = 0;               // 内存使用
    
    // 方法信息
    std::string scan_method;                  // 使用的扫描方法
    std::string platform;                     // 平台信息
    bool used_cache = false;                  // 是否使用缓存
    
    // 时间戳
    std::chrono::system_clock::time_point start_time;
    std::chrono::system_clock::time_point end_time;
};

/**
 * 文件变更事件
 */
enum class FileChangeType {
    CREATED,
    MODIFIED,
    DELETED,
    RENAMED,
    MOVED
};

struct FileChangeEvent {
    FileChangeType type;
    UnifiedFileRecord file;
    std::string old_path;  // 用于 RENAMED/MOVED
    std::chrono::system_clock::time_point timestamp;
};

/**
 * 零扫描接口 - 跨平台统一 API
 * 
 * 这是所有平台实现必须遵循的接口
 * 确保上层代码可以无缝切换平台
 */
class IZeroScanProvider {
public:
    virtual ~IZeroScanProvider() = default;
    
    // 生命周期管理
    virtual bool initialize(const ScanConfiguration& config) = 0;
    virtual void shutdown() = 0;
    
    // 核心功能：零扫描
    virtual bool performZeroScan(
        std::function<void(const UnifiedFileRecord&)> callback
    ) = 0;
    
    // 增量更新：订阅变化
    virtual bool subscribeToChanges(
        std::function<void(const FileChangeEvent&)> callback
    ) = 0;
    
    virtual void unsubscribeFromChanges() = 0;
    
    // 查询和状态
    virtual ScanStatistics getStatistics() const = 0;
    virtual bool isAvailable() const = 0;
    virtual std::string getPlatformInfo() const = 0;
    
    // 配置更新
    virtual void updateConfiguration(const ScanConfiguration& config) = 0;
    
    // 缓存管理
    virtual void clearCache() = 0;
    virtual bool warmupCache() = 0;
    
    // 性能控制
    virtual void pause() = 0;
    virtual void resume() = 0;
    virtual void setThrottleLevel(int level) = 0;  // 0-100
};

/**
 * 零扫描工厂 - 创建平台特定实现
 */
class ZeroScanFactory {
public:
    // 创建最佳可用的提供者
    static std::unique_ptr<IZeroScanProvider> createProvider();
    
    // 创建特定类型的提供者
    enum class ProviderType {
        AUTO,           // 自动选择最佳
        NATIVE,         // 平台原生（MFT/Spotlight/locate）
        SYSTEM_API,     // 系统 API（Search/MDQuery/updatedb）
        FALLBACK        // 降级方案
    };
    
    static std::unique_ptr<IZeroScanProvider> createProvider(ProviderType type);
    
    // 查询可用的提供者
    static std::vector<std::string> getAvailableProviders();
    
    // 性能基准测试
    static ScanStatistics runBenchmark(const ScanConfiguration& config);
};

/**
 * 性能监控器 - 实时性能监控
 */
class PerformanceMonitor {
public:
    void startMonitoring();
    void stopMonitoring();
    
    struct Metrics {
        double cpu_usage_percent;
        size_t memory_usage_mb;
        size_t io_operations_per_sec;
        size_t files_processed_per_sec;
    };
    
    Metrics getCurrentMetrics() const;
    void setAlertThreshold(const Metrics& threshold);
    void setAlertCallback(std::function<void(const Metrics&)> callback);
    
private:
    bool m_monitoring = false;
    Metrics m_current_metrics;
    Metrics m_threshold;
    std::function<void(const Metrics&)> m_alert_callback;
};

} // namespace zero_scan
} // namespace linch_connector