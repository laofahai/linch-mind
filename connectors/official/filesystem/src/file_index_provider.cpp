#include "file_index_provider.hpp"

#ifdef __APPLE__
#include "platform/macos_file_index_provider.hpp"
#elif defined(__linux__)
#include "platform/linux_file_index_provider.hpp"
#elif defined(_WIN32)
#include "platform/windows_file_index_provider.hpp"
#endif

#include <iostream>

namespace linch_connector {

std::unique_ptr<FileIndexProvider> FileIndexProviderFactory::createProvider() {
    std::cout << "🏭 创建文件索引提供者..." << std::endl;
    
#ifdef __APPLE__
    std::cout << "🍎 创建 macOS 文件索引提供者" << std::endl;
    return std::make_unique<MacOSFileIndexProvider>();
#elif defined(__linux__)
    std::cout << "🐧 创建 Linux 文件索引提供者" << std::endl;
    return std::make_unique<LinuxFileIndexProvider>();
#elif defined(_WIN32)
    std::cout << "🪟 创建 Windows 文件索引提供者" << std::endl;
    return std::make_unique<WindowsFileIndexProvider>();
#else
    std::cout << "❌ 不支持的平台" << std::endl;
    return nullptr;
#endif
}

std::string FileIndexProviderFactory::getPlatformName() {
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

bool FileIndexProviderFactory::isZeroScanSupported() {
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

} // namespace linch_connector