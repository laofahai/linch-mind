#pragma once

#include "progress_types.hpp"
#include "../zero_scan/zero_scan_interface.hpp"
#include <nlohmann/json.hpp>
#include <string>
#include <memory>
#include <functional>
#include <filesystem>
#include <fstream>
#include <atomic>
#include <mutex>

namespace linch_connector {
namespace progress {

/**
 * 扫描进度管理器 - 轻量级JSON实现
 * 
 * 核心设计原则：
 * 1. 轻量级：纯JSON存储，无外部依赖
 * 2. 高性能：快速检查点 + 定期详细保存
 * 3. 原子性：临时文件 + 重命名确保数据安全
 * 4. 环境感知：使用 ~/.linch-mind/{env}/filesystem/ 目录
 */
class ScanProgressManager {
public:
    /**
     * 构造函数
     * @param environment_name 环境名称 ("development", "production", etc.)
     */
    explicit ScanProgressManager(const std::string& environment_name = "development");
    
    /**
     * 析构函数 - 确保保存最终状态
     */
    ~ScanProgressManager();
    
    // === 核心功能接口 ===
    
    /**
     * 初始化进度管理器
     * @param config 扫描配置
     * @param save_options 保存选项
     * @return 是否成功初始化
     */
    bool initialize(const zero_scan::ScanConfiguration& config, 
                   const SaveOptions& save_options = SaveOptions{});
    
    /**
     * 开始新的扫描会话
     * @param scan_type 扫描类型 ("full", "incremental", "resume")
     * @param query_types_order 查询类型顺序
     * @return 会话ID
     */
    std::string startNewSession(const std::string& scan_type,
                               const std::vector<std::string>& query_types_order);
    
    /**
     * 尝试从检查点恢复
     * @param resume_options 恢复选项
     * @return 恢复的进度信息，如果无法恢复则返回空
     */
    std::optional<ScanProgress> tryResumeFromCheckpoint(const ResumeOptions& resume_options = ResumeOptions{});
    
    /**
     * 检查是否有有效的检查点可以恢复
     * @return 是否有可恢复的检查点
     */
    bool hasValidCheckpoint() const;
    
    // === 进度更新接口 ===
    
    /**
     * 开始新的批次
     * @param batch_index 批次索引
     * @param query_type 查询类型
     * @param query_string 查询字符串
     */
    void startBatch(size_t batch_index, const std::string& query_type, const std::string& query_string);
    
    /**
     * 更新批次进度
     * @param files_processed 已处理文件数
     * @param files_found 发现的文件总数
     */
    void updateBatchProgress(size_t files_processed, size_t files_found);
    
    /**
     * 完成当前批次
     * @param cpu_usage_peak 峰值CPU使用率
     * @param memory_usage_peak 峰值内存使用 (MB)
     */
    void completeBatch(double cpu_usage_peak = 0.0, size_t memory_usage_peak = 0);
    
    /**
     * 标记整个扫描完成
     */
    void completeSession();
    
    /**
     * 记录错误
     * @param error_message 错误信息
     */
    void recordError(const std::string& error_message);
    
    // === 查询接口 ===
    
    /**
     * 获取当前进度
     * @return 当前进度状态
     */
    const ScanProgress& getCurrentProgress() const { return m_current_progress; }
    
    /**
     * 获取完成百分比
     * @return 0.0 - 1.0 的完成百分比
     */
    double getCompletionPercentage() const;
    
    /**
     * 获取预估剩余时间 (毫秒)
     * @return 预估剩余时间，0表示无法预估
     */
    uint64_t getEstimatedRemainingTime() const;
    
    /**
     * 是否应该跳过某个查询类型 (因为已完成)
     * @param query_type 查询类型
     * @return 是否应该跳过
     */
    bool shouldSkipQueryType(const std::string& query_type) const;
    
    /**
     * 获取下一个应该处理的批次索引
     * @return 下一个批次索引
     */
    size_t getNextBatchIndex() const;
    
    // === 手动保存/加载 ===
    
    /**
     * 立即保存检查点
     * @return 是否成功保存
     */
    bool saveCheckpoint();
    
    /**
     * 立即保存详细进度
     * @return 是否成功保存
     */
    bool saveDetailedProgress();
    
    /**
     * 清除所有进度数据 (重新开始)
     */
    void clearAllProgress();
    
    // === 配置和环境 ===
    
    /**
     * 检查配置是否发生变化
     * @param current_config 当前配置
     * @return 配置是否发生变化
     */
    bool hasConfigurationChanged(const zero_scan::ScanConfiguration& current_config) const;
    
    /**
     * 获取进度文件的存储目录
     * @return 进度文件目录路径
     */
    std::filesystem::path getProgressDirectory() const;

private:
    // === 内部状态 ===
    std::string m_environment_name;                   // 环境名称
    SaveOptions m_save_options;                       // 保存选项
    ScanProgress m_current_progress;                  // 当前进度
    zero_scan::ScanConfiguration m_last_config;      // 上次配置
    
    // 文件路径
    std::filesystem::path m_progress_dir;             // 进度目录
    std::filesystem::path m_checkpoint_path;          // 检查点文件路径
    std::filesystem::path m_progress_path;            // 详细进度文件路径
    std::filesystem::path m_config_hash_path;         // 配置哈希文件路径
    
    // 线程安全
    mutable std::mutex m_mutex;                       // 互斥锁
    std::atomic<bool> m_initialized{false};           // 是否已初始化
    std::atomic<std::chrono::system_clock::time_point> m_last_save_time; // 上次保存时间
    
    // 性能统计
    std::atomic<size_t> m_checkpoint_save_count{0};   // 检查点保存次数
    std::atomic<size_t> m_progress_save_count{0};     // 详细进度保存次数
    
    // === 内部实现方法 ===
    
    // 目录和路径管理
    bool ensureProgressDirectory();
    std::filesystem::path getUserDataDirectory() const;
    
    // JSON序列化/反序列化
    nlohmann::json serializeCheckpoint(const QuickCheckpoint& checkpoint) const;
    nlohmann::json serializeProgress(const ScanProgress& progress) const;
    nlohmann::json serializeConfig(const zero_scan::ScanConfiguration& config) const;
    
    bool deserializeCheckpoint(const nlohmann::json& json, QuickCheckpoint& checkpoint) const;
    bool deserializeProgress(const nlohmann::json& json, ScanProgress& progress) const;
    bool deserializeConfig(const nlohmann::json& json, zero_scan::ScanConfiguration& config) const;
    
    // 文件I/O操作 (原子性)
    bool saveJsonToFile(const nlohmann::json& json, const std::filesystem::path& file_path) const;
    bool loadJsonFromFile(const std::filesystem::path& file_path, nlohmann::json& json) const;
    
    // 配置管理
    std::string calculateConfigHash(const zero_scan::ScanConfiguration& config) const;
    bool saveConfigHash(const std::string& hash) const;
    std::string loadConfigHash() const;
    
    // 时间和统计
    std::string generateSessionId() const;
    void updateStatistics();
    void updateEstimatedTime();
    
    // 自动保存逻辑
    bool shouldAutoSave() const;
    void triggerAutoSaveIfNeeded();
    
    // 数据验证
    bool validateCheckpoint(const QuickCheckpoint& checkpoint) const;
    bool validateProgress(const ScanProgress& progress) const;
    
    // 从检查点重构进度
    ScanProgress reconstructProgressFromCheckpoint(const QuickCheckpoint& checkpoint) const;
    
    // 错误处理
    void logError(const std::string& operation, const std::string& error) const;
    void logInfo(const std::string& message) const;
};

/**
 * 进度管理器的便利工厂函数
 * 自动检测环境并创建合适的管理器实例
 */
std::unique_ptr<ScanProgressManager> createProgressManager(const std::string& environment_name = "");

} // namespace progress
} // namespace linch_connector