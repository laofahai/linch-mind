#pragma once

#include <string>
#include <vector>
#include <chrono>
#include <optional>
#include <unordered_set>

namespace linch_connector {
namespace progress {

/**
 * 扫描会话信息
 * 标识一次完整的扫描过程
 */
struct ScanSession {
    std::string session_id;                           // 唯一会话ID (UUID)
    std::chrono::system_clock::time_point start_time; // 会话开始时间
    std::chrono::system_clock::time_point end_time;   // 会话结束时间 (可选)
    std::string scan_type;                            // "full" | "incremental" | "resume"
    bool completed = false;                           // 是否完成
    std::string error_message;                        // 错误信息 (如果有)
};

/**
 * 批次进度信息
 * 记录每个查询批次的执行状态
 */
struct BatchProgress {
    size_t batch_index = 0;                          // 批次索引
    std::string query_type;                          // 查询类型 ("documents", "images", etc.)
    std::string query_string;                        // MDQuery查询字符串
    size_t files_processed = 0;                      // 已处理文件数
    size_t files_found = 0;                          // 发现的文件总数
    std::chrono::system_clock::time_point start_time; // 批次开始时间
    std::chrono::system_clock::time_point end_time;   // 批次结束时间 (可选)
    bool completed = false;                           // 是否完成
    double cpu_usage_peak = 0.0;                     // 峰值CPU使用率
    size_t memory_usage_peak = 0;                     // 峰值内存使用 (MB)
};

/**
 * 扫描进度状态
 * 包含完整的进度信息
 */
struct ScanProgress {
    // 会话信息
    ScanSession session;
    
    // 当前进度
    size_t current_batch_index = 0;                  // 当前批次索引
    std::string current_query_type;                  // 当前查询类型
    size_t total_batches = 0;                        // 总批次数
    
    // 统计信息
    size_t total_files_processed = 0;                // 总已处理文件数
    size_t total_files_found = 0;                    // 总发现文件数
    std::vector<std::string> query_types_order;      // 查询类型顺序
    
    // 批次历史
    std::vector<BatchProgress> completed_batches;    // 已完成的批次
    std::unordered_set<std::string> completed_queries; // 已完成的查询类型
    
    // 性能指标
    double average_cpu_usage = 0.0;                  // 平均CPU使用率
    size_t peak_memory_usage = 0;                    // 峰值内存使用
    uint64_t estimated_remaining_time_ms = 0;        // 预估剩余时间
    
    // 系统状态
    bool system_load_warning = false;                // 系统负载警告
    std::chrono::system_clock::time_point last_checkpoint; // 最后检查点时间
};

/**
 * 快速检查点数据
 * 用于JSON快速保存/加载
 */
struct QuickCheckpoint {
    std::string session_id;                          // 会话ID
    size_t current_batch_index = 0;                  // 当前批次
    std::string current_query_type;                  // 当前查询类型
    size_t total_files_processed = 0;                // 总已处理文件数
    std::chrono::system_clock::time_point timestamp; // 检查点时间
    bool scan_completed = false;                     // 扫描是否完成
    std::vector<std::string> completed_query_types;  // 已完成的查询类型
};

/**
 * 进度恢复选项
 * 控制从检查点恢复的行为
 */
struct ResumeOptions {
    bool force_resume = false;                       // 强制恢复 (即使有警告)
    bool skip_completed_batches = true;              // 跳过已完成的批次
    bool validate_file_states = false;               // 验证文件状态 (慢但安全)
    std::chrono::hours max_checkpoint_age{24};       // 最大检查点年龄
    bool reset_on_config_change = true;              // 配置变更时重置
};

/**
 * 进度保存选项
 * 控制进度保存的频率和方式 - 使用轻量级JSON存储
 */
struct SaveOptions {
    std::chrono::seconds checkpoint_interval{30};    // 检查点保存间隔
    size_t batch_save_frequency = 1;                 // 批次保存频率 (每N个批次)
    bool enable_detailed_progress = true;            // 启用详细进度存储
    bool enable_quick_checkpoint = true;             // 启用快速检查点
    size_t max_batch_history = 100;                  // 最大批次历史数量 (减少内存占用)
    
    // JSON存储路径 (相对于 ~/.linch-mind/{env}/filesystem/)
    std::string checkpoint_filename = "scan_checkpoint.json";
    std::string progress_filename = "scan_progress.json";
    std::string config_hash_filename = "scan_config_hash.json";
};

} // namespace progress
} // namespace linch_connector