#include "linch_connector/file_index_provider.hpp"

#ifdef __APPLE__
#include "linch_connector/platform/macos_file_index_provider.hpp"
#elif defined(__linux__)
// Linux平台实现将在对应平台文件中定义
#elif defined(_WIN32)
// Windows平台实现将在对应平台文件中定义
#endif

#include <iostream>

namespace linch_connector {

// FileMonitorProviderFactory 实现 - 用于Filesystem连接器
std::unique_ptr<IFileMonitorProvider> FileMonitorProviderFactory::createProvider() {
    std::cout << "🏭 创建文件监控提供者..." << std::endl;
    
#ifdef __APPLE__
    std::cout << "🍎 创建 macOS 文件监控提供者" << std::endl;
    // TODO: 实现 MacOSFileMonitorProvider 
    return nullptr;
#elif defined(__linux__)
    std::cout << "🐧 创建 Linux 文件监控提供者" << std::endl;
    // TODO: 实现 LinuxFileMonitorProvider
    return nullptr;
#elif defined(_WIN32)
    std::cout << "🪟 创建 Windows 文件监控提供者" << std::endl;
    // TODO: 实现 WindowsFileMonitorProvider
    return nullptr;
#else
    std::cout << "❌ 不支持的平台" << std::endl;
    return nullptr;
#endif
}

std::string FileMonitorProviderFactory::getPlatformName() {
#ifdef __APPLE__
    return "macOS";
#elif defined(__linux__)
    return "Linux";
#elif defined(_WIN32)
    return "Windows";
#else
    return "Unknown";
#endif
}

bool FileMonitorProviderFactory::isZeroScanSupported() {
#ifdef __APPLE__
    // macOS通过Spotlight支持零扫描
    return true;
#elif defined(_WIN32)
    // Windows通过MFT或Windows Search Index支持零扫描
    return true;
#elif defined(__linux__)
    // Linux通过locate数据库部分支持零扫描
    return true;
#else
    return false;
#endif
}

// FileIndexProviderFactory 实现 - 用于System Info连接器
std::unique_ptr<IFileIndexProvider> FileIndexProviderFactory::createForCurrentPlatform() {
    std::cout << "🏭 创建文件索引提供者..." << std::endl;
    
#ifdef __APPLE__
    std::cout << "🍎 创建 macOS 文件索引提供者" << std::endl;
    return std::make_unique<MacOSFileIndexProvider>();
#elif defined(__linux__)
    std::cout << "🐧 创建 Linux 文件索引提供者" << std::endl;
    // TODO: 实现 LinuxFileIndexProvider
    return nullptr;
#elif defined(_WIN32)
    std::cout << "🪟 创建 Windows 文件索引提供者" << std::endl;
    // TODO: 实现 WindowsFileIndexProvider
    return nullptr;
#else
    std::cout << "❌ 不支持的平台" << std::endl;
    return nullptr;
#endif
}

} // namespace linch_connector