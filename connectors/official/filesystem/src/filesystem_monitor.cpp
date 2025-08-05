#include "filesystem_monitor.hpp"
#include <iostream>
#include <algorithm>
#include <fstream>

#ifdef _WIN32
    #include <fnmatch.h>  // For Windows, you might need to implement or use a library
#else
    #include <fnmatch.h>
#endif

namespace fs = std::filesystem;

FileSystemMonitor::FileSystemMonitor() {
}

FileSystemMonitor::~FileSystemMonitor() {
    stopMonitoring();
}

bool FileSystemMonitor::addWatch(const WatchConfig& config) {
    std::lock_guard<std::mutex> lock(m_configMutex);
    
    // Check if path already being watched
    auto it = std::find_if(m_watchConfigs.begin(), m_watchConfigs.end(),
        [&config](const WatchConfig& existing) {
            return existing.path == config.path;
        });
    
    if (it != m_watchConfigs.end()) {
        std::cout << "⚠️  Path already being watched: " << config.path << std::endl;
        return false;
    }
    
    // Validate path exists
    if (!fs::exists(config.path)) {
        std::cout << "❌ Path does not exist: " << config.path << std::endl;
        return false;
    }
    
    if (!fs::is_directory(config.path)) {
        std::cout << "❌ Path is not a directory: " << config.path << std::endl;
        return false;
    }
    
    m_watchConfigs.push_back(config);
    
    std::cout << "✅ Added watch for: " << config.path << std::endl;
    return true;
}

bool FileSystemMonitor::removeWatch(const std::string& path) {
    std::lock_guard<std::mutex> lock(m_configMutex);
    
    auto it = std::find_if(m_watchConfigs.begin(), m_watchConfigs.end(),
        [&path](const WatchConfig& config) {
            return config.path == path;
        });
    
    if (it == m_watchConfigs.end()) {
        return false;
    }
    
    m_watchConfigs.erase(it);
    
    // Clean up file states for this path
    {
        std::lock_guard<std::mutex> stateLock(m_statesMutex);
        auto stateIt = m_fileStates.begin();
        while (stateIt != m_fileStates.end()) {
            if (stateIt->first.find(path) == 0) {
                stateIt = m_fileStates.erase(stateIt);
            } else {
                ++stateIt;
            }
        }
    }
    
    std::cout << "✅ Removed watch for: " << path << std::endl;
    return true;
}

bool FileSystemMonitor::startMonitoring(ChangeCallback callback, int pollInterval) {
    if (m_monitoring) {
        std::cout << "⚠️  Already monitoring" << std::endl;
        return false;
    }
    
    if (m_watchConfigs.empty()) {
        std::cout << "❌ No paths to watch" << std::endl;
        return false;
    }
    
    m_callback = callback;
    m_pollInterval = pollInterval;
    m_monitoring = true;
    
    // Start monitoring thread
    m_monitorThread = std::thread(&FileSystemMonitor::monitorLoop, this);
    
    // Start event processing thread
    m_processingThread = std::thread(&FileSystemMonitor::processEvents, this);
    
    std::cout << "🔍 Filesystem monitoring started (poll interval: " << pollInterval << "ms)" << std::endl;
    return true;
}

void FileSystemMonitor::stopMonitoring() {
    if (!m_monitoring) {
        return;
    }
    
    std::cout << "🛑 Stopping filesystem monitoring..." << std::endl;
    m_monitoring = false;
    
    // Wake up processing thread
    m_queueCondition.notify_all();
    
    // Wait for threads to finish
    if (m_monitorThread.joinable()) {
        m_monitorThread.join();
    }
    
    if (m_processingThread.joinable()) {
        m_processingThread.join();
    }
    
    // Clear event queue
    {
        std::lock_guard<std::mutex> lock(m_queueMutex);
        while (!m_eventQueue.empty()) {
            m_eventQueue.pop();
        }
    }
    
    // Clear file states
    {
        std::lock_guard<std::mutex> lock(m_statesMutex);
        m_fileStates.clear();
    }
    
    std::cout << "📁 Filesystem monitoring stopped" << std::endl;
}

bool FileSystemMonitor::isMonitoring() const {
    return m_monitoring;
}

std::vector<std::string> FileSystemMonitor::getWatchedPaths() const {
    std::lock_guard<std::mutex> lock(m_configMutex);
    std::vector<std::string> paths;
    for (const auto& config : m_watchConfigs) {
        if (config.enabled) {
            paths.push_back(config.path);
        }
    }
    return paths;
}

bool FileSystemMonitor::updateWatchConfig(const std::string& path, const WatchConfig& newConfig) {
    std::lock_guard<std::mutex> lock(m_configMutex);
    
    auto it = std::find_if(m_watchConfigs.begin(), m_watchConfigs.end(),
        [&path](const WatchConfig& config) {
            return config.path == path;
        });
    
    if (it == m_watchConfigs.end()) {
        return false;
    }
    
    *it = newConfig;
    return true;
}

void FileSystemMonitor::monitorLoop() {
    std::cout << "📋 Started filesystem monitoring loop" << std::endl;
    
    while (m_monitoring) {
        try {
            // Scan all watched directories
            {
                std::lock_guard<std::mutex> lock(m_configMutex);
                for (const auto& config : m_watchConfigs) {
                    if (config.enabled) {
                        scanDirectory(config);
                    }
                }
            }
            
            // Sleep for poll interval
            std::this_thread::sleep_for(std::chrono::milliseconds(m_pollInterval));
            
        } catch (const std::exception& e) {
            std::cerr << "❌ Error in monitoring loop: " << e.what() << std::endl;
            std::this_thread::sleep_for(std::chrono::milliseconds(1000));
        }
    }
    
    std::cout << "📋 Filesystem monitoring loop stopped" << std::endl;
}

void FileSystemMonitor::processEvents() {
    std::cout << "📋 Started filesystem event processing thread" << std::endl;
    
    while (m_monitoring) {
        std::unique_lock<std::mutex> lock(m_queueMutex);
        
        // Wait for events or stop signal
        m_queueCondition.wait(lock, [this] {
            return !m_eventQueue.empty() || !m_monitoring;
        });
        
        // Process all available events
        while (!m_eventQueue.empty() && m_monitoring) {
            FileEvent event = m_eventQueue.front();
            m_eventQueue.pop();
            lock.unlock();
            
            try {
                // Call the callback
                if (m_callback) {
                    m_callback(event);
                }
            } catch (const std::exception& e) {
                std::cerr << "❌ Error processing file event: " << e.what() << std::endl;
            }
            
            lock.lock();
        }
    }
    
    std::cout << "📋 Filesystem event processing thread stopped" << std::endl;
}

void FileSystemMonitor::scanDirectory(const WatchConfig& config) {
    try {
        if (config.recursive) {
            scanDirectoryRecursive(config.path, config);
        } else {
            // Non-recursive: only scan immediate files
            for (const auto& entry : fs::directory_iterator(config.path)) {
                if (entry.is_regular_file()) {
                    detectChanges(entry.path().string(), config);
                }
            }
        }
    } catch (const std::exception& e) {
        std::cerr << "❌ Error scanning directory " << config.path << ": " << e.what() << std::endl;
    }
}

void FileSystemMonitor::scanDirectoryRecursive(const std::string& dirPath, const WatchConfig& config) {
    try {
        for (const auto& entry : fs::recursive_directory_iterator(dirPath)) {
            if (entry.is_regular_file()) {
                detectChanges(entry.path().string(), config);
            }
        }
    } catch (const std::exception& e) {
        std::cerr << "❌ Error scanning directory recursively " << dirPath << ": " << e.what() << std::endl;
    }
}

void FileSystemMonitor::detectChanges(const std::string& filePath, const WatchConfig& config) {
    if (!shouldProcessFile(filePath, config)) {
        return;
    }
    
    try {
        std::lock_guard<std::mutex> lock(m_statesMutex);
        
        bool fileExists = fs::exists(filePath);
        auto currentTime = fileExists ? fs::last_write_time(filePath) : std::filesystem::file_time_type{};
        size_t currentSize = fileExists ? fs::file_size(filePath) : 0;
        
        auto it = m_fileStates.find(filePath);
        
        if (it == m_fileStates.end()) {
            // New file discovered
            if (fileExists) {
                m_fileStates[filePath] = FileInfo(currentTime, currentSize);
                
                // Queue creation event
                {
                    std::lock_guard<std::mutex> queueLock(m_queueMutex);
                    m_eventQueue.emplace(filePath, "created", getCurrentTimestamp(), currentSize);
                    m_queueCondition.notify_one();
                }
            }
        } else {
            // Existing file - check for changes
            FileInfo& info = it->second;
            
            if (!fileExists && info.exists) {
                // File was deleted
                info.exists = false;
                
                std::lock_guard<std::mutex> queueLock(m_queueMutex);
                m_eventQueue.emplace(filePath, "deleted", getCurrentTimestamp(), 0);
                m_queueCondition.notify_one();
                
            } else if (fileExists && (currentTime != info.lastWriteTime || currentSize != info.fileSize)) {
                // File was modified
                info.lastWriteTime = currentTime;
                info.fileSize = currentSize;
                info.exists = true;
                
                std::lock_guard<std::mutex> queueLock(m_queueMutex);
                m_eventQueue.emplace(filePath, "modified", getCurrentTimestamp(), currentSize);
                m_queueCondition.notify_one();
            }
        }
    } catch (const std::exception& e) {
        std::cerr << "❌ Error detecting changes for " << filePath << ": " << e.what() << std::endl;
    }
}

bool FileSystemMonitor::shouldProcessFile(const std::string& filePath, const WatchConfig& config) {
    fs::path path(filePath);
    
    // Check if it's a regular file
    if (!fs::exists(path) || !fs::is_regular_file(path)) {
        return false;
    }
    
    // Check file extension
    std::string extension = path.extension().string();
    std::transform(extension.begin(), extension.end(), extension.begin(), ::tolower);
    
    if (!config.supportedExtensions.empty() && 
        config.supportedExtensions.find(extension) == config.supportedExtensions.end()) {
        return false;
    }
    
    // Check file size
    try {
        size_t fileSize = fs::file_size(path);
        if (fileSize > config.maxFileSize) {
            return false;
        }
    } catch (const std::exception&) {
        return false;
    }
    
    // Check ignore patterns
    if (matchesIgnorePattern(filePath, config.ignorePatterns)) {
        return false;
    }
    
    return true;
}

bool FileSystemMonitor::matchesIgnorePattern(const std::string& filePath, 
                                           const std::vector<std::string>& patterns) {
    fs::path path(filePath);
    std::string fileName = path.filename().string();
    std::string relativePath = path.string();
    
    for (const auto& pattern : patterns) {
        // Check filename match
        if (fnmatch(pattern.c_str(), fileName.c_str(), FNM_CASEFOLD) == 0) {
            return true;
        }
        
        // Check path match
        if (fnmatch(pattern.c_str(), relativePath.c_str(), FNM_CASEFOLD) == 0) {
            return true;
        }
        
        // Check directory pattern (ends with /*)
        if (pattern.size() > 2 && pattern.substr(pattern.size() - 2) == "/*") {
            std::string dirPattern = pattern.substr(0, pattern.size() - 2);
            if (relativePath.find(dirPattern) != std::string::npos) {
                return true;
            }
        }
    }
    
    return false;
}

FileSystemMonitor::WatchConfig* FileSystemMonitor::findConfigForPath(const std::string& filePath) {
    std::lock_guard<std::mutex> lock(m_configMutex);
    
    fs::path file(filePath);
    file = file.make_preferred();
    
    for (auto& config : m_watchConfigs) {
        if (!config.enabled) continue;
        
        fs::path watchPath(config.path);
        watchPath = watchPath.make_preferred();
        
        try {
            // Check if file is under this watch path
            auto relativePath = fs::relative(file, watchPath);
            
            // If relative path doesn't start with "..", it's under watchPath
            if (!relativePath.empty() && relativePath.string().substr(0, 2) != "..") {
                if (config.recursive || file.parent_path() == watchPath) {
                    return &config;
                }
            }
        } catch (const std::exception&) {
            continue;
        }
    }
    
    return nullptr;
}

uint64_t FileSystemMonitor::getCurrentTimestamp() {
    return std::chrono::duration_cast<std::chrono::milliseconds>(
        std::chrono::system_clock::now().time_since_epoch()).count();
}