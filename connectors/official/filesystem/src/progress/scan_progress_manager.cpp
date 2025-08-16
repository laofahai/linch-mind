#include "scan_progress_manager.hpp"
#include <iostream>
#include <iomanip>
#include <sstream>
#include <random>
#include <cstdlib>
#include <algorithm>

#ifdef __APPLE__
#include <pwd.h>
#include <unistd.h>
#endif

namespace linch_connector {
namespace progress {

ScanProgressManager::ScanProgressManager(const std::string& environment_name)
    : m_environment_name(environment_name.empty() ? "development" : environment_name) {
    
    // 初始化路径
    m_progress_dir = getUserDataDirectory() / m_environment_name / "filesystem";
    
    // 设置默认的上次保存时间
    m_last_save_time.store(std::chrono::system_clock::now());
    
    logInfo("ScanProgressManager created for environment: " + m_environment_name);
}

ScanProgressManager::~ScanProgressManager() {
    if (m_initialized.load()) {
        // 析构时保存最终状态
        saveCheckpoint();
        saveDetailedProgress();
        logInfo("ScanProgressManager destroyed, final state saved");
    }
}

bool ScanProgressManager::initialize(const zero_scan::ScanConfiguration& config, 
                                   const SaveOptions& save_options) {
    std::lock_guard<std::mutex> lock(m_mutex);
    
    if (m_initialized.load()) {
        logInfo("ScanProgressManager already initialized");
        return true;
    }
    
    // 保存配置
    m_last_config = config;
    m_save_options = save_options;
    
    // 确保目录存在
    if (!ensureProgressDirectory()) {
        logError("initialize", "Failed to create progress directory");
        return false;
    }
    
    // 设置文件路径
    m_checkpoint_path = m_progress_dir / m_save_options.checkpoint_filename;
    m_progress_path = m_progress_dir / m_save_options.progress_filename;
    m_config_hash_path = m_progress_dir / m_save_options.config_hash_filename;
    
    m_initialized.store(true);
    
    logInfo("ScanProgressManager initialized successfully");
    logInfo("Progress directory: " + m_progress_dir.string());
    
    return true;
}

std::string ScanProgressManager::startNewSession(const std::string& scan_type,
                                                const std::vector<std::string>& query_types_order) {
    std::lock_guard<std::mutex> lock(m_mutex);
    
    if (!m_initialized.load()) {
        logError("startNewSession", "Manager not initialized");
        return "";
    }
    
    // 生成新的会话ID
    std::string session_id = generateSessionId();
    
    // 重置进度状态
    m_current_progress = ScanProgress{};
    m_current_progress.session.session_id = session_id;
    m_current_progress.session.start_time = std::chrono::system_clock::now();
    m_current_progress.session.scan_type = scan_type;
    m_current_progress.session.completed = false;
    
    m_current_progress.query_types_order = query_types_order;
    m_current_progress.total_batches = query_types_order.size();
    
    // 立即保存初始状态
    saveCheckpoint();
    
    logInfo("Started new " + scan_type + " session: " + session_id);
    logInfo("Query types order: [" + 
            std::accumulate(query_types_order.begin(), query_types_order.end(), std::string{},
                          [](const std::string& a, const std::string& b) {
                              return a.empty() ? b : a + ", " + b;
                          }) + "]");
    
    return session_id;
}

std::optional<ScanProgress> ScanProgressManager::tryResumeFromCheckpoint(const ResumeOptions& resume_options) {
    std::lock_guard<std::mutex> lock(m_mutex);
    
    if (!m_initialized.load()) {
        logError("tryResumeFromCheckpoint", "Manager not initialized");
        return std::nullopt;
    }
    
    // 检查是否有检查点文件
    if (!std::filesystem::exists(m_checkpoint_path)) {
        logInfo("No checkpoint file found, cannot resume");
        return std::nullopt;
    }
    
    // 加载快速检查点
    nlohmann::json checkpoint_json;
    if (!loadJsonFromFile(m_checkpoint_path, checkpoint_json)) {
        logError("tryResumeFromCheckpoint", "Failed to load checkpoint file");
        return std::nullopt;
    }
    
    QuickCheckpoint checkpoint;
    if (!deserializeCheckpoint(checkpoint_json, checkpoint)) {
        logError("tryResumeFromCheckpoint", "Failed to deserialize checkpoint");
        return std::nullopt;
    }
    
    // 验证检查点
    if (!validateCheckpoint(checkpoint)) {
        logError("tryResumeFromCheckpoint", "Invalid checkpoint data");
        return std::nullopt;
    }
    
    // 检查检查点年龄
    auto checkpoint_age = std::chrono::system_clock::now() - checkpoint.timestamp;
    if (checkpoint_age > resume_options.max_checkpoint_age) {
        logInfo("Checkpoint too old (" + std::to_string(
                std::chrono::duration_cast<std::chrono::hours>(checkpoint_age).count()) + 
                " hours), cannot resume");
        if (!resume_options.force_resume) {
            return std::nullopt;
        }
        logInfo("Force resume enabled, ignoring checkpoint age");
    }
    
    // 如果扫描已完成，不需要恢复
    if (checkpoint.scan_completed) {
        logInfo("Previous scan already completed, no need to resume");
        return std::nullopt;
    }
    
    // 尝试加载详细进度
    ScanProgress progress;
    if (std::filesystem::exists(m_progress_path)) {
        nlohmann::json progress_json;
        if (loadJsonFromFile(m_progress_path, progress_json)) {
            if (deserializeProgress(progress_json, progress)) {
                logInfo("Loaded detailed progress from file");
            } else {
                logInfo("Failed to load detailed progress, using checkpoint only");
                // 从检查点重构基本进度
                progress = reconstructProgressFromCheckpoint(checkpoint);
            }
        } else {
            logInfo("Failed to read detailed progress file, using checkpoint only");
            progress = reconstructProgressFromCheckpoint(checkpoint);
        }
    } else {
        logInfo("No detailed progress file found, using checkpoint only");
        progress = reconstructProgressFromCheckpoint(checkpoint);
    }
    
    // 验证和设置当前进度
    if (validateProgress(progress)) {
        m_current_progress = progress;
        logInfo("Successfully resumed from checkpoint");
        logInfo("Session ID: " + checkpoint.session_id);
        logInfo("Current batch: " + std::to_string(checkpoint.current_batch_index));
        logInfo("Current query: " + checkpoint.current_query_type);
        logInfo("Files processed: " + std::to_string(checkpoint.total_files_processed));
        return progress;
    } else {
        logError("tryResumeFromCheckpoint", "Loaded progress data is invalid");
        return std::nullopt;
    }
}

bool ScanProgressManager::hasValidCheckpoint() const {
    std::lock_guard<std::mutex> lock(m_mutex);
    
    if (!m_initialized.load() || !std::filesystem::exists(m_checkpoint_path)) {
        return false;
    }
    
    // 快速检查：尝试加载并验证检查点
    nlohmann::json checkpoint_json;
    if (!loadJsonFromFile(m_checkpoint_path, checkpoint_json)) {
        return false;
    }
    
    QuickCheckpoint checkpoint;
    if (!deserializeCheckpoint(checkpoint_json, checkpoint)) {
        return false;
    }
    
    // 检查是否已完成
    if (checkpoint.scan_completed) {
        return false;
    }
    
    // 检查年龄 (使用默认的24小时限制)
    auto checkpoint_age = std::chrono::system_clock::now() - checkpoint.timestamp;
    if (checkpoint_age > std::chrono::hours{24}) {
        return false;
    }
    
    return validateCheckpoint(checkpoint);
}

void ScanProgressManager::startBatch(size_t batch_index, const std::string& query_type, const std::string& query_string) {
    std::lock_guard<std::mutex> lock(m_mutex);
    
    if (!m_initialized.load()) {
        logError("startBatch", "Manager not initialized");
        return;
    }
    
    // 更新当前进度
    m_current_progress.current_batch_index = batch_index;
    m_current_progress.current_query_type = query_type;
    
    // 创建新的批次进度
    BatchProgress batch;
    batch.batch_index = batch_index;
    batch.query_type = query_type;
    batch.query_string = query_string;
    batch.start_time = std::chrono::system_clock::now();
    batch.completed = false;
    
    // 添加到当前批次（替换如果已存在）
    auto it = std::find_if(m_current_progress.completed_batches.begin(),
                          m_current_progress.completed_batches.end(),
                          [batch_index](const BatchProgress& b) { return b.batch_index == batch_index; });
    
    if (it != m_current_progress.completed_batches.end()) {
        *it = batch;  // 替换现有批次（重试场景）
    } else {
        m_current_progress.completed_batches.push_back(batch);
    }
    
    logInfo("Started batch " + std::to_string(batch_index) + " (" + query_type + ")");
    
    // 触发自动保存
    triggerAutoSaveIfNeeded();
}

void ScanProgressManager::updateBatchProgress(size_t files_processed, size_t files_found) {
    std::lock_guard<std::mutex> lock(m_mutex);
    
    if (!m_initialized.load()) {
        return;
    }
    
    // 更新当前批次的进度
    auto& batches = m_current_progress.completed_batches;
    if (!batches.empty()) {
        auto& current_batch = batches.back();
        current_batch.files_processed = files_processed;
        current_batch.files_found = files_found;
    }
    
    // 更新总统计
    updateStatistics();
    updateEstimatedTime();
    
    // 触发自动保存
    triggerAutoSaveIfNeeded();
}

void ScanProgressManager::completeBatch(double cpu_usage_peak, size_t memory_usage_peak) {
    std::lock_guard<std::mutex> lock(m_mutex);
    
    if (!m_initialized.load()) {
        return;
    }
    
    auto& batches = m_current_progress.completed_batches;
    if (!batches.empty()) {
        auto& current_batch = batches.back();
        current_batch.completed = true;
        current_batch.end_time = std::chrono::system_clock::now();
        current_batch.cpu_usage_peak = cpu_usage_peak;
        current_batch.memory_usage_peak = memory_usage_peak;
        
        // 添加到已完成查询集合
        m_current_progress.completed_queries.insert(current_batch.query_type);
        
        logInfo("Completed batch " + std::to_string(current_batch.batch_index) + 
                " (" + current_batch.query_type + ")");
        logInfo("Files processed: " + std::to_string(current_batch.files_processed) + 
                ", found: " + std::to_string(current_batch.files_found));
        
        if (cpu_usage_peak > 0) {
            logInfo("Peak CPU: " + std::to_string(cpu_usage_peak) + "%");
        }
        if (memory_usage_peak > 0) {
            logInfo("Peak Memory: " + std::to_string(memory_usage_peak) + " MB");
        }
    }
    
    // 更新统计
    updateStatistics();
    
    // 立即保存检查点
    saveCheckpoint();
    
    // 定期保存详细进度
    if (m_current_progress.completed_batches.size() % m_save_options.batch_save_frequency == 0) {
        saveDetailedProgress();
    }
}

void ScanProgressManager::completeSession() {
    std::lock_guard<std::mutex> lock(m_mutex);
    
    if (!m_initialized.load()) {
        return;
    }
    
    m_current_progress.session.completed = true;
    m_current_progress.session.end_time = std::chrono::system_clock::now();
    
    auto duration = m_current_progress.session.end_time - m_current_progress.session.start_time;
    auto duration_ms = std::chrono::duration_cast<std::chrono::milliseconds>(duration).count();
    
    logInfo("Session completed: " + m_current_progress.session.session_id);
    logInfo("Total duration: " + std::to_string(duration_ms) + " ms");
    logInfo("Total files processed: " + std::to_string(m_current_progress.total_files_processed));
    logInfo("Total batches: " + std::to_string(m_current_progress.completed_batches.size()));
    
    // 保存最终状态
    saveCheckpoint();
    saveDetailedProgress();
}

void ScanProgressManager::recordError(const std::string& error_message) {
    std::lock_guard<std::mutex> lock(m_mutex);
    
    if (!m_initialized.load()) {
        return;
    }
    
    m_current_progress.session.error_message = error_message;
    logError("recordError", error_message);
    
    // 立即保存错误状态
    saveCheckpoint();
}

// === 查询接口实现 ===

double ScanProgressManager::getCompletionPercentage() const {
    std::lock_guard<std::mutex> lock(m_mutex);
    
    if (m_current_progress.total_batches == 0) {
        return 0.0;
    }
    
    size_t completed_batches = 0;
    for (const auto& batch : m_current_progress.completed_batches) {
        if (batch.completed) {
            completed_batches++;
        }
    }
    
    return static_cast<double>(completed_batches) / static_cast<double>(m_current_progress.total_batches);
}

uint64_t ScanProgressManager::getEstimatedRemainingTime() const {
    std::lock_guard<std::mutex> lock(m_mutex);
    return m_current_progress.estimated_remaining_time_ms;
}

bool ScanProgressManager::shouldSkipQueryType(const std::string& query_type) const {
    std::lock_guard<std::mutex> lock(m_mutex);
    return m_current_progress.completed_queries.find(query_type) != m_current_progress.completed_queries.end();
}

size_t ScanProgressManager::getNextBatchIndex() const {
    std::lock_guard<std::mutex> lock(m_mutex);
    return m_current_progress.current_batch_index;
}

// === 保存/加载实现 ===

bool ScanProgressManager::saveCheckpoint() {
    if (!m_initialized.load()) {
        return false;
    }
    
    // 创建快速检查点
    QuickCheckpoint checkpoint;
    checkpoint.session_id = m_current_progress.session.session_id;
    checkpoint.current_batch_index = m_current_progress.current_batch_index;
    checkpoint.current_query_type = m_current_progress.current_query_type;
    checkpoint.total_files_processed = m_current_progress.total_files_processed;
    checkpoint.timestamp = std::chrono::system_clock::now();
    checkpoint.scan_completed = m_current_progress.session.completed;
    
    // 转换已完成的查询类型
    checkpoint.completed_query_types.reserve(m_current_progress.completed_queries.size());
    for (const auto& query_type : m_current_progress.completed_queries) {
        checkpoint.completed_query_types.push_back(query_type);
    }
    
    // 序列化并保存
    nlohmann::json json = serializeCheckpoint(checkpoint);
    bool success = saveJsonToFile(json, m_checkpoint_path);
    
    if (success) {
        m_checkpoint_save_count.fetch_add(1);
        m_last_save_time.store(checkpoint.timestamp);
        // logInfo("Checkpoint saved successfully");
    } else {
        logError("saveCheckpoint", "Failed to save checkpoint");
    }
    
    return success;
}

bool ScanProgressManager::saveDetailedProgress() {
    if (!m_initialized.load()) {
        return false;
    }
    
    nlohmann::json json = serializeProgress(m_current_progress);
    bool success = saveJsonToFile(json, m_progress_path);
    
    if (success) {
        m_progress_save_count.fetch_add(1);
        logInfo("Detailed progress saved successfully");
    } else {
        logError("saveDetailedProgress", "Failed to save detailed progress");
    }
    
    return success;
}

void ScanProgressManager::clearAllProgress() {
    std::lock_guard<std::mutex> lock(m_mutex);
    
    // 删除所有进度文件
    try {
        if (std::filesystem::exists(m_checkpoint_path)) {
            std::filesystem::remove(m_checkpoint_path);
        }
        if (std::filesystem::exists(m_progress_path)) {
            std::filesystem::remove(m_progress_path);
        }
        if (std::filesystem::exists(m_config_hash_path)) {
            std::filesystem::remove(m_config_hash_path);
        }
        
        logInfo("All progress data cleared");
    } catch (const std::exception& e) {
        logError("clearAllProgress", "Failed to clear progress files: " + std::string(e.what()));
    }
    
    // 重置内存状态
    m_current_progress = ScanProgress{};
}

// === 时间和统计 ===

std::string ScanProgressManager::generateSessionId() const {
    // 生成基于时间戳和随机数的会话ID
    auto now = std::chrono::system_clock::now();
    auto timestamp = std::chrono::duration_cast<std::chrono::milliseconds>(now.time_since_epoch()).count();
    
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<> dis(1000, 9999);
    
    std::stringstream ss;
    ss << "scan_" << timestamp << "_" << dis(gen);
    return ss.str();
}

void ScanProgressManager::updateStatistics() {
    // 计算总文件数和处理进度
    m_current_progress.total_files_processed = 0;
    m_current_progress.total_files_found = 0;
    
    double total_cpu = 0.0;
    size_t cpu_samples = 0;
    
    for (const auto& batch : m_current_progress.completed_batches) {
        m_current_progress.total_files_processed += batch.files_processed;
        m_current_progress.total_files_found += batch.files_found;
        
        if (batch.cpu_usage_peak > 0) {
            total_cpu += batch.cpu_usage_peak;
            cpu_samples++;
        }
        
        if (batch.memory_usage_peak > m_current_progress.peak_memory_usage) {
            m_current_progress.peak_memory_usage = batch.memory_usage_peak;
        }
    }
    
    // 计算平均CPU使用率
    if (cpu_samples > 0) {
        m_current_progress.average_cpu_usage = total_cpu / cpu_samples;
    }
}

void ScanProgressManager::updateEstimatedTime() {
    if (m_current_progress.completed_batches.empty()) {
        m_current_progress.estimated_remaining_time_ms = 0;
        return;
    }
    
    // 计算已完成批次的平均耗时
    uint64_t total_duration_ms = 0;
    size_t completed_count = 0;
    
    for (const auto& batch : m_current_progress.completed_batches) {
        if (batch.completed) {
            auto duration = batch.end_time - batch.start_time;
            total_duration_ms += std::chrono::duration_cast<std::chrono::milliseconds>(duration).count();
            completed_count++;
        }
    }
    
    if (completed_count > 0 && m_current_progress.total_batches > completed_count) {
        uint64_t avg_duration_ms = total_duration_ms / completed_count;
        size_t remaining_batches = m_current_progress.total_batches - completed_count;
        m_current_progress.estimated_remaining_time_ms = avg_duration_ms * remaining_batches;
    } else {
        m_current_progress.estimated_remaining_time_ms = 0;
    }
}

// === 自动保存逻辑 ===

bool ScanProgressManager::shouldAutoSave() const {
    auto now = std::chrono::system_clock::now();
    auto last_save = m_last_save_time.load();
    auto time_since_save = now - last_save;
    
    return time_since_save >= m_save_options.checkpoint_interval;
}

void ScanProgressManager::triggerAutoSaveIfNeeded() {
    if (shouldAutoSave()) {
        saveCheckpoint();
    }
}

// === 数据验证 ===

bool ScanProgressManager::validateCheckpoint(const QuickCheckpoint& checkpoint) const {
    // 基本验证
    if (checkpoint.session_id.empty()) {
        return false;
    }
    
    // 时间验证
    auto now = std::chrono::system_clock::now();
    if (checkpoint.timestamp > now) {
        return false;  // 未来时间无效
    }
    
    return true;
}

bool ScanProgressManager::validateProgress(const ScanProgress& progress) const {
    // 基本验证
    if (progress.session.session_id.empty()) {
        return false;
    }
    
    // 批次数量验证
    if (progress.current_batch_index > progress.total_batches) {
        return false;
    }
    
    // 查询类型验证
    if (!progress.current_query_type.empty()) {
        bool found = std::find(progress.query_types_order.begin(), 
                              progress.query_types_order.end(),
                              progress.current_query_type) != progress.query_types_order.end();
        if (!found) {
            return false;
        }
    }
    
    return true;
}

// === 从检查点重构进度 ===

ScanProgress ScanProgressManager::reconstructProgressFromCheckpoint(const QuickCheckpoint& checkpoint) const {
    ScanProgress progress;
    
    // 基本会话信息
    progress.session.session_id = checkpoint.session_id;
    progress.session.scan_type = "resumed";
    progress.session.start_time = checkpoint.timestamp;  // 使用检查点时间作为近似
    progress.session.completed = checkpoint.scan_completed;
    
    // 当前进度
    progress.current_batch_index = checkpoint.current_batch_index;
    progress.current_query_type = checkpoint.current_query_type;
    progress.total_files_processed = checkpoint.total_files_processed;
    
    // 已完成的查询类型
    for (const auto& query_type : checkpoint.completed_query_types) {
        progress.completed_queries.insert(query_type);
    }
    
    // 设置检查点时间
    progress.last_checkpoint = checkpoint.timestamp;
    
    return progress;
}

// === 错误处理和日志 ===

void ScanProgressManager::logError(const std::string& operation, const std::string& error) const {
    std::cerr << "❌ [ScanProgressManager::" << operation << "] " << error << std::endl;
}

void ScanProgressManager::logInfo(const std::string& message) const {
    std::cout << "ℹ️  [ScanProgressManager] " << message << std::endl;
}

// === 工厂函数 ===

std::unique_ptr<ScanProgressManager> createProgressManager(const std::string& environment_name) {
    std::string env = environment_name;
    if (env.empty()) {
        // 自动检测环境
        const char* env_var = getenv("LINCH_MIND_ENV");
        if (env_var) {
            env = env_var;
        } else {
            env = "development";  // 默认环境
        }
    }
    
    return std::make_unique<ScanProgressManager>(env);
}

// === 配置和环境管理实现 ===

bool ScanProgressManager::hasConfigurationChanged(const zero_scan::ScanConfiguration& current_config) const {
    std::lock_guard<std::mutex> lock(m_mutex);
    
    if (!m_initialized.load()) {
        return true;  // 如果未初始化，认为配置有变化
    }
    
    // 计算当前配置的哈希
    std::string current_hash = calculateConfigHash(current_config);
    
    // 加载保存的配置哈希
    std::string saved_hash = loadConfigHash();
    
    return current_hash != saved_hash;
}

std::filesystem::path ScanProgressManager::getProgressDirectory() const {
    return m_progress_dir;
}

// === 内部实现方法 ===

bool ScanProgressManager::ensureProgressDirectory() {
    try {
        if (!std::filesystem::exists(m_progress_dir)) {
            std::filesystem::create_directories(m_progress_dir);
            logInfo("Created progress directory: " + m_progress_dir.string());
        }
        return true;
    } catch (const std::exception& e) {
        logError("ensureProgressDirectory", "Failed to create directory: " + std::string(e.what()));
        return false;
    }
}

std::filesystem::path ScanProgressManager::getUserDataDirectory() const {
    // 获取用户主目录
    std::filesystem::path home_dir;
    
#ifdef __APPLE__
    const char* home = getenv("HOME");
    if (home) {
        home_dir = home;
    } else {
        struct passwd* pw = getpwuid(getuid());
        if (pw) {
            home_dir = pw->pw_dir;
        } else {
            home_dir = "/tmp";  // 回退方案
        }
    }
#else
    const char* home = getenv("HOME");
    if (home) {
        home_dir = home;
    } else {
        home_dir = "/tmp";  // 回退方案
    }
#endif
    
    return home_dir / ".linch-mind";
}

// === JSON序列化/反序列化 ===

nlohmann::json ScanProgressManager::serializeCheckpoint(const QuickCheckpoint& checkpoint) const {
    nlohmann::json json;
    
    json["version"] = "1.0";
    json["session_id"] = checkpoint.session_id;
    json["current_batch_index"] = checkpoint.current_batch_index;
    json["current_query_type"] = checkpoint.current_query_type;
    json["total_files_processed"] = checkpoint.total_files_processed;
    json["scan_completed"] = checkpoint.scan_completed;
    json["completed_query_types"] = checkpoint.completed_query_types;
    
    // 时间戳转换
    auto timestamp_ms = std::chrono::duration_cast<std::chrono::milliseconds>(
        checkpoint.timestamp.time_since_epoch()).count();
    json["timestamp_ms"] = timestamp_ms;
    
    return json;
}

nlohmann::json ScanProgressManager::serializeProgress(const ScanProgress& progress) const {
    nlohmann::json json;
    
    json["version"] = "1.0";
    
    // 会话信息
    auto& session_json = json["session"];
    session_json["session_id"] = progress.session.session_id;
    session_json["scan_type"] = progress.session.scan_type;
    session_json["completed"] = progress.session.completed;
    session_json["error_message"] = progress.session.error_message;
    
    auto start_ms = std::chrono::duration_cast<std::chrono::milliseconds>(
        progress.session.start_time.time_since_epoch()).count();
    session_json["start_time_ms"] = start_ms;
    
    if (progress.session.completed) {
        auto end_ms = std::chrono::duration_cast<std::chrono::milliseconds>(
            progress.session.end_time.time_since_epoch()).count();
        session_json["end_time_ms"] = end_ms;
    }
    
    // 当前进度
    json["current_batch_index"] = progress.current_batch_index;
    json["current_query_type"] = progress.current_query_type;
    json["total_batches"] = progress.total_batches;
    json["query_types_order"] = progress.query_types_order;
    
    // 统计信息
    json["total_files_processed"] = progress.total_files_processed;
    json["total_files_found"] = progress.total_files_found;
    json["average_cpu_usage"] = progress.average_cpu_usage;
    json["peak_memory_usage"] = progress.peak_memory_usage;
    json["estimated_remaining_time_ms"] = progress.estimated_remaining_time_ms;
    json["system_load_warning"] = progress.system_load_warning;
    
    // 已完成的查询类型
    json["completed_queries"] = std::vector<std::string>(
        progress.completed_queries.begin(), progress.completed_queries.end());
    
    // 批次历史（限制数量以避免文件过大）
    auto& batches_json = json["completed_batches"];
    size_t batch_limit = std::min(progress.completed_batches.size(), m_save_options.max_batch_history);
    
    for (size_t i = progress.completed_batches.size() - batch_limit; i < progress.completed_batches.size(); ++i) {
        const auto& batch = progress.completed_batches[i];
        nlohmann::json batch_json;
        batch_json["batch_index"] = batch.batch_index;
        batch_json["query_type"] = batch.query_type;
        batch_json["query_string"] = batch.query_string;
        batch_json["files_processed"] = batch.files_processed;
        batch_json["files_found"] = batch.files_found;
        batch_json["completed"] = batch.completed;
        batch_json["cpu_usage_peak"] = batch.cpu_usage_peak;
        batch_json["memory_usage_peak"] = batch.memory_usage_peak;
        
        auto batch_start_ms = std::chrono::duration_cast<std::chrono::milliseconds>(
            batch.start_time.time_since_epoch()).count();
        batch_json["start_time_ms"] = batch_start_ms;
        
        if (batch.completed) {
            auto batch_end_ms = std::chrono::duration_cast<std::chrono::milliseconds>(
                batch.end_time.time_since_epoch()).count();
            batch_json["end_time_ms"] = batch_end_ms;
        }
        
        batches_json.push_back(batch_json);
    }
    
    return json;
}

nlohmann::json ScanProgressManager::serializeConfig(const zero_scan::ScanConfiguration& config) const {
    nlohmann::json json;
    
    json["include_paths"] = config.include_paths;
    json["exclude_paths"] = config.exclude_paths;
    json["exclude_patterns"] = config.exclude_patterns;
    json["batch_size"] = config.batch_size;
    json["max_results"] = config.max_results;
    json["timeout_ms"] = config.timeout.count();
    json["include_hidden"] = config.include_hidden;
    json["include_system"] = config.include_system;
    json["directories_only"] = config.directories_only;
    json["files_only"] = config.files_only;
    json["use_cache"] = config.use_cache;
    json["parallel_processing"] = config.parallel_processing;
    json["thread_count"] = config.thread_count;
    
    return json;
}

// 继续添加反序列化和文件I/O方法...
bool ScanProgressManager::deserializeCheckpoint(const nlohmann::json& json, QuickCheckpoint& checkpoint) const {
    try {
        if (!json.contains("version") || json["version"] != "1.0") {
            logError("deserializeCheckpoint", "Unsupported checkpoint version");
            return false;
        }
        
        checkpoint.session_id = json["session_id"];
        checkpoint.current_batch_index = json["current_batch_index"];
        checkpoint.current_query_type = json["current_query_type"];
        checkpoint.total_files_processed = json["total_files_processed"];
        checkpoint.scan_completed = json["scan_completed"];
        checkpoint.completed_query_types = json["completed_query_types"];
        
        // 时间戳转换
        int64_t timestamp_ms = json["timestamp_ms"];
        checkpoint.timestamp = std::chrono::system_clock::time_point{
            std::chrono::milliseconds{timestamp_ms}
        };
        
        return true;
    } catch (const std::exception& e) {
        logError("deserializeCheckpoint", "Failed to deserialize: " + std::string(e.what()));
        return false;
    }
}

bool ScanProgressManager::deserializeProgress(const nlohmann::json& json, ScanProgress& progress) const {
    try {
        if (!json.contains("version") || json["version"] != "1.0") {
            logError("deserializeProgress", "Unsupported progress version");
            return false;
        }
        
        // 会话信息
        const auto& session_json = json["session"];
        progress.session.session_id = session_json["session_id"];
        progress.session.scan_type = session_json["scan_type"];
        progress.session.completed = session_json["completed"];
        progress.session.error_message = session_json["error_message"];
        
        int64_t start_ms = session_json["start_time_ms"];
        progress.session.start_time = std::chrono::system_clock::time_point{
            std::chrono::milliseconds{start_ms}
        };
        
        if (progress.session.completed && session_json.contains("end_time_ms")) {
            int64_t end_ms = session_json["end_time_ms"];
            progress.session.end_time = std::chrono::system_clock::time_point{
                std::chrono::milliseconds{end_ms}
            };
        }
        
        // 当前进度和统计信息
        progress.current_batch_index = json["current_batch_index"];
        progress.current_query_type = json["current_query_type"];
        progress.total_batches = json["total_batches"];
        progress.query_types_order = json["query_types_order"];
        progress.total_files_processed = json["total_files_processed"];
        progress.total_files_found = json["total_files_found"];
        progress.average_cpu_usage = json["average_cpu_usage"];
        progress.peak_memory_usage = json["peak_memory_usage"];
        progress.estimated_remaining_time_ms = json["estimated_remaining_time_ms"];
        progress.system_load_warning = json["system_load_warning"];
        
        // 已完成的查询类型
        std::vector<std::string> completed_queries_vec = json["completed_queries"];
        progress.completed_queries.clear();
        for (const auto& query : completed_queries_vec) {
            progress.completed_queries.insert(query);
        }
        
        return true;
    } catch (const std::exception& e) {
        logError("deserializeProgress", "Failed to deserialize: " + std::string(e.what()));
        return false;
    }
}

bool ScanProgressManager::deserializeConfig(const nlohmann::json& json, zero_scan::ScanConfiguration& config) const {
    try {
        config.include_paths = json["include_paths"];
        config.exclude_paths = json["exclude_paths"];
        config.exclude_patterns = json["exclude_patterns"];
        config.batch_size = json["batch_size"];
        config.max_results = json["max_results"];
        config.timeout = std::chrono::milliseconds{json["timeout_ms"]};
        config.include_hidden = json["include_hidden"];
        config.include_system = json["include_system"];
        config.directories_only = json["directories_only"];
        config.files_only = json["files_only"];
        config.use_cache = json["use_cache"];
        config.parallel_processing = json["parallel_processing"];
        config.thread_count = json["thread_count"];
        
        return true;
    } catch (const std::exception& e) {
        logError("deserializeConfig", "Failed to deserialize: " + std::string(e.what()));
        return false;
    }
}

// === 文件I/O操作 ===

bool ScanProgressManager::saveJsonToFile(const nlohmann::json& json, const std::filesystem::path& file_path) const {
    try {
        // 使用临时文件确保原子性
        std::filesystem::path temp_path = file_path;
        temp_path += ".tmp";
        
        // 写入临时文件
        {
            std::ofstream file(temp_path);
            if (!file.is_open()) {
                logError("saveJsonToFile", "Failed to open temporary file: " + temp_path.string());
                return false;
            }
            
            file << json.dump(2);  // 格式化JSON，便于调试
            
            if (!file.good()) {
                logError("saveJsonToFile", "Failed to write to temporary file");
                return false;
            }
        }
        
        // 原子性重命名
        std::filesystem::rename(temp_path, file_path);
        
        return true;
    } catch (const std::exception& e) {
        logError("saveJsonToFile", "Exception: " + std::string(e.what()));
        return false;
    }
}

bool ScanProgressManager::loadJsonFromFile(const std::filesystem::path& file_path, nlohmann::json& json) const {
    try {
        if (!std::filesystem::exists(file_path)) {
            return false;
        }
        
        std::ifstream file(file_path);
        if (!file.is_open()) {
            logError("loadJsonFromFile", "Failed to open file: " + file_path.string());
            return false;
        }
        
        file >> json;
        
        if (!file.good() && !file.eof()) {
            logError("loadJsonFromFile", "Failed to read JSON from file");
            return false;
        }
        
        return true;
    } catch (const std::exception& e) {
        logError("loadJsonFromFile", "Exception: " + std::string(e.what()));
        return false;
    }
}

// === 配置管理 ===

std::string ScanProgressManager::calculateConfigHash(const zero_scan::ScanConfiguration& config) const {
    std::stringstream ss;
    
    for (const auto& path : config.include_paths) {
        ss << "inc:" << path << ";";
    }
    for (const auto& path : config.exclude_paths) {
        ss << "exc:" << path << ";";
    }
    for (const auto& pattern : config.exclude_patterns) {
        ss << "pat:" << pattern << ";";
    }
    
    ss << "batch:" << config.batch_size << ";";
    ss << "max:" << config.max_results << ";";
    ss << "hidden:" << config.include_hidden << ";";
    ss << "system:" << config.include_system << ";";
    
    std::string config_str = ss.str();
    std::hash<std::string> hasher;
    size_t hash_value = hasher(config_str);
    
    std::stringstream hash_ss;
    hash_ss << std::hex << hash_value;
    return hash_ss.str();
}

bool ScanProgressManager::saveConfigHash(const std::string& hash) const {
    nlohmann::json json;
    json["config_hash"] = hash;
    json["timestamp_ms"] = std::chrono::duration_cast<std::chrono::milliseconds>(
        std::chrono::system_clock::now().time_since_epoch()).count();
    
    return saveJsonToFile(json, m_config_hash_path);
}

std::string ScanProgressManager::loadConfigHash() const {
    nlohmann::json json;
    if (!loadJsonFromFile(m_config_hash_path, json)) {
        return "";
    }
    
    try {
        return json["config_hash"];
    } catch (const std::exception&) {
        return "";
    }
}

} // namespace progress
} // namespace linch_connector