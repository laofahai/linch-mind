/**
 * 事件防抖器实现 - 根本性解决方案
 */

#include "event_debouncer.hpp"
#include <iostream>
#include <algorithm>

namespace linch_connector {

EventDebouncer::EventDebouncer(const DebouncerConfig& config) 
    : m_config(config) {
}

EventDebouncer::~EventDebouncer() {
    stop();
}

bool EventDebouncer::start(EventHandler handler) {
    if (m_running || !handler) {
        return false;
    }
    
    m_handler = std::move(handler);
    m_running = true;
    
    // 启动处理线程
    m_processingThread = std::thread(&EventDebouncer::processingLoop, this);
    
    std::cout << "🔄 事件防抖器已启动 (延迟: " << m_config.debounceDelay.count() << "ms)" << std::endl;
    return true;
}

void EventDebouncer::stop() {
    if (!m_running) {
        return;
    }
    
    m_running = false;
    m_eventsCV.notify_all();
    
    if (m_processingThread.joinable()) {
        m_processingThread.join();
    }
    
    // 处理剩余的待处理事件
    std::lock_guard<std::mutex> lock(m_eventsMutex);
    for (const auto& [path, pendingEvent] : m_pendingEvents) {
        if (m_handler) {
            m_handler(pendingEvent.event);
        }
    }
    m_pendingEvents.clear();
    
    std::cout << "⏹️ 事件防抖器已停止" << std::endl;
}

bool EventDebouncer::submitEvent(const FileEvent& event) {
    if (!m_running) {
        return false;
    }
    
    std::lock_guard<std::mutex> lock(m_eventsMutex);
    
    // 检查队列大小限制
    if (m_pendingEvents.size() >= m_config.maxPendingEvents) {
        std::lock_guard<std::mutex> statsLock(m_statsMutex);
        // 统计被拒绝的事件
        return false;
    }
    
    std::string fileKey = getFileKey(event.path);
    auto now = std::chrono::steady_clock::now();
    auto scheduledTime = now + m_config.debounceDelay;
    
    // 检查是否已有该文件的待处理事件
    auto it = m_pendingEvents.find(fileKey);
    if (it != m_pendingEvents.end()) {
        // 合并事件：使用最新的事件，重置计时器
        it->second.event = event;
        it->second.scheduledTime = scheduledTime;
        it->second.isCoalesced = true;
        
        std::lock_guard<std::mutex> statsLock(m_statsMutex);
        m_stats.eventsCoalesced++;
    } else {
        // 新文件事件
        m_pendingEvents[fileKey] = PendingEvent(event, scheduledTime, false);
    }
    
    // 更新统计
    {
        std::lock_guard<std::mutex> statsLock(m_statsMutex);
        m_stats.eventsReceived++;
        m_stats.currentPending = m_pendingEvents.size();
    }
    
    // 通知处理线程
    m_eventsCV.notify_one();
    return true;
}

EventDebouncer::Statistics EventDebouncer::getStatistics() const {
    std::lock_guard<std::mutex> lock(m_statsMutex);
    Statistics stats = m_stats;
    
    // 计算合并率
    if (stats.eventsReceived > 0) {
        stats.coalescingRatio = static_cast<double>(stats.eventsCoalesced) / stats.eventsReceived;
    }
    
    return stats;
}

void EventDebouncer::processingLoop() {
    while (m_running) {
        std::unique_lock<std::mutex> lock(m_eventsMutex);
        
        // 等待事件或超时检查
        m_eventsCV.wait_for(lock, std::chrono::milliseconds(50), [this] {
            return !m_pendingEvents.empty() || !m_running;
        });
        
        if (!m_running) {
            break;
        }
        
        processExpiredEvents();
    }
}

void EventDebouncer::processExpiredEvents() {
    // 注意：调用此方法时已持有 m_eventsMutex 锁
    
    auto now = std::chrono::steady_clock::now();
    std::vector<std::string> expiredKeys;
    std::vector<FileEvent> expiredEvents;
    
    // 找到所有到期的事件
    for (const auto& [path, pendingEvent] : m_pendingEvents) {
        if (pendingEvent.scheduledTime <= now) {
            expiredKeys.push_back(path);
            expiredEvents.push_back(pendingEvent.event);
        }
    }
    
    // 移除到期的事件
    for (const auto& key : expiredKeys) {
        m_pendingEvents.erase(key);
    }
    
    // 更新统计
    {
        std::lock_guard<std::mutex> statsLock(m_statsMutex);
        m_stats.eventsProcessed += expiredEvents.size();
        m_stats.currentPending = m_pendingEvents.size();
    }
    
    // 释放锁后处理事件（避免在回调中持有锁）
    m_eventsMutex.unlock();
    
    // 处理到期的事件
    for (const auto& event : expiredEvents) {
        try {
            if (m_handler) {
                m_handler(event);
            }
        } catch (const std::exception& e) {
            std::cerr << "❌ 事件处理器异常: " << e.what() << std::endl;
        }
    }
    
    // 重新获取锁以继续循环
    m_eventsMutex.lock();
}

std::string EventDebouncer::getFileKey(const std::string& path) const {
    // 使用绝对路径作为键，确保同一文件的不同表示被正确合并
    // 这里可以添加路径规范化逻辑
    return path;
}

} // namespace linch_connector