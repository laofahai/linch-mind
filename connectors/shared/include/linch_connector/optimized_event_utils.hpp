#pragma once

#include "connector_event.hpp"
#include <string_view>
#include <memory_resource>
#include <filesystem>
#include <chrono>
#include <iostream>

namespace linch_connector {
namespace optimization {

/**
 * 高性能事件工具类
 * 提供零拷贝事件构造和优化的内存管理
 */
class EventUtils {
public:
    /**
     * 剪贴板事件快速构造 - 零拷贝版本
     */
    static ConnectorEvent createClipboardEvent(std::string content) {
        size_t contentLength = content.length();
        
        // 使用emplace避免中间JSON对象构造
        return ConnectorEvent::emplace(
            "clipboard", 
            "changed",
            json{
                {"content", std::move(content)},     // 移动语义，避免拷贝
                {"content_length", contentLength},
                {"content_type", "text"}
            }
        );
    }
    
    /**
     * 文件系统事件快速构造 - 零拷贝版本  
     */
    static ConnectorEvent createFilesystemEvent(
        std::string filePath,
        std::string_view eventType,
        bool isDirectory = false,
        size_t fileSize = 0,
        std::string oldPath = "") {
        
        // 预计算路径组件，避免重复解析
        std::filesystem::path path(filePath);
        std::string fileName = path.filename().string();
        std::string extension = path.extension().string();
        std::string directory = path.parent_path().string();
        
        // 构造事件数据
        json eventData = {
            {"file_path", std::move(filePath)},       // 移动原始路径
            {"file_name", std::move(fileName)},
            {"extension", std::move(extension)},
            {"directory", std::move(directory)},
            {"is_directory", isDirectory}
        };
        
        // 条件性添加字段，避免不必要的JSON操作
        if (!isDirectory && fileSize > 0) {
            eventData["size"] = fileSize;
        }
        
        if (!oldPath.empty()) {
            eventData["old_path"] = std::move(oldPath);
        }
        
        return ConnectorEvent::create(
            "filesystem",
            std::string(eventType),
            std::move(eventData)
        );
    }
    
    /**
     * 批量事件预分配容器
     */
    static std::vector<ConnectorEvent> createEventBatch(size_t expectedSize) {
        std::vector<ConnectorEvent> events;
        events.reserve(expectedSize);  // 预分配内存避免重分配
        return events;
    }
};

/**
 * 事件回调优化包装器
 * 提供统一的性能监控和错误处理
 */
template<typename CallbackType>
class OptimizedCallback {
private:
    CallbackType m_callback;
    mutable size_t m_callCount{0};
    mutable std::chrono::nanoseconds m_totalTime{0};
    
public:
    OptimizedCallback(CallbackType callback) : m_callback(std::move(callback)) {}
    
    void operator()(ConnectorEvent&& event) const {
        auto start = std::chrono::high_resolution_clock::now();
        
        try {
            m_callback(std::move(event));
        } catch (const std::exception& e) {
            // 记录错误但不抛出，保持性能
            std::cerr << "Event callback error: " << e.what() << std::endl;
        }
        
        auto end = std::chrono::high_resolution_clock::now();
        m_totalTime += std::chrono::duration_cast<std::chrono::nanoseconds>(end - start);
        ++m_callCount;
    }
    
    // 性能统计
    double getAverageLatencyMs() const {
        return m_callCount > 0 ? 
            (m_totalTime.count() / 1000000.0) / m_callCount : 0.0;
    }
    
    size_t getCallCount() const { return m_callCount; }
};

/**
 * 创建优化的回调包装器
 */
template<typename CallbackType>
OptimizedCallback<CallbackType> makeOptimizedCallback(CallbackType callback) {
    return OptimizedCallback<CallbackType>(std::move(callback));
}

} // namespace optimization
} // namespace linch_connector