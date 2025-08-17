/**
 * 事件防抖器 - 根本性解决方案
 * 
 * 基于Gemini的深度分析，实现事件合并/防抖机制
 * 解决文件保存时产生的"事件风暴"问题
 */

#pragma once

#include <string>
#include <unordered_map>
#include <chrono>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <functional>

namespace linch_connector {

/**
 * 防抖器配置
 */
struct DebouncerConfig {
    std::chrono::milliseconds debounceDelay{100};  // 防抖延迟
    size_t maxPendingEvents{1000};                 // 最大待处理事件数
    bool enableCoalescing{true};                   // 启用事件合并
};

/**
 * 待处理事件信息
 */
struct PendingEvent {
    FileEvent event;
    std::chrono::steady_clock::time_point scheduledTime;
    bool isCoalesced{false};
    
    // 默认构造函数
    PendingEvent() : event(FileEventType::CREATED, ""), isCoalesced(false) {}
    
    // 带参数构造函数
    PendingEvent(const FileEvent& e, std::chrono::steady_clock::time_point st, bool coalesced = false)
        : event(e), scheduledTime(st), isCoalesced(coalesced) {}
};

/**
 * 事件防抖器
 * 
 * 核心思想：
 * 1. 不立即处理事件，而是延迟一小段时间
 * 2. 如果在延迟期间收到同一文件的新事件，重置计时器
 * 3. 只有当计时器真正到期时，才处理该文件的最终事件
 * 4. 这将多个抖动事件合并成一个稳定事件
 */
class EventDebouncer {
public:
    using EventHandler = std::function<void(const FileEvent&)>;
    
    explicit EventDebouncer(const DebouncerConfig& config = {});
    ~EventDebouncer();
    
    /**
     * 启动防抖器
     */
    bool start(EventHandler handler);
    
    /**
     * 停止防抖器
     */
    void stop();
    
    /**
     * 提交事件进行防抖处理
     * 
     * @param event 原始事件
     * @return true 如果事件被接受，false 如果被拒绝（队列满等）
     */
    bool submitEvent(const FileEvent& event);
    
    /**
     * 获取统计信息
     */
    struct Statistics {
        size_t eventsReceived{0};
        size_t eventsProcessed{0};
        size_t eventsCoalesced{0};
        size_t currentPending{0};
        double coalescingRatio{0.0};
    };
    
    Statistics getStatistics() const;
    
private:
    void processingLoop();
    void processExpiredEvents();
    std::string getFileKey(const std::string& path) const;
    
    DebouncerConfig m_config;
    EventHandler m_handler;
    
    // 线程控制
    std::atomic<bool> m_running{false};
    std::thread m_processingThread;
    
    // 事件存储
    mutable std::mutex m_eventsMutex;
    std::unordered_map<std::string, PendingEvent> m_pendingEvents;
    std::condition_variable m_eventsCV;
    
    // 统计信息
    mutable std::mutex m_statsMutex;
    Statistics m_stats;
};

} // namespace linch_connector