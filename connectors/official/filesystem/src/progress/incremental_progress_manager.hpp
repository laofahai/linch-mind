#pragma once

#include "scan_progress_manager.hpp"
#include "incremental_progress_types.hpp"
#include <memory>
#include <atomic>
#include <mutex>

namespace linch_connector {
namespace progress {

/**
 * 增量扫描进度管理器
 * 
 * 扩展基础ScanProgressManager，添加增量扫描特定功能：
 * 1. FSEvents状态管理
 * 2. 策略执行历史跟踪
 * 3. 系统负载监控
 * 4. 增量检查点保存/恢复
 */
class IncrementalProgressManager : public IncrementalProgressManagerExtension {
public:
    /**
     * 构造函数
     * @param base_manager 基础进度管理器
     */
    explicit IncrementalProgressManager(std::shared_ptr<ScanProgressManager> base_manager);
    
    ~IncrementalProgressManager() override;
    
    // === IncrementalProgressManagerExtension 接口实现 ===
    
    std::string startIncrementalSession(
        const std::string& base_session_id,
        const std::string& strategy
    ) override;
    
    void updateFSEventsState(uint64_t event_id, bool monitoring_active) override;
    
    void recordStrategyExecution(
        const std::string& strategy,
        uint64_t duration_ms,
        size_t files_processed,
        bool success,
        const std::string& error_message = ""
    ) override;
    
    void updateSystemLoadState(double mds_cpu_usage, size_t memory_usage_mb) override;
    
    bool saveIncrementalCheckpoint() override;
    
    std::optional<IncrementalScanProgress> resumeFromIncrementalCheckpoint(
        const IncrementalResumeOptions& options = IncrementalResumeOptions{}
    ) override;
    
    const IncrementalScanProgress& getCurrentIncrementalProgress() const override;
    
    FSEventsState getFSEventsState() const override;
    
    ChangeQueueState getChangeQueueState() const override;
    
    std::vector<StrategyExecution> getStrategyHistory() const override;
    
    // === 扩展功能 ===
    
    /**
     * 初始化增量进度管理器
     * @param config 扫描配置
     * @param options 增量保存选项
     * @return 是否成功初始化
     */
    bool initialize(const zero_scan::ScanConfiguration& config,
                   const IncrementalSaveOptions& options = IncrementalSaveOptions{});
    
    /**
     * 更新变更监控状态
     * @param monitoring_active 监控是否活跃
     * @param pending_changes 待处理变更数
     * @param queue_size 队列大小
     * @param processing_rate 处理速率
     */
    void updateChangeMonitoringState(
        bool monitoring_active,
        size_t pending_changes,
        size_t queue_size,
        double processing_rate
    );
    
    /**
     * 记录性能基准
     * @param strategy 策略类型
     * @param duration_ms 执行时间
     * @param files_per_second 处理速度
     */
    void recordPerformanceBenchmark(
        const std::string& strategy,
        uint64_t duration_ms,
        double files_per_second
    );
    
    /**
     * 设置负载警告状态
     * @param warning_active 是否有负载警告
     * @param reason 警告原因
     */
    void setLoadWarning(bool warning_active, const std::string& reason = "");
    
    /**
     * 获取策略效率评分
     * @return 0.0-1.0的效率评分
     */
    double getStrategyEfficiencyScore() const;
    
    /**
     * 检查是否需要切换策略
     * @param current_strategy 当前策略
     * @return 是否建议切换
     */
    bool shouldSwitchStrategy(const std::string& current_strategy) const;
    
    /**
     * 清除增量进度数据
     */
    void clearIncrementalProgress();
    
    // === 委托到基础管理器的方法 ===
    
    /**
     * 获取基础进度管理器
     */
    std::shared_ptr<ScanProgressManager> getBaseManager() const { return m_base_manager; }
    
    /**
     * 委托基础方法
     */
    std::optional<ScanProgress> tryResumeFromCheckpoint(const ResumeOptions& options = ResumeOptions{}) {
        return m_base_manager->tryResumeFromCheckpoint(options);
    }
    
    bool hasValidCheckpoint() const {
        return m_base_manager->hasValidCheckpoint();
    }
    
    void startBatch(size_t batch_index, const std::string& query_type, const std::string& query_string) {
        m_base_manager->startBatch(batch_index, query_type, query_string);
    }
    
    void updateBatchProgress(size_t files_processed, size_t files_found) {
        m_base_manager->updateBatchProgress(files_processed, files_found);
    }
    
    void completeBatch(double cpu_usage_peak = 0.0, size_t memory_usage_peak = 0) {
        m_base_manager->completeBatch(cpu_usage_peak, memory_usage_peak);
    }
    
    void completeSession() {
        m_base_manager->completeSession();
        completeIncrementalSession();
    }
    
    void recordError(const std::string& error_message) {
        m_base_manager->recordError(error_message);
    }
    
    const ScanProgress& getCurrentProgress() const {
        return m_base_manager->getCurrentProgress();
    }

private:
    // === 内部状态 ===
    std::shared_ptr<ScanProgressManager> m_base_manager;
    IncrementalSaveOptions m_options;
    mutable IncrementalScanProgress m_incremental_progress;
    
    // 文件路径
    std::filesystem::path m_incremental_checkpoint_path;
    std::filesystem::path m_fsevents_state_path;
    std::filesystem::path m_strategy_history_path;
    
    // 线程安全
    mutable std::mutex m_mutex;
    std::atomic<bool> m_initialized{false};
    std::atomic<std::chrono::system_clock::time_point> m_last_incremental_save_time;
    
    // 状态缓存
    mutable FSEventsState m_fsevents_state;
    mutable ChangeQueueState m_queue_state;
    std::string m_current_load_warning_reason;
    
    // 统计计数器
    std::atomic<size_t> m_total_strategy_executions{0};
    std::atomic<size_t> m_successful_strategy_executions{0};
    
    // === 内部实现方法 ===
    
    // 初始化和路径管理
    bool setupIncrementalPaths();
    std::filesystem::path getIncrementalProgressDirectory() const;
    
    // 完成增量会话
    void completeIncrementalSession();
    
    // JSON序列化/反序列化
    nlohmann::json serializeIncrementalCheckpoint(const IncrementalQuickCheckpoint& checkpoint) const;
    nlohmann::json serializeFSEventsState(const FSEventsState& state) const;
    nlohmann::json serializeStrategyHistory(const std::vector<StrategyExecution>& history) const;
    nlohmann::json serializeIncrementalProgress(const IncrementalScanProgress& progress) const;
    
    bool deserializeIncrementalCheckpoint(const nlohmann::json& json, IncrementalQuickCheckpoint& checkpoint) const;
    bool deserializeFSEventsState(const nlohmann::json& json, FSEventsState& state) const;
    bool deserializeStrategyHistory(const nlohmann::json& json, std::vector<StrategyExecution>& history) const;
    bool deserializeIncrementalProgress(const nlohmann::json& json, IncrementalScanProgress& progress) const;
    
    // 文件I/O操作
    bool saveIncrementalJsonToFile(const nlohmann::json& json, const std::filesystem::path& file_path) const;
    bool loadIncrementalJsonFromFile(const std::filesystem::path& file_path, nlohmann::json& json) const;
    
    // 状态同步
    void syncWithBaseProgress();
    void updateIncrementalProgressFromBase();
    
    // 策略分析
    void analyzeStrategyPerformance();
    double calculateStrategySuccessRate(const std::string& strategy) const;
    uint64_t calculateAverageStrategyDuration(const std::string& strategy) const;
    
    // 自动保存逻辑
    bool shouldAutoSaveIncremental() const;
    void triggerIncrementalAutoSaveIfNeeded();
    
    // 数据验证
    bool validateIncrementalCheckpoint(const IncrementalQuickCheckpoint& checkpoint) const;
    bool validateFSEventsState(const FSEventsState& state) const;
    
    // 从增量检查点重构进度
    IncrementalScanProgress reconstructIncrementalProgressFromCheckpoint(
        const IncrementalQuickCheckpoint& checkpoint
    ) const;
    
    // 错误处理和日志
    void logIncrementalInfo(const std::string& message) const;
    void logIncrementalWarning(const std::string& message) const;
    void logIncrementalError(const std::string& operation, const std::string& error) const;
    
    // 时间和ID生成
    std::string generateIncrementalSessionId() const;
    
    // 性能优化
    void cleanupOldStrategyHistory();
    void optimizeStrategyHistorySize();
    
    // 配置管理
    void updateIncrementalConfigFromBase();
    bool hasIncrementalConfigurationChanged() const;
};

/**
 * 增量进度管理器工厂
 */
class IncrementalProgressManagerFactory {
public:
    /**
     * 创建增量进度管理器
     * @param base_manager 基础进度管理器
     * @return 增量管理器实例
     */
    static std::unique_ptr<IncrementalProgressManager> create(
        std::shared_ptr<ScanProgressManager> base_manager
    );
    
    /**
     * 创建带配置的增量管理器
     * @param base_manager 基础进度管理器
     * @param config 扫描配置
     * @param options 增量保存选项
     * @return 增量管理器实例
     */
    static std::unique_ptr<IncrementalProgressManager> createWithOptions(
        std::shared_ptr<ScanProgressManager> base_manager,
        const zero_scan::ScanConfiguration& config,
        const IncrementalSaveOptions& options
    );
    
    /**
     * 从现有基础管理器升级为增量管理器
     * @param base_manager 基础进度管理器
     * @param preserve_state 是否保留现有状态
     * @return 升级后的增量管理器实例
     */
    static std::unique_ptr<IncrementalProgressManager> upgradeFromBase(
        std::shared_ptr<ScanProgressManager> base_manager,
        bool preserve_state = true
    );
};

} // namespace progress
} // namespace linch_connector