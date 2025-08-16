#pragma once

#include <string>
#include <vector>
#include <functional>
#include <memory>
#include <set>
#include <unordered_map>
#include <mutex>
#include <chrono>
#include <filesystem>
#include <atomic>

namespace fs = std::filesystem;

// 文件系统事件类型
enum class FileEventType {
    CREATED,
    MODIFIED,
    DELETED,
    RENAMED_OLD,
    RENAMED_NEW,
    UNKNOWN
};

// 文件系统事件
struct FileSystemEvent {
    std::string path;
    std::string oldPath;  // 用于重命名事件
    FileEventType type;
    std::chrono::system_clock::time_point timestamp;
    size_t fileSize;
    bool isDirectory;
    
    // 默认构造函数
    FileSystemEvent() : type(FileEventType::UNKNOWN), fileSize(0), isDirectory(false) {
        timestamp = std::chrono::system_clock::now();
    }
    
    FileSystemEvent(const std::string& p, FileEventType t)
        : path(p), type(t), fileSize(0), isDirectory(false) {
        timestamp = std::chrono::system_clock::now();
    }
};

// 监控配置
struct MonitorConfig {
    std::string path;
    bool recursive = true;
    std::set<std::string> includeExtensions;
    std::set<std::string> excludePatterns;
    size_t maxFileSize = 50 * 1024 * 1024;  // 50MB
    bool watchDirectories = true;
    bool watchFiles = true;
    
    // 目录级剪枝 - 这些目录将被完全忽略
    std::set<std::string> excludeDirectories = {
        ".git", ".svn", ".hg", ".bzr",
        "node_modules", "__pycache__", ".pytest_cache",
        "build", "dist", "target", "out",
        ".idea", ".vscode", ".vs", ".DS_Store"
    };
    
    MonitorConfig(const std::string& p) : path(p) {}
};

// 事件回调
using EventCallback = std::function<void(const FileSystemEvent&)>;
using BatchEventCallback = std::function<void(const std::vector<FileSystemEvent>&)>;

// 抽象基类 - 所有平台监控器的接口
class INativeMonitor {
public:
    virtual ~INativeMonitor() = default;
    
    // 核心接口
    virtual bool start(EventCallback callback) = 0;
    virtual void stop() = 0;
    virtual bool isRunning() const = 0;
    
    // 配置管理
    virtual bool addPath(const MonitorConfig& config) = 0;
    virtual bool removePath(const std::string& path) = 0;
    virtual std::vector<std::string> getMonitoredPaths() const = 0;
    
    // 设置批处理回调（可选）
    virtual void setBatchCallback(BatchEventCallback callback, std::chrono::milliseconds batchInterval) {
        m_batchCallback = callback;
        m_batchInterval = batchInterval;
    }
    
protected:
    std::atomic<bool> m_running{false};
    EventCallback m_eventCallback;
    BatchEventCallback m_batchCallback;
    std::chrono::milliseconds m_batchInterval{500};
    
    // 路径过滤
    bool shouldIgnorePath(const std::string& path, const MonitorConfig& config) {
        fs::path fsPath(path);
        
        // 检查是否是排除的目录
        std::string filename = fsPath.filename().string();
        if (config.excludeDirectories.count(filename) > 0) {
            return true;
        }
        
        // 检查排除模式
        for (const auto& pattern : config.excludePatterns) {
            if (matchPattern(path, pattern)) {
                return true;
            }
        }
        
        // 如果指定了包含扩展名，检查文件扩展名
        if (!config.includeExtensions.empty() && fs::is_regular_file(fsPath)) {
            std::string ext = fsPath.extension().string();
            if (config.includeExtensions.count(ext) == 0) {
                return true;
            }
        }
        
        // 优化：延迟文件大小检查，仅在真正需要时执行
        // 这避免了对每个文件事件进行系统调用
        // 文件大小将在处理事件时检查（如果需要）
        // 这里不再进行预检查
        
        return false;
    }
    
    // 简单的模式匹配（可以后续改进为更复杂的glob匹配）
    bool matchPattern(const std::string& path, const std::string& pattern) {
        // 简单实现：检查路径是否包含模式
        return path.find(pattern) != std::string::npos;
    }
};

// 事件去重和批处理器
class EventDebouncer {
public:
    EventDebouncer(std::chrono::milliseconds debounceTime = std::chrono::milliseconds(500))
        : m_lastEventTime(std::chrono::system_clock::now().time_since_epoch().count()), m_debounceTime(debounceTime) {}
    
    void addEvent(const FileSystemEvent& event) {
        // 使用原子操作减少锁竞争
        auto now = std::chrono::system_clock::now();
        m_lastEventTime.store(now.time_since_epoch().count());
        
        // 短锁：仅在修改数据结构时持有锁
        {
            std::lock_guard<std::mutex> lock(m_mutex);
            
            // 如果是同一文件的重复事件，合并或更新
            auto it = m_pendingEvents.find(event.path);
            if (it != m_pendingEvents.end()) {
                // 更新事件类型优先级：DELETED > CREATED > MODIFIED
                if (event.type == FileEventType::DELETED) {
                    it->second = event;
                } else if (it->second.type != FileEventType::DELETED) {
                    it->second = event;
                }
            } else {
                m_pendingEvents[event.path] = event;
            }
        } // 锁自动释放
    }
    
    std::vector<FileSystemEvent> getEventsIfReady() {
        // 无锁预检查：避免在未到时间时获取锁
        auto now = std::chrono::system_clock::now();
        auto lastTime = std::chrono::system_clock::time_point(
            std::chrono::system_clock::duration(m_lastEventTime.load()));
        
        if (now - lastTime < m_debounceTime) {
            return {}; // 快速返回，无需锁
        }
        
        std::lock_guard<std::mutex> lock(m_mutex);
        
        if (m_pendingEvents.empty()) {
            return {};
        }
        
        // 双重检查：再次验证时间（防止竞态条件）
        lastTime = std::chrono::system_clock::time_point(
            std::chrono::system_clock::duration(m_lastEventTime.load()));
        if (now - lastTime >= m_debounceTime) {
            std::vector<FileSystemEvent> result;
            result.reserve(m_pendingEvents.size());
            
            for (auto& [path, event] : m_pendingEvents) {
                // 🚀 性能优化: 延迟文件系统检查以减少CPU开销
                // 仅在确实需要时才进行文件系统调用，大多数情况下使用事件提供的信息
                try {
                    std::filesystem::path fsPath(event.path);
                    // 优化：使用单次stat调用获取所有信息
                    std::error_code ec;
                    auto fileStatus = std::filesystem::status(fsPath, ec);
                    if (!ec) {
                        event.isDirectory = std::filesystem::is_directory(fileStatus);
                        if (!event.isDirectory) {
                            // 仅对普通文件获取大小，避免对目录的额外系统调用
                            auto fileSize = std::filesystem::file_size(fsPath, ec);
                            event.fileSize = ec ? 0 : fileSize;
                        }
                    }
                    // 如果文件不存在或发生错误，保持默认值（isDirectory=false, fileSize=0）
                } catch (...) {
                    // 忽略文件系统错误，使用默认值以避免处理中断
                }
                
                result.push_back(std::move(event));
            }
            
            m_pendingEvents.clear();
            return result;
        }
        
        return {};
    }
    
    std::vector<FileSystemEvent> forceFlush() {
        std::lock_guard<std::mutex> lock(m_mutex);
        std::vector<FileSystemEvent> result;
        result.reserve(m_pendingEvents.size());
        
        for (auto& [path, event] : m_pendingEvents) {
            result.push_back(std::move(event));
        }
        
        m_pendingEvents.clear();
        return result;
    }
    
private:
    std::unordered_map<std::string, FileSystemEvent> m_pendingEvents;
    std::atomic<std::chrono::system_clock::rep> m_lastEventTime; // 原子时间戳
    std::chrono::milliseconds m_debounceTime;
    mutable std::mutex m_mutex; // 保护pendingEvents的最小锁
};