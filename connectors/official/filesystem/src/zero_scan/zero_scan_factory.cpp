#include "zero_scan_interface.hpp"

#ifdef __APPLE__
#include "platform/macos/macos_zero_scan_provider.hpp"
#endif

#ifdef __linux__
#include "platform/linux/linux_zero_scan_provider.hpp"
#endif

#ifdef _WIN32
#include "platform/windows/windows_zero_scan_provider.hpp"
#endif

namespace linch_connector {
namespace zero_scan {

std::unique_ptr<IZeroScanProvider> ZeroScanFactory::createProvider() {
    return createProvider(ProviderType::AUTO);
}

std::unique_ptr<IZeroScanProvider> ZeroScanFactory::createProvider(ProviderType type) {
    switch (type) {
        case ProviderType::AUTO:
        case ProviderType::NATIVE:
#ifdef __APPLE__
            return std::make_unique<MacOSZeroScanProvider>();
#elif defined(__linux__)
            return std::make_unique<LinuxZeroScanProvider>();
#elif defined(_WIN32)
            return std::make_unique<WindowsZeroScanProvider>();
#else
            return nullptr;
#endif
        
        case ProviderType::SYSTEM_API:
#ifdef __APPLE__
            return std::make_unique<MacOSZeroScanProvider>();
#elif defined(__linux__)
            // Linux System API implementation
            return nullptr;
#elif defined(_WIN32)
            // Windows System API implementation
            return nullptr;
#else
            return nullptr;
#endif
        
        case ProviderType::FALLBACK:
            // 降级实现：使用标准库递归遍历
            return nullptr;
        
        default:
            return nullptr;
    }
}

std::vector<std::string> ZeroScanFactory::getAvailableProviders() {
    std::vector<std::string> providers;
    
#ifdef __APPLE__
    providers.push_back("macOS Spotlight (MDQuery)");
    providers.push_back("macOS mdfind");
#endif

#ifdef __linux__
    providers.push_back("Linux locate");
    providers.push_back("Linux find");
#endif

#ifdef _WIN32
    providers.push_back("Windows MFT");
    providers.push_back("Windows Search API");
#endif

    providers.push_back("Standard Library (Fallback)");
    
    return providers;
}

ScanStatistics ZeroScanFactory::runBenchmark(const ScanConfiguration& config) {
    auto provider = createProvider(ProviderType::AUTO);
    if (!provider) {
        ScanStatistics stats;
        stats.scan_method = "Benchmark Failed";
        stats.error_count = 1;
        return stats;
    }
    
    if (!provider->initialize(config)) {
        ScanStatistics stats;
        stats.scan_method = provider->getPlatformInfo();
        stats.error_count = 1;
        return stats;
    }
    
    size_t fileCount = 0;
    auto startTime = std::chrono::high_resolution_clock::now();
    
    provider->performZeroScan([&fileCount](const UnifiedFileRecord& record) {
        fileCount++;
    });
    
    auto endTime = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(endTime - startTime);
    
    ScanStatistics stats = provider->getStatistics();
    stats.scan_duration_ms = duration.count();
    stats.total_files = fileCount;
    
    if (duration.count() > 0) {
        stats.files_per_second = (fileCount * 1000) / duration.count();
    }
    
    provider->shutdown();
    return stats;
}

} // namespace zero_scan
} // namespace linch_connector