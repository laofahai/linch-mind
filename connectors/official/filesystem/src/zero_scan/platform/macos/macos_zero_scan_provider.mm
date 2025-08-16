#ifdef __APPLE__

#include "macos_zero_scan_provider.hpp"
#include <iostream>
#include <sstream>
#include <regex>
#include <unistd.h>
#include <sys/sysctl.h>
#include <iomanip>

// Objective-C includes for MDQuery
#import <Foundation/Foundation.h>
#import <CoreServices/CoreServices.h>

namespace linch_connector {
namespace zero_scan {

MacOSZeroScanProvider::MacOSZeroScanProvider() {
    m_stats.platform = "macOS";
    m_stats.scan_method = "Spotlight MDQuery";
}

MacOSZeroScanProvider::~MacOSZeroScanProvider() {
    shutdown();
}

bool MacOSZeroScanProvider::initialize(const ScanConfiguration& config) {
    if (m_initialized.load()) {
        return true;
    }
    
    m_config = config;
    
    // 检查 Spotlight 可用性
    if (!checkSpotlightAvailability()) {
        std::cerr << "❌ Spotlight 不可用" << std::endl;
        return false;
    }
    
    // 初始化进度管理器
    m_progress_manager = progress::createProgressManager();
    if (!m_progress_manager->initialize(config)) {
        std::cerr << "⚠️  进度管理器初始化失败，将使用基础模式" << std::endl;
        m_progress_manager.reset();
    } else {
        std::cout << "✅ 进度管理器初始化完成" << std::endl;
    }
    
    // 初始化系统负载监控
    if (!initializeSystemMonitoring()) {
        std::cerr << "⚠️  系统监控初始化失败，将使用基础模式" << std::endl;
        // 不是致命错误，可以继续
    }
    
    // 初始化 FSEvents（用于增量更新）
    if (!initializeFSEvents()) {
        std::cerr << "⚠️  FSEvents 初始化失败，增量更新不可用" << std::endl;
        // 不是致命错误，可以继续
    }
    
    m_initialized.store(true);
    
    std::cout << "✅ macOS 零扫描提供者初始化完成" << std::endl;
    std::cout << "   📋 平台信息: " << getPlatformInfo() << std::endl;
    
    return true;
}

void MacOSZeroScanProvider::shutdown() {
    if (!m_initialized.load()) {
        return;
    }
    
    m_scanning.store(false);
    
    // 停止 FSEvents
    if (m_fsevents_stream) {
        FSEventStreamStop((FSEventStreamRef)m_fsevents_stream);
        FSEventStreamInvalidate((FSEventStreamRef)m_fsevents_stream);
        FSEventStreamRelease((FSEventStreamRef)m_fsevents_stream);
        m_fsevents_stream = nullptr;
    }
    
    // 停止 MDQuery
    if (m_mdquery) {
        MDQueryStop((MDQueryRef)m_mdquery);
        CFRelease((MDQueryRef)m_mdquery);
        m_mdquery = nullptr;
    }
    
    // 等待线程结束
    if (m_fsevents_thread && m_fsevents_thread->joinable()) {
        m_fsevents_thread->join();
    }
    
    if (m_worker_thread && m_worker_thread->joinable()) {
        m_worker_thread->join();
    }
    
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
    
    m_file_callback = callback;
    m_scanning.store(true);
    
    std::cout << "🚀 开始 Everything 式零扫描..." << std::endl;
    
    auto startTime = std::chrono::high_resolution_clock::now();
    m_stats.start_time = std::chrono::system_clock::now();
    
    bool success = executeMDQuery(callback);
    
    auto endTime = std::chrono::high_resolution_clock::now();
    m_stats.end_time = std::chrono::system_clock::now();
    m_stats.scan_duration_ms = std::chrono::duration_cast<std::chrono::milliseconds>(
        endTime - startTime
    ).count();
    
    if (m_stats.scan_duration_ms > 0) {
        m_stats.files_per_second = (m_stats.total_files * 1000) / m_stats.scan_duration_ms;
    }
    
    m_scanning.store(false);
    
    if (success) {
        std::cout << "🎉 零扫描完成！性能数据:" << std::endl;
        std::cout << "   📁 文件数量: " << m_stats.total_files << std::endl;
        std::cout << "   📊 扫描速度: " << m_stats.files_per_second << " 文件/秒" << std::endl;
        std::cout << "   ⏱️  用时: " << m_stats.scan_duration_ms << "ms" << std::endl;
        
        if (m_stats.files_per_second > 10000) {
            std::cout << "   🏆 达到 Everything 级别性能！" << std::endl;
        }
    }
    
    return success;
}

bool MacOSZeroScanProvider::subscribeToChanges(
    std::function<void(const FileChangeEvent&)> callback) {
    
    if (!m_initialized.load()) {
        return false;
    }
    
    m_change_callback = callback;
    
    // FSEvents 应该已经在 initialize 中启动
    return m_fsevents_stream != nullptr;
}

void MacOSZeroScanProvider::unsubscribeFromChanges() {
    m_change_callback = nullptr;
}

ScanStatistics MacOSZeroScanProvider::getStatistics() const {
    std::lock_guard<std::mutex> lock(m_mutex);
    return m_stats;
}

bool MacOSZeroScanProvider::isAvailable() const {
    return checkSpotlightAvailability();
}

std::string MacOSZeroScanProvider::getPlatformInfo() const {
    std::stringstream ss;
    ss << "macOS " << getOSVersion() << " Spotlight MDQuery";
    
    if (checkAPFSAvailability()) {
        ss << " + APFS";
    }
    
    return ss.str();
}

void MacOSZeroScanProvider::updateConfiguration(const ScanConfiguration& config) {
    std::lock_guard<std::mutex> lock(m_mutex);
    m_config = config;
}

void MacOSZeroScanProvider::clearCache() {
    std::lock_guard<std::mutex> lock(m_mutex);
    m_cache.records.clear();
    m_cache.valid = false;
}

bool MacOSZeroScanProvider::warmupCache() {
    // Spotlight 索引本身就是系统级缓存，无需额外预热
    return true;
}

void MacOSZeroScanProvider::pause() {
    m_paused.store(true);
}

void MacOSZeroScanProvider::resume() {
    m_paused.store(false);
    m_cv.notify_all();
}

void MacOSZeroScanProvider::setThrottleLevel(int level) {
    m_throttle_level.store(std::clamp(level, 0, 100));
}

// 私有方法实现

bool MacOSZeroScanProvider::initializeSystemMonitoring() {
    // 初始化系统负载监控参数
    m_max_mds_cpu_percent = 50.0;  // mds进程CPU使用率上限
    m_current_batch_size = 0;
    
    // 检查是否能获取系统负载信息
    return checkSystemLoad();
}

bool MacOSZeroScanProvider::executeBatchQuery(const std::string& queryString, 
                                              std::function<void(const UnifiedFileRecord&)> callback,
                                              size_t maxResults) {
    @autoreleasepool {
        // 创建批次查询
        NSString* nsQueryString = [NSString stringWithUTF8String:queryString.c_str()];
        
        MDQueryRef query = MDQueryCreate(
            kCFAllocatorDefault,
            (__bridge CFStringRef)nsQueryString,
            NULL,
            NULL
        );
        
        if (!query) {
            std::cerr << "❌ 无法创建批次查询" << std::endl;
            return false;
        }
        
        // 执行同步查询以控制批次大小
        Boolean success = MDQueryExecute(query, kMDQuerySynchronous);
        
        if (!success) {
            std::cerr << "❌ 批次查询执行失败" << std::endl;
            CFRelease(query);
            return false;
        }
        
        CFIndex resultCount = MDQueryGetResultCount(query);
        CFIndex processCount = std::min(static_cast<CFIndex>(maxResults), resultCount);
        
        std::cout << "📈 批次查询结果: " << resultCount << " 个，将处理 " << processCount << " 个" << std::endl;
        
        m_current_batch_size = 0;
        
        for (CFIndex i = 0; i < processCount && m_scanning.load(); ++i) {
            // 定期检查系统负载
            if (i % 500 == 0 && !checkSystemLoad()) {
                std::cout << "⚠️  系统负载过高，提前结束批次" << std::endl;
                break;
            }
            
            // 定期更新进度管理器
            if (i % 100 == 0 && m_progress_manager) {
                m_progress_manager->updateBatchProgress(m_current_batch_size, static_cast<size_t>(resultCount));
            }
            
            MDItemRef item = (MDItemRef)MDQueryGetResultAtIndex(query, i);
            if (!item) continue;
            
            UnifiedFileRecord record = createRecordFromMDItem(item);
            
            // 检查过滤条件
            if (!shouldIncludeFile(record.path)) {
                continue;
            }
            
            if (callback) {
                callback(record);
            }
            
            m_current_batch_size++;
            
            // 微小延迟，减少系统压力
            if (i % 100 == 0) {
                std::this_thread::sleep_for(std::chrono::microseconds(50));
            }
        }
        
        CFRelease(query);
        
        std::cout << "✅ 批次处理完成，实际处理 " << m_current_batch_size << " 个文件" << std::endl;
        return true;
    }
}

bool MacOSZeroScanProvider::checkSystemLoad() const {
    @autoreleasepool {
        // 检查mds进程CPU使用率
        NSTask* task = [[NSTask alloc] init];
        task.launchPath = @"/usr/bin/top";
        task.arguments = @[@"-l", @"1", @"-stats", @"pid,command,cpu"];
        
        NSPipe* pipe = [NSPipe pipe];
        task.standardOutput = pipe;
        task.standardError = pipe;
        
        @try {
            [task launch];
            [task waitUntilExit];
            
            if (task.terminationStatus != 0) {
                return true;  // 如果无法检查，假设系统正常
            }
            
            NSData* data = [[pipe fileHandleForReading] readDataToEndOfFile];
            NSString* output = [[NSString alloc] initWithData:data encoding:NSUTF8StringEncoding];
            
            // 解析mds进程CPU使用率
            NSArray* lines = [output componentsSeparatedByString:@"\n"];
            for (NSString* line in lines) {
                if ([line containsString:@"mds"] && ![line containsString:@"mdsync"]) {
                    NSArray* components = [line componentsSeparatedByCharactersInSet:
                                         [NSCharacterSet whitespaceCharacterSet]];
                    
                    // 查找CPU使用率列
                    for (NSString* component in components) {
                        if ([component hasSuffix:@"%"]) {
                            double cpuUsage = [component doubleValue];
                            if (cpuUsage > m_max_mds_cpu_percent) {
                                std::cout << "⚠️  mds CPU使用率: " << cpuUsage << "% > " 
                                          << m_max_mds_cpu_percent << "%" << std::endl;
                                return false;
                            }
                            break;
                        }
                    }
                    break;
                }
            }
            
        } @catch (NSException* exception) {
            // 如果检查失败，假设系统正常
            return true;
        }
        
        return true;  // 系统负载正常
    }
}

bool MacOSZeroScanProvider::initializeFSEvents() {
    // FSEvents 初始化将在后续实现
    // 这里先返回 true 以允许系统继续工作
    return true;
}

bool MacOSZeroScanProvider::executeMDQuery(std::function<void(const UnifiedFileRecord&)> callback) {
    std::cout << "🔍 启动智能批量扫描（支持断点续传）..." << std::endl;
    
    // 定义扫描策略：按文件类型分批查询
    std::vector<std::string> queryBatches = {
        "kMDItemKind == 'Folder'",                    // 先扫描目录
        "kMDItemContentType LIKE 'text/*'",           // 文本文件
        "kMDItemContentType LIKE 'image/*'",          // 图片文件
        "kMDItemContentType LIKE 'application/*'",    // 应用程序文件
        "kMDItemContentType LIKE 'video/*'",          // 视频文件
        "kMDItemContentType LIKE 'audio/*'"           // 音频文件
    };
    
    std::vector<std::string> queryTypeNames = {
        "folders", "text", "images", "applications", "videos", "audio"
    };
    
    // 检查是否可以从断点恢复
    std::string session_id;
    size_t start_batch_index = 0;
    
    if (m_progress_manager && m_progress_manager->hasValidCheckpoint()) {
        auto resumed_progress = m_progress_manager->tryResumeFromCheckpoint();
        if (resumed_progress.has_value()) {
            start_batch_index = resumed_progress->current_batch_index;
            session_id = resumed_progress->session.session_id;
            std::cout << "🔄 从断点恢复扫描，会话ID: " << session_id << std::endl;
            std::cout << "   📍 从批次 " << (start_batch_index + 1) << " 开始" << std::endl;
        }
    }
    
    // 如果没有恢复，启动新会话
    if (session_id.empty() && m_progress_manager) {
        session_id = m_progress_manager->startNewSession("full", queryTypeNames);
        std::cout << "🆕 启动新扫描会话: " << session_id << std::endl;
    }
    
    size_t totalProcessed = 0;
    const size_t maxBatchSize = 5000;  // 每批最大处理5000个文件
    
    for (size_t batchIndex = start_batch_index; batchIndex < queryBatches.size() && m_scanning.load(); ++batchIndex) {
        // 检查是否应该跳过已完成的批次
        if (m_progress_manager && m_progress_manager->shouldSkipQueryType(queryTypeNames[batchIndex])) {
            std::cout << "⏭️  跳过已完成的批次: " << queryTypeNames[batchIndex] << std::endl;
            continue;
        }
        
        std::cout << "📂 批次 " << (batchIndex + 1) << "/" << queryBatches.size() 
                  << " (" << queryTypeNames[batchIndex] << "): " << queryBatches[batchIndex] << std::endl;
        
        // 开始批次进度跟踪
        if (m_progress_manager) {
            m_progress_manager->startBatch(batchIndex, queryTypeNames[batchIndex], queryBatches[batchIndex]);
        }
        
        // 检查系统负载
        if (!checkSystemLoad()) {
            std::cout << "⚠️  系统负载过高，暂停扫描（进度已保存）" << std::endl;
            if (m_progress_manager) {
                m_progress_manager->saveCheckpoint();
            }
            break;
        }
        
        bool batchSuccess = executeBatchQuery(queryBatches[batchIndex], callback, maxBatchSize);
        if (!batchSuccess) {
            std::cerr << "❌ 批次 " << (batchIndex + 1) << " 执行失败" << std::endl;
            if (m_progress_manager) {
                m_progress_manager->recordError("Batch " + std::to_string(batchIndex + 1) + " execution failed");
            }
            continue;
        }
        
        // 完成批次进度跟踪
        if (m_progress_manager) {
            // 简单的性能统计（实际项目中可以更精确地测量）
            double cpu_usage = getCurrentCPUUsage();
            size_t memory_usage = getCurrentMemoryUsage();
            m_progress_manager->completeBatch(cpu_usage, memory_usage);
            
            // 显示进度
            double completion = m_progress_manager->getCompletionPercentage();
            uint64_t remaining_time = m_progress_manager->getEstimatedRemainingTime();
            std::cout << "   📊 进度: " << std::fixed << std::setprecision(1) << (completion * 100.0) << "%";
            if (remaining_time > 0) {
                std::cout << ", 预计剩余: " << (remaining_time / 1000) << "秒";
            }
            std::cout << std::endl;
        }
        
        totalProcessed += m_current_batch_size;
        
        // 批次间延迟，给系统喘息时间
        if (batchIndex < queryBatches.size() - 1) {
            std::this_thread::sleep_for(std::chrono::milliseconds(200)); // 稍微增加延迟确保进度保存
        }
        
        // 检查是否达到最大文件数限制
        if (m_config.max_results > 0 && totalProcessed >= m_config.max_results) {
            std::cout << "📋 达到最大文件数限制: " << totalProcessed << std::endl;
            break;
        }
    }
    
    // 完成扫描会话
    if (m_progress_manager) {
        m_progress_manager->completeSession();
    }
    
    std::cout << "✅ 智能扫描完成，共处理 " << totalProcessed << " 个文件" << std::endl;
    if (!session_id.empty()) {
        std::cout << "   🎯 会话ID: " << session_id << std::endl;
    }
    return true;
}

// 废弃的方法，已被新的批量处理替代
void MacOSZeroScanProvider::processMDQueryResults(void* mdquery) {
    // 这个方法已被 executeBatchQuery 替代，不再使用
    std::cout << "⚠️  processMDQueryResults 已废弃，使用 executeBatchQuery" << std::endl;
}

UnifiedFileRecord MacOSZeroScanProvider::createRecordFromMDItem(void* mditem) {
    @autoreleasepool {
        MDItemRef item = (MDItemRef)mditem;
        UnifiedFileRecord record;
        
        // 优化路径获取：使用预分配缓冲区减少内存分配
        CFStringRef pathRef = (CFStringRef)MDItemCopyAttribute(item, kMDItemPath);
        if (pathRef) {
            const char* pathCStr = CFStringGetCStringPtr(pathRef, kCFStringEncodingUTF8);
            if (pathCStr) {
                record.path.assign(pathCStr);
            } else {
                // 使用栈上缓冲区减少堆分配
                constexpr size_t STACK_BUFFER_SIZE = 1024;
                char stackBuffer[STACK_BUFFER_SIZE];
                
                CFIndex length = CFStringGetLength(pathRef);
                CFIndex maxSize = CFStringGetMaximumSizeForEncoding(length, kCFStringEncodingUTF8) + 1;
                
                if (static_cast<size_t>(maxSize) <= STACK_BUFFER_SIZE) {
                    if (CFStringGetCString(pathRef, stackBuffer, maxSize, kCFStringEncodingUTF8)) {
                        record.path.assign(stackBuffer);
                    }
                } else {
                    // 只有在必要时才使用堆分配
                    std::unique_ptr<char[]> buffer(new char[maxSize]);
                    if (CFStringGetCString(pathRef, buffer.get(), maxSize, kCFStringEncodingUTF8)) {
                        record.path.assign(buffer.get());
                    }
                }
            }
            CFRelease(pathRef);
        }
        
        // 优化文件名和扩展名提取：减少字符串操作
        if (!record.path.empty()) {
            const char* pathCStr = record.path.c_str();
            const char* lastSlash = strrchr(pathCStr, '/');
            
            if (lastSlash && *(lastSlash + 1) != '\0') {
                record.name.assign(lastSlash + 1);
                
                const char* lastDot = strrchr(lastSlash + 1, '.');
                if (lastDot && lastDot > lastSlash + 1) {
                    record.extension.assign(lastDot);
                }
            } else {
                record.name = record.path;
                
                const char* lastDot = strrchr(pathCStr, '.');
                if (lastDot && lastDot > pathCStr) {
                    record.extension.assign(lastDot);
                }
            }
        }
        
        // 获取文件大小
        CFNumberRef sizeRef = (CFNumberRef)MDItemCopyAttribute(item, kMDItemFSSize);
        if (sizeRef) {
            CFNumberGetValue(sizeRef, kCFNumberLongLongType, &record.size);
            CFRelease(sizeRef);
        }
        
        // 获取修改时间
        CFDateRef dateRef = (CFDateRef)MDItemCopyAttribute(item, kMDItemFSContentChangeDate);
        if (dateRef) {
            CFAbsoluteTime absTime = CFDateGetAbsoluteTime(dateRef);
            auto timeInterval = std::chrono::duration_cast<std::chrono::seconds>(
                std::chrono::duration<double>(absTime + kCFAbsoluteTimeIntervalSince1970)
            );
            record.modified_time = std::chrono::system_clock::time_point(timeInterval);
            CFRelease(dateRef);
        }
        
        // 判断是否为目录
        CFStringRef kindRef = (CFStringRef)MDItemCopyAttribute(item, kMDItemKind);
        if (kindRef) {
            CFStringRef folderKind = CFSTR("Folder");
            record.is_directory = CFStringCompare(kindRef, folderKind, 0) == kCFCompareEqualTo;
            CFRelease(kindRef);
        }
        
        return record;
    }
}

// 新的查询策略不再使用这个方法，保留用于向后兼容
std::string MacOSZeroScanProvider::getQueryString() const {
    // 默认返回基本查询，但现在使用分批查询策略
    return "kMDItemKind == 'Folder'";
}

bool MacOSZeroScanProvider::shouldIncludeFile(const std::string& path) const {
    // 检查包含路径
    if (!m_config.include_paths.empty()) {
        bool matchesInclude = false;
        for (const auto& includePath : m_config.include_paths) {
            if (path.find(includePath) == 0) {
                matchesInclude = true;
                break;
            }
        }
        if (!matchesInclude) {
            return false;
        }
    }
    
    // 检查排除路径
    for (const auto& excludePath : m_config.exclude_paths) {
        if (path.find(excludePath) == 0) {
            return false;
        }
    }
    
    // 检查排除模式（简化正则表达式处理）
    for (const auto& pattern : m_config.exclude_patterns) {
        try {
            if (std::regex_search(path, std::regex(pattern))) {
                return false;
            }
        } catch (const std::exception&) {
            // 忽略正则表达式错误
            continue;
        }
    }
    
    return true;
}

void MacOSZeroScanProvider::updateStatistics() {
    std::lock_guard<std::mutex> lock(m_mutex);
    m_stats.memory_usage_mb = getCurrentMemoryUsage();
    m_stats.cpu_usage_percent = getCurrentCPUUsage();
    
    // 计算平均性能
    auto now = std::chrono::high_resolution_clock::now();
    auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(
        now - std::chrono::time_point_cast<std::chrono::milliseconds>(
            std::chrono::high_resolution_clock::time_point(
                std::chrono::duration_cast<std::chrono::high_resolution_clock::duration>(
                    m_stats.start_time.time_since_epoch()
                )
            )
        )
    ).count();
    
    if (elapsed > 0) {
        m_stats.files_per_second = (m_stats.total_files * 1000) / elapsed;
        
        // 输出实时统计
        if (m_stats.total_files % 10000 == 0 && m_stats.total_files > 0) {
            std::cout << "📊 实时统计: " << m_stats.total_files << " 文件, "
                      << m_stats.files_per_second << " 文件/秒, "
                      << m_stats.memory_usage_mb << "MB内存" << std::endl;
        }
    }
}

size_t MacOSZeroScanProvider::getCurrentMemoryUsage() const {
    struct task_basic_info info;
    mach_msg_type_number_t size = sizeof(info);
    kern_return_t kerr = task_info(mach_task_self(), TASK_BASIC_INFO, (task_info_t)&info, &size);
    
    if (kerr == KERN_SUCCESS) {
        return info.resident_size / (1024 * 1024);  // 转换为 MB
    }
    
    return 0;
}

double MacOSZeroScanProvider::getCurrentCPUUsage() const {
    struct task_basic_info info;
    mach_msg_type_number_t size = sizeof(info);
    kern_return_t kerr = task_info(mach_task_self(), TASK_BASIC_INFO, (task_info_t)&info, &size);
    
    if (kerr != KERN_SUCCESS) {
        return 0.0;
    }
    
    // 简化的 CPU 使用率计算（基于系统时间）
    static std::chrono::steady_clock::time_point lastTime = std::chrono::steady_clock::now();
    static double lastCpuTime = 0.0;
    
    auto currentTime = std::chrono::steady_clock::now();
    double currentCpuTime = info.user_time.seconds + info.user_time.microseconds / 1000000.0 +
                           info.system_time.seconds + info.system_time.microseconds / 1000000.0;
    
    auto timeDiff = std::chrono::duration<double>(currentTime - lastTime).count();
    double cpuUsage = 0.0;
    
    if (timeDiff > 0.0 && lastCpuTime > 0.0) {
        cpuUsage = ((currentCpuTime - lastCpuTime) / timeDiff) * 100.0;
    }
    
    lastTime = currentTime;
    lastCpuTime = currentCpuTime;
    
    return std::min(100.0, std::max(0.0, cpuUsage));
}

bool MacOSZeroScanProvider::checkSpotlightAvailability() const {
    @autoreleasepool {
        // 检查系统版本（Spotlight 在 macOS 10.4+ 中可用）
        NSProcessInfo* processInfo = [NSProcessInfo processInfo];
        NSOperatingSystemVersion version = [processInfo operatingSystemVersion];
        if (version.majorVersion < 10 || (version.majorVersion == 10 && version.minorVersion < 4)) {
            std::cerr << "❌ macOS 版本太旧，不支持 Spotlight" << std::endl;
            return false;
        }
        
        // 检查 Spotlight 系统服务状态
        NSTask* task = [[NSTask alloc] init];
        task.launchPath = @"/usr/bin/mdutil";
        task.arguments = @[@"-s", @"/"];
        
        NSPipe* pipe = [NSPipe pipe];
        task.standardOutput = pipe;
        task.standardError = pipe;
        
        @try {
            [task launch];
            [task waitUntilExit];
            
            if (task.terminationStatus != 0) {
                std::cerr << "❌ mdutil 命令执行失败" << std::endl;
                return false;
            }
            
            NSData* data = [[pipe fileHandleForReading] readDataToEndOfFile];
            NSString* output = [[NSString alloc] initWithData:data encoding:NSUTF8StringEncoding];
            
            // 检查索引状态
            if ([output containsString:@"Indexing disabled"]) {
                std::cerr << "❌ Spotlight 索引已禁用" << std::endl;
                return false;
            }
            
        } @catch (NSException* exception) {
            std::cerr << "❌ 检查 Spotlight 状态时出错: " 
                      << [[exception description] UTF8String] << std::endl;
            return false;
        }
        
        // 检查文件系统访问权限
        if (access("/", R_OK) != 0) {
            std::cerr << "❌ 没有文件系统读取权限" << std::endl;
            return false;
        }
        
        // 尝试创建测试查询
        MDQueryRef testQuery = MDQueryCreate(
            kCFAllocatorDefault,
            CFSTR("kMDItemKind == 'Folder'"),
            NULL,
            NULL
        );
        
        if (!testQuery) {
            std::cerr << "❌ 无法创建 MDQuery" << std::endl;
            return false;
        }
        
        // 测试执行查询
        Boolean testResult = MDQueryExecute(testQuery, kMDQuerySynchronous);
        CFIndex testCount = MDQueryGetResultCount(testQuery);
        
        CFRelease(testQuery);
        
        if (!testResult) {
            std::cerr << "❌ MDQuery 测试执行失败" << std::endl;
            return false;
        }
        
        if (testCount == 0) {
            std::cerr << "⚠️  Spotlight 索引可能为空或正在构建中" << std::endl;
            // 不返回 false，因为索引可能正在构建
        }
        
        std::cout << "✅ Spotlight 可用，测试查询返回 " << testCount << " 个结果" << std::endl;
        return true;
    }
}

bool MacOSZeroScanProvider::checkAPFSAvailability() const {
    // 检查当前系统是否支持 APFS
    // 这里简化实现，实际可以检查文件系统类型
    return true;  // macOS 10.13+ 一般都支持 APFS
}

std::string MacOSZeroScanProvider::getOSVersion() const {
    @autoreleasepool {
        NSProcessInfo* processInfo = [NSProcessInfo processInfo];
        NSOperatingSystemVersion version = [processInfo operatingSystemVersion];
        
        std::stringstream ss;
        ss << version.majorVersion << "." << version.minorVersion << "." << version.patchVersion;
        return ss.str();
    }
}

} // namespace zero_scan
} // namespace linch_connector

#endif // __APPLE__