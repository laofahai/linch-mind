#pragma once

#include "progress_types.hpp"
#include "../zero_scan/zero_scan_interface.hpp"
#include <string>
#include <vector>
#include <chrono>
#include <unordered_map>
#include <atomic>

namespace linch_connector {
namespace progress {

/**
 * 增量扫描会话信息
 * 扩展基础ScanSession，添加增量扫描特定数据
 */
struct IncrementalScanSession : public ScanSession {
    // 增量扫描特定信息
    std::string base_scan_session_id;                    // 基础全量扫描会话ID
    std::chrono::system_clock::time_point last_full_scan_time; // 上次全量扫描时间
    size_t total_changes_detected = 0;                   // 检测到的变更总数
    size_t changes_processed = 0;                        // 已处理的变更数
    
    // FSEvents监控状态
    bool fsevents_active = false;                        // FSEvents是否活跃
    std::chrono::system_clock::time_point fsevents_start_time; // FSEvents启动时间
    uint64_t fsevents_event_id = 0;                      // 当前FSEvents ID
    
    // 策略信息
    std::string current_strategy;                        // 当前使用的扫描策略
    std::vector<std::string> strategy_history;           // 策略使用历史
    
    IncrementalScanSession() {
        scan_type = "incremental";
    }
};

/**
 * 增量批次进度信息
 * 扩展基础BatchProgress，添加增量扫描特定数据
 */
struct IncrementalBatchProgress : public BatchProgress {
    // 增量扫描特定信息
    std::string scan_strategy;                           // 使用的扫描策略
    std::vector<std::string> target_paths;               // 目标扫描路径
    size_t changes_in_batch = 0;                         // 本批次的变更数量
    
    // 事件统计
    size_t created_files = 0;                            // 新建文件数
    size_t modified_files = 0;                           // 修改文件数
    size_t deleted_files = 0;                            // 删除文件数
    size_t renamed_files = 0;                            // 重命名文件数
    
    // 性能指标
    uint64_t fsevents_processing_latency_ms = 0;         // FSEvents处理延迟
    double mds_cpu_usage_peak = 0.0;                     // mds进程峰值CPU使用
    
    IncrementalBatchProgress() : BatchProgress() {
        query_type = "incremental_scan";
    }
};

/**
 * 增量扫描进度状态
 * 扩展基础ScanProgress，添加增量扫描特定数据
 */
struct IncrementalScanProgress : public ScanProgress {
    // 增量扫描会话信息
    IncrementalScanSession incremental_session;
    
    // 变更监控状态
    struct ChangeMonitoringState {
        bool monitoring_active = false;                  // 监控是否活跃
        size_t pending_changes = 0;                      // 待处理变更数
        size_t queue_size = 0;                           // 事件队列大小
        std::chrono::system_clock::time_point last_event_time; // 最后事件时间
        double event_processing_rate = 0.0;              // 事件处理速率
    } monitoring_state;
    
    // 策略执行历史
    struct StrategyExecution {
        std::string strategy;                            // 策略名称
        std::chrono::system_clock::time_point execution_time; // 执行时间
        uint64_t duration_ms = 0;                        // 执行耗时
        size_t files_processed = 0;                      // 处理文件数
        bool success = false;                             // 是否成功
        std::string error_message;                       // 错误信息
    };
    std::vector<StrategyExecution> strategy_history;
    
    // 系统负载监控
    struct SystemLoadState {
        double current_mds_cpu_usage = 0.0;              // 当前mds CPU使用率
        double peak_mds_cpu_usage = 0.0;                 // 峰值mds CPU使用率
        size_t current_memory_usage_mb = 0;              // 当前内存使用
        bool load_warning_active = false;                // 是否有负载警告
        std::chrono::system_clock::time_point last_check_time; // 最后检查时间
    } system_load;
    
    // 性能基准
    struct PerformanceBenchmark {
        uint64_t average_full_scan_duration_ms = 0;      // 平均全量扫描耗时
        uint64_t average_incremental_scan_duration_ms = 0; // 平均增量扫描耗时
        double full_scan_files_per_second = 0.0;         // 全量扫描处理速度
        double incremental_scan_files_per_second = 0.0;  // 增量扫描处理速度
        double strategy_efficiency_score = 0.0;          // 策略效率评分
    } performance_benchmark;
    
    IncrementalScanProgress() : ScanProgress() {
        session.scan_type = "incremental";
    }
};

/**
 * 增量扫描检查点
 * 扩展基础QuickCheckpoint，添加增量扫描特定数据
 */
struct IncrementalQuickCheckpoint : public QuickCheckpoint {
    // FSEvents状态
    uint64_t fsevents_event_id = 0;                      // FSEvents事件ID
    std::chrono::system_clock::time_point fsevents_timestamp; // FSEvents时间戳
    
    // 变更状态
    size_t pending_changes = 0;                          // 待处理变更数
    size_t queue_size = 0;                               // 队列大小
    std::string last_strategy;                           // 最后使用的策略
    
    // 性能状态
    double last_mds_cpu_usage = 0.0;                     // 最后的mds CPU使用率
    size_t last_memory_usage_mb = 0;                     // 最后的内存使用
    
    // 目标路径 (混合扫描)
    std::vector<std::string> target_paths;               // 目标扫描路径
    
    IncrementalQuickCheckpoint() : QuickCheckpoint() {
        // 继承基类构造函数
    }
};

/**
 * 增量扫描恢复选项
 * 扩展基础ResumeOptions，添加增量扫描特定选项
 */
struct IncrementalResumeOptions : public ResumeOptions {
    // FSEvents恢复
    bool resume_fsevents_monitoring = true;              // 恢复FSEvents监控
    bool validate_fsevents_continuity = true;            // 验证FSEvents连续性
    uint64_t max_event_id_gap = 1000;                    // 最大事件ID间隙
    
    // 策略恢复
    bool resume_last_strategy = true;                     // 恢复最后的策略
    bool allow_strategy_fallback = true;                 // 允许策略降级
    
    // 性能恢复
    bool restore_performance_state = true;               // 恢复性能状态
    bool reset_on_load_spike = true;                     // 负载峰值时重置
    
    IncrementalResumeOptions() : ResumeOptions() {
        // 继承基类构造函数
    }
};

/**
 * 增量扫描保存选项
 * 扩展基础SaveOptions，添加增量扫描特定选项
 */
struct IncrementalSaveOptions : public SaveOptions {
    // 增量数据保存
    bool save_fsevents_state = true;                     // 保存FSEvents状态
    bool save_change_queue_state = false;                // 保存变更队列状态
    bool save_strategy_history = true;                   // 保存策略历史
    
    // 保存频率
    std::chrono::seconds fsevents_checkpoint_interval{10}; // FSEvents检查点间隔
    size_t changes_save_frequency = 100;                 // 变更保存频率
    
    // 文件名扩展
    std::string incremental_checkpoint_filename = "incremental_checkpoint.json";
    std::string fsevents_state_filename = "fsevents_state.json";
    std::string strategy_history_filename = "strategy_history.json";
    
    IncrementalSaveOptions() : SaveOptions() {
        // 继承基类构造函数
    }
};

/**
 * FSEvents状态信息
 * 用于保存和恢复FSEvents监控状态
 */
struct FSEventsState {
    uint64_t last_event_id = 0;                          // 最后处理的事件ID
    std::chrono::system_clock::time_point last_event_time; // 最后事件时间
    std::vector<std::string> monitored_paths;            // 监控的路径
    bool stream_active = false;                           // 流是否活跃
    std::string stream_uuid;                              // 流的UUID
    
    // 性能统计
    size_t total_events_processed = 0;                   // 总处理事件数
    uint64_t average_processing_latency_ms = 0;          // 平均处理延迟
    double events_per_second = 0.0;                      // 每秒事件数
};

/**
 * 变更队列状态信息
 * 用于保存和恢复变更队列状态 (可选)
 */
struct ChangeQueueState {
    size_t queue_size = 0;                               // 队列大小
    size_t pending_changes = 0;                          // 待处理变更数
    std::chrono::system_clock::time_point oldest_event_time; // 最老事件时间
    std::chrono::system_clock::time_point newest_event_time; // 最新事件时间
    
    // 统计信息
    size_t total_events_enqueued = 0;                    // 总入队事件数
    size_t total_events_dequeued = 0;                    // 总出队事件数
    size_t events_dropped = 0;                           // 丢弃事件数
    double deduplication_rate = 0.0;                     // 去重率
};

/**
 * 增量扫描进度管理器接口扩展
 * 为ScanProgressManager添加增量扫描支持
 */
class IncrementalProgressManagerExtension {
public:
    virtual ~IncrementalProgressManagerExtension() = default;
    
    // === 增量会话管理 ===
    
    /**
     * 开始增量扫描会话
     * @param base_session_id 基础全量扫描会话ID
     * @param strategy 初始策略
     * @return 增量会话ID
     */
    virtual std::string startIncrementalSession(
        const std::string& base_session_id,
        const std::string& strategy
    ) = 0;
    
    /**
     * 更新FSEvents状态
     * @param event_id 当前事件ID
     * @param monitoring_active 监控是否活跃
     */
    virtual void updateFSEventsState(uint64_t event_id, bool monitoring_active) = 0;
    
    /**
     * 记录策略执行
     * @param strategy 策略名称
     * @param duration_ms 执行耗时
     * @param files_processed 处理文件数
     * @param success 是否成功
     */
    virtual void recordStrategyExecution(
        const std::string& strategy,
        uint64_t duration_ms,
        size_t files_processed,
        bool success,
        const std::string& error_message = ""
    ) = 0;
    
    /**
     * 更新系统负载状态
     * @param mds_cpu_usage mds CPU使用率
     * @param memory_usage_mb 内存使用
     */
    virtual void updateSystemLoadState(double mds_cpu_usage, size_t memory_usage_mb) = 0;
    
    /**
     * 保存增量检查点
     * @return 是否成功保存
     */
    virtual bool saveIncrementalCheckpoint() = 0;
    
    /**
     * 从增量检查点恢复
     * @param options 恢复选项
     * @return 恢复的进度信息
     */
    virtual std::optional<IncrementalScanProgress> resumeFromIncrementalCheckpoint(
        const IncrementalResumeOptions& options = IncrementalResumeOptions{}
    ) = 0;
    
    // === 状态查询 ===
    
    /**
     * 获取当前增量进度
     */
    virtual const IncrementalScanProgress& getCurrentIncrementalProgress() const = 0;
    
    /**
     * 获取FSEvents状态
     */
    virtual FSEventsState getFSEventsState() const = 0;
    
    /**
     * 获取变更队列状态
     */
    virtual ChangeQueueState getChangeQueueState() const = 0;
    
    /**
     * 获取策略执行历史
     */
    virtual std::vector<StrategyExecution> getStrategyHistory() const = 0;
};

} // namespace progress
} // namespace linch_connector