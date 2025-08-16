#ifdef __APPLE__

#include "macos_file_index_provider.hpp"
#include <iostream>
#include <sstream>
#include <regex>
#include <filesystem>
#include <cstdlib>
#include <sys/stat.h>
#include <unistd.h>

namespace fs = std::filesystem;

namespace linch_connector {

// 默认排除模式
const std::vector<std::string> MacOSFileIndexProvider::DEFAULT_EXCLUDE_PATTERNS = {
    R"(^\..*)",           // 隐藏文件
    R"(.*\.tmp$)",        // 临时文件
    R"(.*\.log$)",        // 日志文件
    R"(.*\.cache$)",      // 缓存文件
    R"(.*/\.git/.*)",     // Git目录
    R"(.*/node_modules/.*)", // Node.js模块
    R"(.*/\.DS_Store$)",  // macOS系统文件
    R"(.*/\.Trash/.*)",   // 废纸篓
    R"(.*/\.Trashes/.*)", // 废纸篓
};

MacOSFileIndexProvider::MacOSFileIndexProvider() {
    m_stats.platform_info = "macOS Spotlight + FSEvents";
    m_excludePatterns = DEFAULT_EXCLUDE_PATTERNS;
    
    // 默认监控用户主目录
    const char* homeDir = getenv("HOME");
    if (homeDir) {
        m_watchDirectories.push_back(std::string(homeDir));
    }
    
    std::cout << "🍎 macOS文件索引提供者初始化" << std::endl;
}

MacOSFileIndexProvider::~MacOSFileIndexProvider() {
    stop();
}

bool MacOSFileIndexProvider::initialize() {
    if (m_initialized) {
        std::cout << "⚠️ 已经初始化过了" << std::endl;
        return true;
    }
    
    if (!isAvailable()) {
        std::cout << "❌ Spotlight索引不可用" << std::endl;
        return false;
    }
    
    std::cout << "🚀 开始初始化Spotlight索引查询..." << std::endl;
    
    // 异步执行初始化，避免阻塞
    m_running = true;
    m_initThread = std::make_unique<std::thread>(&MacOSFileIndexProvider::initializationWorker, this);
    
    return true;
}

bool MacOSFileIndexProvider::watchChanges() {
    if (m_watching) {
        std::cout << "⚠️ 已经在监控文件变更" << std::endl;
        return true;
    }
    
    std::cout << "👀 启动FSEvents文件变更监控..." << std::endl;
    
    // 启动事件处理工作线程
    m_eventThread = std::make_unique<std::thread>(&MacOSFileIndexProvider::eventProcessingWorker, this);
    
    // 启动FSEvents监控
    return startFSEventsMonitoring();
}

void MacOSFileIndexProvider::stop() {
    std::cout << "🛑 停止macOS文件索引提供者" << std::endl;
    
    m_running = false;
    
    // 停止FSEvents
    stopFSEventsMonitoring();
    
    // 通知事件处理线程退出
    {
        std::lock_guard<std::mutex> lock(m_eventQueueMutex);
        m_eventQueueCV.notify_all();
    }
    
    // 等待线程结束
    if (m_initThread && m_initThread->joinable()) {
        m_initThread->join();
    }
    if (m_eventThread && m_eventThread->joinable()) {
        m_eventThread->join();
    }
    if (m_fsEventsThread && m_fsEventsThread->joinable()) {
        m_fsEventsThread->join();
    }
    
    m_initialized = false;
    m_watching = false;
}

IndexStats MacOSFileIndexProvider::getStats() const {
    std::lock_guard<std::mutex> lock(m_statsMutex);
    return m_stats;
}

bool MacOSFileIndexProvider::isAvailable() const {
    return checkSpotlightAvailability();
}

std::string MacOSFileIndexProvider::getPlatformInfo() const {
    return m_stats.platform_info + " | " + getSpotlightStatus();
}

void MacOSFileIndexProvider::setInitialBatchCallback(InitialBatchCallback callback) {
    m_initialBatchCallback = callback;
}

void MacOSFileIndexProvider::setFileEventCallback(FileEventCallback callback) {
    m_fileEventCallback = callback;
}

void MacOSFileIndexProvider::setProgressCallback(ProgressCallback callback) {
    m_progressCallback = callback;
}

void MacOSFileIndexProvider::setWatchDirectories(const std::vector<std::string>& directories) {
    m_watchDirectories = directories;
}

void MacOSFileIndexProvider::setExcludePatterns(const std::vector<std::string>& patterns) {
    m_excludePatterns = patterns;
}

// ========== 私有方法实现 ==========

void MacOSFileIndexProvider::initializationWorker() {
    std::cout << "🔍 后台线程开始查询Spotlight索引..." << std::endl;
    
    try {
        if (querySpotlightIndex()) {
            std::lock_guard<std::mutex> lock(m_statsMutex);
            m_stats.is_initialized = true;
            m_initialized = true;
            std::cout << "✅ Spotlight索引查询完成，总文件数: " << m_stats.total_files << std::endl;
        } else {
            std::lock_guard<std::mutex> lock(m_statsMutex);
            m_stats.last_error = "Spotlight索引查询失败";
            std::cout << "❌ Spotlight索引查询失败" << std::endl;
        }
    } catch (const std::exception& e) {
        std::lock_guard<std::mutex> lock(m_statsMutex);
        m_stats.last_error = std::string("初始化异常: ") + e.what();
        std::cout << "❌ 初始化异常: " << e.what() << std::endl;
    }
}

bool MacOSFileIndexProvider::querySpotlightIndex() {
    std::cout << "⚡ 启动 Everything 式零扫描索引..." << std::endl;
    
    // 使用真正的零扫描实现！
    MacOSSpotlightZeroScan zeroScan;
    
    // 配置零扫描选项
    zeroScan.setIncludeSystemFiles(false); // 排除系统文件
    zeroScan.setMaxResults(0); // 无限制，像 Everything 一样！
    
    std::vector<FileInfo> currentBatch;
    currentBatch.reserve(BATCH_SIZE);
    
    // 执行零扫描
    bool success = zeroScan.performInstantScan([this, &currentBatch](const SpotlightFileRecord& record) {
        // 检查是否需要排除
        if (shouldExcludePath(record.path)) {
            return;
        }
        
        // 将 SpotlightFileRecord 转换为 FileInfo
        FileInfo fileInfo;
        fileInfo.path = record.path;
        fileInfo.name = record.name;
        fileInfo.extension = record.extension;
        fileInfo.size = record.size;
        fileInfo.is_directory = record.is_directory;
        fileInfo.modified_time = std::chrono::system_clock::from_time_t(record.modified_time);
        
        currentBatch.push_back(std::move(fileInfo));
        
        // 当批次足够大时发送
        if (currentBatch.size() >= BATCH_SIZE) {
            if (m_initialBatchCallback) {
                m_initialBatchCallback(currentBatch);
            }
            
            {
                std::lock_guard<std::mutex> lock(m_statsMutex);
                m_stats.indexed_files += currentBatch.size();
            }
            
            currentBatch.clear();
            currentBatch.reserve(BATCH_SIZE);
        }
    });
    
    // 发送剩余的文件
    if (!currentBatch.empty()) {
        if (m_initialBatchCallback) {
            m_initialBatchCallback(currentBatch);
        }
        
        std::lock_guard<std::mutex> lock(m_statsMutex);
        m_stats.indexed_files += currentBatch.size();
    }
    
    if (success) {
        auto stats = zeroScan.getStatistics();
        {
            std::lock_guard<std::mutex> lock(m_statsMutex);
            m_stats.total_files = stats.total_files + stats.total_directories;
        }
        
        std::cout << "🎉 零扫描完成！性能数据:" << std::endl;
        std::cout << "   📊 扫描速度: " << stats.files_per_second << " 文件/秒" << std::endl;
        std::cout << "   ⏱️  用时: " << stats.scan_duration_ms << "ms" << std::endl;
        
        if (stats.files_per_second > 10000) {
            std::cout << "   🏆 达到 Everything 级别性能！" << std::endl;
        }
    }
    
    return success;
}

void MacOSFileIndexProvider::parseSpotlightOutput(const std::string& output) {
    std::vector<FileInfo> batch;
    batch.reserve(BATCH_SIZE);
    
    std::istringstream stream(output);
    std::string path;
    uint64_t processedCount = 0;
    
    // 使用NULL分隔符分割路径
    while (std::getline(stream, path, '\0')) {
        if (path.empty()) continue;
        
        // 检查是否需要排除
        if (shouldExcludePath(path)) {
            continue;
        }
        
        // 创建文件信息
        FileInfo fileInfo = createFileInfoFromPath(path);
        if (!fileInfo.path.empty()) {
            batch.push_back(std::move(fileInfo));
            processedCount++;
            
            // 批量发送数据
            if (batch.size() >= BATCH_SIZE) {
                if (m_initialBatchCallback) {
                    m_initialBatchCallback(batch);
                }
                
                {
                    std::lock_guard<std::mutex> lock(m_statsMutex);
                    m_stats.indexed_files += batch.size();
                }
                
                if (m_progressCallback) {
                    m_progressCallback(processedCount, 0); // 总数未知
                }
                
                batch.clear();
                batch.reserve(BATCH_SIZE);
            }
        }
        
        // 检查是否需要停止
        if (!m_running) {
            break;
        }
    }
    
    // 发送剩余的文件
    if (!batch.empty()) {
        if (m_initialBatchCallback) {
            m_initialBatchCallback(batch);
        }
        
        std::lock_guard<std::mutex> lock(m_statsMutex);
        m_stats.indexed_files += batch.size();
    }
    
    {
        std::lock_guard<std::mutex> lock(m_statsMutex);
        m_stats.total_files = m_stats.indexed_files;
    }
    
    std::cout << "📊 处理完成，共处理 " << processedCount << " 个文件" << std::endl;
}

FileInfo MacOSFileIndexProvider::createFileInfoFromPath(const std::string& path) {
    FileInfo info;
    
    try {
        struct stat fileStat;
        if (stat(path.c_str(), &fileStat) != 0) {
            return info; // 返回空的FileInfo
        }
        
        info.path = path;
        info.name = fs::path(path).filename().string();
        info.extension = fs::path(path).extension().string();
        info.size = static_cast<uint64_t>(fileStat.st_size);
        info.is_directory = S_ISDIR(fileStat.st_mode);
        
        // 转换修改时间
        auto timepoint = std::chrono::system_clock::from_time_t(fileStat.st_mtime);
        info.modified_time = timepoint;
        
    } catch (const std::exception& e) {
        std::cerr << "❌ 处理文件路径失败: " << path << ", 错误: " << e.what() << std::endl;
        return FileInfo{}; // 返回空的FileInfo
    }
    
    return info;
}

bool MacOSFileIndexProvider::shouldExcludePath(const std::string& path) const {
    for (const auto& pattern : m_excludePatterns) {
        try {
            std::regex regex(pattern);
            if (std::regex_search(path, regex)) {
                return true;
            }
        } catch (const std::regex_error& e) {
            std::cerr << "⚠️ 无效的排除正则表达式: " << pattern << std::endl;
        }
    }
    return false;
}

std::string MacOSFileIndexProvider::executeCommand(const std::string& command) const {
    FILE* pipe = popen(command.c_str(), "r");
    if (!pipe) {
        std::cerr << "❌ 执行命令失败: " << command << std::endl;
        return "";
    }
    
    std::string result;
    char buffer[4096];
    while (fgets(buffer, sizeof(buffer), pipe) != nullptr) {
        result += buffer;
    }
    
    int status = pclose(pipe);
    if (status != 0) {
        std::cerr << "⚠️ 命令执行返回非零状态: " << status << std::endl;
    }
    
    return result;
}

bool MacOSFileIndexProvider::checkSpotlightAvailability() const {
    // 检查mdutil命令是否可用
    std::string output = executeCommand("which mdfind");
    if (output.empty()) {
        return false;
    }
    
    // 检查Spotlight服务状态
    output = executeCommand("mdutil -s / 2>/dev/null");
    return !output.empty();
}

std::string MacOSFileIndexProvider::getSpotlightStatus() const {
    std::string status = executeCommand("mdutil -s / 2>/dev/null | head -1");
    if (status.empty()) {
        return "Spotlight状态未知";
    }
    
    // 简化状态信息
    if (status.find("Enabled") != std::string::npos) {
        return "Spotlight已启用";
    } else if (status.find("Disabled") != std::string::npos) {
        return "Spotlight已禁用";
    } else {
        return "Spotlight状态: " + status;
    }
}

// FSEvents相关方法的简化实现（完整实现较复杂）
bool MacOSFileIndexProvider::startFSEventsMonitoring() {
    std::cout << "🔄 启动FSEvents监控 (简化版)" << std::endl;
    
    // 这里应该实现完整的FSEvents监控
    // 由于FSEvents API较复杂，这里先提供简化版本
    m_watching = true;
    
    std::lock_guard<std::mutex> lock(m_statsMutex);
    m_stats.is_watching = true;
    
    return true;
}

void MacOSFileIndexProvider::stopFSEventsMonitoring() {
    if (m_eventStream) {
        FSEventStreamStop(m_eventStream);
        FSEventStreamInvalidate(m_eventStream);
        FSEventStreamRelease(m_eventStream);
        m_eventStream = nullptr;
    }
    
    std::lock_guard<std::mutex> lock(m_statsMutex);
    m_stats.is_watching = false;
    m_watching = false;
}

void MacOSFileIndexProvider::eventProcessingWorker() {
    std::cout << "🔄 事件处理工作线程启动" << std::endl;
    
    while (m_running) {
        std::unique_lock<std::mutex> lock(m_eventQueueMutex);
        m_eventQueueCV.wait_for(lock, std::chrono::milliseconds(100), 
                               [this] { return !m_eventQueue.empty() || !m_running; });
        
        // 处理队列中的事件
        while (!m_eventQueue.empty()) {
            FileEvent event = std::move(m_eventQueue.front());
            m_eventQueue.pop();
            lock.unlock();
            
            // 调用回调函数
            if (m_fileEventCallback) {
                m_fileEventCallback(event);
            }
            
            lock.lock();
        }
    }
    
    std::cout << "🛑 事件处理工作线程退出" << std::endl;
}

void MacOSFileIndexProvider::fsEventsCallback(
    ConstFSEventStreamRef streamRef,
    void* clientCallBackInfo,
    size_t numEvents,
    void* eventPaths,
    const FSEventStreamEventFlags eventFlags[],
    const FSEventStreamEventId eventIds[]) {
    
    // FSEvents回调的完整实现
    // 这里需要将FSEvents事件转换为我们的FileEvent并添加到队列
}

void MacOSFileIndexProvider::processFSEvent(const std::string& path, FSEventStreamEventFlags flags) {
    // 处理单个FSEvents事件
}

FileEventType MacOSFileIndexProvider::determineFSEventType(FSEventStreamEventFlags flags) const {
    // 根据FSEvents标志确定事件类型
    if (flags & kFSEventStreamEventFlagItemCreated) {
        return FileEventType::CREATED;
    } else if (flags & kFSEventStreamEventFlagItemModified) {
        return FileEventType::MODIFIED;
    } else if (flags & kFSEventStreamEventFlagItemRemoved) {
        return FileEventType::DELETED;
    } else if (flags & kFSEventStreamEventFlagItemRenamed) {
        return FileEventType::RENAMED;
    }
    return FileEventType::MODIFIED; // 默认
}

} // namespace linch_connector

#endif // __APPLE__