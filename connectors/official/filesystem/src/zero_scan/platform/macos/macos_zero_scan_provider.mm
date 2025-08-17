#ifdef __APPLE__

#include "macos_zero_scan_provider.hpp"
#include <iostream>
#include <sstream>
#include <unistd.h>

// Objective-C includes for mdfind
#import <Foundation/Foundation.h>

namespace linch_connector {
namespace zero_scan {

MacOSZeroScanProvider::MacOSZeroScanProvider() {
    m_stats.platform = "macOS";
    m_stats.scan_method = "mdfind命令行";
}

MacOSZeroScanProvider::~MacOSZeroScanProvider() {
    shutdown();
}

bool MacOSZeroScanProvider::initialize(const ScanConfiguration& config) {
    if (m_initialized.load()) {
        return true;
    }
    
    m_config = config;
    m_initialized.store(true);
    
    std::cout << "✅ macOS 零扫描提供者初始化完成 (极简版)" << std::endl;
    return true;
}

void MacOSZeroScanProvider::shutdown() {
    if (!m_initialized.load()) {
        return;
    }
    
    m_scanning.store(false);
    m_initialized.store(false);
    
    std::cout << "🔄 macOS 零扫描提供者已关闭" << std::endl;
}

bool MacOSZeroScanProvider::performZeroScan(
    std::function<void(const UnifiedFileRecord&)> callback) {
    
    if (!m_initialized.load()) {
        std::cerr << "❌ 提供者未初始化" << std::endl;
        return false;
    }
    
    if (m_scanning.load()) {
        std::cerr << "⚠️  已有扫描在进行中" << std::endl;
        return false;
    }
    
    m_scanning.store(true);
    
    std::cout << "🧪 开始极简零扫描测试..." << std::endl;
    
    // 设置最低优先级
    setpriority(PRIO_PROCESS, 0, 20);
    
    auto startTime = std::chrono::high_resolution_clock::now();
    m_stats.start_time = std::chrono::system_clock::now();
    
    // 🧪 极简测试：只查询5个文档文件
    bool success = executeSimpleMDFind(callback);
    
    auto endTime = std::chrono::high_resolution_clock::now();
    m_stats.end_time = std::chrono::system_clock::now();
    m_stats.scan_duration_ms = std::chrono::duration_cast<std::chrono::milliseconds>(
        endTime - startTime
    ).count();
    
    m_scanning.store(false);
    
    if (success) {
        std::cout << "🎉 极简零扫描完成！" << std::endl;
        std::cout << "   📁 文件数量: " << m_stats.total_files << std::endl;
        std::cout << "   ⏱️  用时: " << m_stats.scan_duration_ms << "ms" << std::endl;
    }
    
    return success;
}

bool MacOSZeroScanProvider::executeSimpleMDFind(
    std::function<void(const UnifiedFileRecord&)> callback) {
    
    std::cout << "🔍 执行极简mdfind测试 (只查5个文档)" << std::endl;
    
    @autoreleasepool {
        // 构建简单的mdfind命令
        NSString* command = @"/usr/bin/mdfind 'kind:document' | head -5";
        
        // 执行命令
        NSTask* task = [[NSTask alloc] init];
        task.launchPath = @"/bin/sh";
        task.arguments = @[@"-c", command];
        
        NSPipe* pipe = [NSPipe pipe];
        task.standardOutput = pipe;
        task.standardError = pipe;
        
        size_t processed_count = 0;
        
        @try {
            [task launch];
            [task waitUntilExit];
            
            if (task.terminationStatus != 0) {
                std::cout << "⚠️  mdfind 命令执行失败" << std::endl;
                return false;
            }
            
            // 读取输出
            NSData* data = [[pipe fileHandleForReading] readDataToEndOfFile];
            NSString* output = [[NSString alloc] initWithData:data encoding:NSUTF8StringEncoding];
            
            if (!output || output.length == 0) {
                std::cout << "ℹ️ mdfind 无结果输出" << std::endl;
                return true;
            }
            
            // 按行处理结果
            NSArray<NSString*>* lines = [output componentsSeparatedByString:@"\n"];
            
            std::cout << "📋 mdfind返回 " << lines.count << " 行结果" << std::endl;
            
            for (NSUInteger i = 0; i < lines.count; i++) {
                if (!m_scanning.load()) {
                    break;
                }
                
                NSString* line = lines[i];
                if (line.length == 0) {
                    continue;
                }
                
                std::cout << "📄 处理文件: " << [line UTF8String] << std::endl;
                
                // 创建简单记录
                UnifiedFileRecord record;
                record.path = [line UTF8String];
                
                // 提取文件名
                size_t last_slash = record.path.find_last_of('/');
                if (last_slash != std::string::npos) {
                    record.name = record.path.substr(last_slash + 1);
                } else {
                    record.name = record.path;
                }
                
                // 设置默认值
                record.size = 0;
                record.is_directory = false;
                record.modified_time = std::chrono::system_clock::now();
                
                // 调用回调
                if (callback) {
                    callback(record);
                    processed_count++;
                }
                
                // 每个文件后休眠1秒
                std::cout << "😴 处理完成，休眠1秒..." << std::endl;
                std::this_thread::sleep_for(std::chrono::milliseconds(1000));
            }
            
        } @catch (NSException* exception) {
            std::cout << "❌ mdfind 执行异常: " << [[exception description] UTF8String] << std::endl;
            return false;
        }
        
        std::cout << "✅ 极简mdfind完成，处理了 " << processed_count << " 个文件" << std::endl;
        m_stats.total_files = processed_count;
        
        return true;
    }
}

// 其他必需的接口实现
bool MacOSZeroScanProvider::subscribeToChanges(
    std::function<void(const FileChangeEvent&)> callback) {
    // 简化实现
    return true;
}

void MacOSZeroScanProvider::unsubscribeFromChanges() {
    // 简化实现
}

ScanStatistics MacOSZeroScanProvider::getStatistics() const {
    std::lock_guard<std::mutex> lock(m_mutex);
    return m_stats;
}

bool MacOSZeroScanProvider::isAvailable() const {
    return true;  // 简化实现
}

std::string MacOSZeroScanProvider::getPlatformInfo() const {
    return "macOS mdfind极简版";
}

void MacOSZeroScanProvider::updateConfiguration(const ScanConfiguration& config) {
    std::lock_guard<std::mutex> lock(m_mutex);
    m_config = config;
}

void MacOSZeroScanProvider::clearCache() {
    // 简化实现
}

bool MacOSZeroScanProvider::warmupCache() {
    return true;  // 简化实现
}

void MacOSZeroScanProvider::pause() {
    m_paused.store(true);
}

void MacOSZeroScanProvider::resume() {
    m_paused.store(false);
}

void MacOSZeroScanProvider::setThrottleLevel(int level) {
    // 简化实现
}

} // namespace zero_scan
} // namespace linch_connector

#endif // __APPLE__