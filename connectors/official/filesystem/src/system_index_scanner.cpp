#include "system_index_scanner.hpp"
#include <iostream>
#include <algorithm>
#include <filesystem>

namespace fs = std::filesystem;

// ========================================
// SystemIndexScannerFactory Implementation
// ========================================

std::unique_ptr<ISystemIndexScanner> SystemIndexScannerFactory::createScanner() {
#ifdef _WIN32
    return std::make_unique<WindowsSystemIndexScanner>();
#elif defined(__APPLE__)
    return std::make_unique<MacOSSystemIndexScanner>();
#elif defined(__linux__)
    return std::make_unique<LinuxSystemIndexScanner>();
#else
    std::cerr << "❌ 不支持的平台，无法创建系统索引扫描器" << std::endl;
    return nullptr;
#endif
}

std::string SystemIndexScannerFactory::getPlatformName() {
#ifdef _WIN32
    return "Windows";
#elif defined(__APPLE__)
    return "macOS";
#elif defined(__linux__)
    return "Linux";
#else
    return "Unknown";
#endif
}

bool SystemIndexScannerFactory::isPlatformSupported() {
#if defined(_WIN32) || defined(__APPLE__) || defined(__linux__)
    return true;
#else
    return false;
#endif
}

SystemIndexQuery SystemIndexScannerFactory::getDefaultQuery() {
    SystemIndexQuery query;
    query.namePattern = "*";
    query.includeHidden = false;
    query.maxResults = 10000;
    
#ifdef __APPLE__
    // macOS特定优化
    query.maxResults = 50000; // Spotlight很快，可以处理更多结果
#elif defined(_WIN32)
    // Windows特定优化
    query.maxResults = 100000; // NTFS MFT访问很快
#elif defined(__linux__)
    // Linux特定优化
    query.maxResults = 20000; // locate数据库中等速度
#endif
    
    return query;
}

// ========================================
// HybridIndexManager Implementation
// ========================================

HybridIndexManager::HybridIndexManager() {
    m_stats.startTime = std::chrono::steady_clock::now();
}

HybridIndexManager::~HybridIndexManager() = default;

bool HybridIndexManager::initialize() {
    std::cout << "🚀 初始化混合索引管理器..." << std::endl;
    
    // 创建平台特定的系统索引扫描器
    m_systemScanner = SystemIndexScannerFactory::createScanner();
    if (!m_systemScanner) {
        std::cerr << "❌ 无法创建系统索引扫描器" << std::endl;
        return false;
    }
    
    std::cout << "📋 平台: " << SystemIndexScannerFactory::getPlatformName() << std::endl;
    std::cout << "🔧 扫描器: " << m_systemScanner->getPlatformInfo() << std::endl;
    
    // 初始化系统索引扫描器
    if (!m_systemScanner->initialize()) {
        std::cerr << "❌ 系统索引扫描器初始化失败" << std::endl;
        return false;
    }
    
    if (!m_systemScanner->isAvailable()) {
        std::cerr << "⚠️ 系统索引不可用，将回退到文件系统遍历" << std::endl;
        return true; // 仍然返回true，但会使用回退方案
    }
    
    // 检查索引健康状态
    if (!m_systemScanner->isIndexHealthy()) {
        std::cerr << "⚠️ 系统索引健康检查失败" << std::endl;
    }
    
    std::cout << "📊 " << m_systemScanner->getIndexStats() << std::endl;
    std::cout << "✅ 混合索引管理器初始化完成" << std::endl;
    
    return true;
}

bool HybridIndexManager::queryFiles(const SystemIndexQuery& query, 
                                   std::vector<SystemIndexResult>& results) {
    m_stats.systemIndexQueries++;
    
    if (!m_systemScanner || !m_systemScanner->isAvailable()) {
        std::cerr << "❌ 系统索引不可用" << std::endl;
        return false;
    }
    
    auto startTime = std::chrono::steady_clock::now();
    
    bool success = m_systemScanner->queryIndex(query, results);
    
    auto endTime = std::chrono::steady_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(endTime - startTime);
    
    if (success) {
        m_stats.systemIndexHits++;
        std::cout << "⚡ 系统索引查询完成，耗时 " << duration.count() 
                  << "ms，返回 " << results.size() << " 个结果" << std::endl;
    } else {
        std::cerr << "❌ 系统索引查询失败，耗时 " << duration.count() << "ms" << std::endl;
    }
    
    return success;
}

bool HybridIndexManager::getPathFiles(const std::string& path,
                                     std::vector<SystemIndexResult>& results) {
    if (!m_systemScanner || !m_systemScanner->isAvailable()) {
        std::cerr << "❌ 系统索引不可用，无法获取路径文件" << std::endl;
        return false;
    }
    
    auto startTime = std::chrono::steady_clock::now();
    
    bool success = m_systemScanner->getAllFiles(path, results);
    
    auto endTime = std::chrono::steady_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(endTime - startTime);
    
    if (success) {
        std::cout << "📁 路径文件获取完成，耗时 " << duration.count() 
                  << "ms，路径: " << path << "，文件数: " << results.size() << std::endl;
        
        // 过滤结果，只保留指定路径下的文件
        results.erase(
            std::remove_if(results.begin(), results.end(),
                [&path](const SystemIndexResult& result) {
                    return result.path.find(path) != 0;
                }),
            results.end()
        );
        
        std::cout << "🔍 路径过滤后剩余 " << results.size() << " 个文件" << std::endl;
    } else {
        std::cerr << "❌ 路径文件获取失败" << std::endl;
    }
    
    return success;
}

void HybridIndexManager::setRealtimeCallback(std::function<void(const SystemIndexResult&)> callback) {
    m_realtimeCallback = callback;
}

std::string HybridIndexManager::getStats() const {
    auto now = std::chrono::steady_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::seconds>(now - m_stats.startTime);
    
    std::string stats = "混合索引统计:\n";
    stats += "  运行时间: " + std::to_string(duration.count()) + "秒\n";
    stats += "  系统索引查询: " + std::to_string(m_stats.systemIndexQueries) + "\n";
    stats += "  成功命中: " + std::to_string(m_stats.systemIndexHits) + "\n";
    stats += "  实时事件: " + std::to_string(m_stats.realtimeEvents) + "\n";
    
    if (m_stats.systemIndexQueries > 0) {
        double hitRate = (double)m_stats.systemIndexHits / m_stats.systemIndexQueries * 100.0;
        stats += "  命中率: " + std::to_string(hitRate) + "%\n";
    }
    
    if (m_systemScanner && m_systemScanner->isAvailable()) {
        stats += "  " + m_systemScanner->getIndexStats() + "\n";
    }
    
    return stats;
}

// ========================================
// 平台特定实现的占位符
// ========================================

#ifdef _WIN32
// Windows实现将在单独的文件中提供
WindowsSystemIndexScanner::WindowsSystemIndexScanner() = default;
WindowsSystemIndexScanner::~WindowsSystemIndexScanner() = default;
bool WindowsSystemIndexScanner::isAvailable() const { return false; }
std::string WindowsSystemIndexScanner::getPlatformInfo() const { return "Windows MFT/Search Index (未实现)"; }
bool WindowsSystemIndexScanner::initialize() { return false; }
bool WindowsSystemIndexScanner::queryIndex(const SystemIndexQuery&, std::vector<SystemIndexResult>&) { return false; }
bool WindowsSystemIndexScanner::getAllFiles(const std::string&, std::vector<SystemIndexResult>&) { return false; }
bool WindowsSystemIndexScanner::isIndexHealthy() const { return false; }
std::string WindowsSystemIndexScanner::getIndexStats() const { return "未实现"; }
#endif

#ifdef __linux__
// Linux实现将在单独的文件中提供
LinuxSystemIndexScanner::LinuxSystemIndexScanner() = default;
LinuxSystemIndexScanner::~LinuxSystemIndexScanner() = default;
bool LinuxSystemIndexScanner::isAvailable() const { return false; }
std::string LinuxSystemIndexScanner::getPlatformInfo() const { return "Linux locate/mlocate (未实现)"; }
bool LinuxSystemIndexScanner::initialize() { return false; }
bool LinuxSystemIndexScanner::queryIndex(const SystemIndexQuery&, std::vector<SystemIndexResult>&) { return false; }
bool LinuxSystemIndexScanner::getAllFiles(const std::string&, std::vector<SystemIndexResult>&) { return false; }
bool LinuxSystemIndexScanner::isIndexHealthy() const { return false; }
std::string LinuxSystemIndexScanner::getIndexStats() const { return "未实现"; }
#endif