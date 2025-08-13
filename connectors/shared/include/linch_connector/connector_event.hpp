#pragma once

#include <string>
#include <chrono>
#include <nlohmann/json.hpp>

namespace linch_connector {

using json = nlohmann::json;

/**
 * 统一连接器事件结构
 * 所有连接器都使用此结构发送事件到daemon
 */
struct ConnectorEvent {
    std::string connectorId;      // 连接器ID (例如: "clipboard", "filesystem")
    std::string eventType;        // 事件类型 (例如: "changed", "created", "modified", "deleted")
    json eventData;              // 事件数据 (连接器特定的数据结构)
    std::chrono::system_clock::time_point timestamp;  // 事件时间戳
    json metadata;               // 可选元数据

    /**
     * 将事件转换为daemon API格式的JSON
     */
    json toJson() const {
        return json{
            {"connector_id", connectorId},
            {"event_type", eventType},
            {"event_data", eventData},
            {"timestamp", std::chrono::duration_cast<std::chrono::milliseconds>(
                timestamp.time_since_epoch()).count()},
            {"metadata", metadata}
        };
    }

    /**
     * 创建一个基本事件
     */
    static ConnectorEvent create(const std::string& connectorId, 
                                const std::string& eventType,
                                const json& eventData) {
        ConnectorEvent event;
        event.connectorId = connectorId;
        event.eventType = eventType;
        event.eventData = eventData;
        event.timestamp = std::chrono::system_clock::now();
        event.metadata = json::object();
        return event;
    }
};

/**
 * 连接器监控器统一接口
 * 所有类型的监控器都应实现此接口
 */
class IConnectorMonitor {
public:
    virtual ~IConnectorMonitor() = default;

    /**
     * 开始监控
     * @param callback 事件回调函数
     * @return 是否成功启动
     */
    virtual bool start(std::function<void(const ConnectorEvent&)> callback) = 0;

    /**
     * 停止监控
     */
    virtual void stop() = 0;

    /**
     * 检查是否正在监控
     */
    virtual bool isRunning() const = 0;

    /**
     * 获取监控器统计信息
     */
    struct Statistics {
        size_t eventsProcessed = 0;
        size_t eventsFiltered = 0;
        size_t pathsMonitored = 0;
        std::string platformInfo;
        std::chrono::system_clock::time_point startTime;
        bool isRunning = false;
    };

    virtual Statistics getStatistics() const = 0;
};

/**
 * 监控器配置基类
 */
struct MonitorConfig {
    std::string name;            // 配置名称
    json settings;               // 配置设置 (JSON格式，支持各种类型)
    
    template<typename T>
    T get(const std::string& key, const T& defaultValue = T{}) const {
        if (settings.contains(key)) {
            try {
                return settings[key].get<T>();
            } catch (...) {
                return defaultValue;
            }
        }
        return defaultValue;
    }

    void set(const std::string& key, const json& value) {
        settings[key] = value;
    }
};

} // namespace linch_connector