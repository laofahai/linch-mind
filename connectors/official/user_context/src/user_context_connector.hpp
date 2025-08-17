#pragma once

#include <linch_connector/base_connector.hpp>
#include <linch_connector/null_monitor.hpp>
#include <memory>
#include <thread>
#include <atomic>
#include <chrono>
#include <functional>
#include <mutex>
#include <string>
#include <vector>

#ifdef __OBJC__
@class NSWorkspace;
@class NSNotificationCenter;
@class NSRunningApplication;
#else
typedef struct objc_object NSWorkspace;
typedef struct objc_object NSNotificationCenter;
typedef struct objc_object NSRunningApplication;
#endif

namespace linch_connector {

/**
 * 用户情境感知类型
 */
enum class UserContextType {
    ACTIVE_APP_CHANGED,    // 前台应用切换
    WINDOW_FOCUS_CHANGED,  // 窗口焦点变化
    DEVICE_STATE_CHANGED,  // 设备状态变化（睡眠/唤醒/电源）
    NETWORK_STATE_CHANGED, // 网络环境变化
    SYSTEM_LOAD_UPDATE,    // 系统负载更新（轻量级）
    USER_ACTIVITY_SUMMARY  // 用户活动摘要（定期）
};

/**
 * 网络连接类型
 */
enum class NetworkType {
    UNKNOWN,
    WIFI,
    ETHERNET,
    CELLULAR,
    VPN,
    DISCONNECTED
};

/**
 * 设备电源状态
 */
enum class PowerState {
    UNKNOWN,
    ON_BATTERY,
    PLUGGED_IN,
    CHARGING,
    FULLY_CHARGED
};

/**
 * 用户活动模式
 */
enum class ActivityPattern {
    ACTIVE_WORK,     // 积极工作中
    LIGHT_USAGE,     // 轻度使用
    BACKGROUND_IDLE, // 后台待机
    AWAY,            // 离开
    FOCUSED_DEEP     // 专注深度工作
};


/**
 * 用户情境感知连接器
 * 
 * 核心职责：
 * 1. 用户活动监控（前台应用、窗口焦点、工作模式）
 * 2. 设备状态感知（电源、睡眠/唤醒、网络环境）
 * 3. 智能负载监控（整体负载、TOP进程、资源压力）
 * 
 * 设计特点：
 * - 事件驱动：使用NSWorkspace API，避免轮询
 * - 用户导向：理解"用户在干什么"而非"系统在干什么"
 * - 轻量级：<1% CPU占用，<50MB内存
 * - 隐私友好：数据本地处理，不收集敏感内容
 */
class UserContextConnector : public BaseConnector {
public:
    UserContextConnector();
    ~UserContextConnector() override = default;
    
    /**
     * 手动触发用户情境收集
     */
    void triggerUserContextCollection(UserContextType type = UserContextType::USER_ACTIVITY_SUMMARY);

protected:
    // 实现BaseConnector纯虚函数
    std::unique_ptr<IConnectorMonitor> createMonitor() override;
    bool loadConnectorConfig() override;
    bool onInitialize() override;
    bool onStart() override;
    void onStop() override;

private:
    
    // 配置参数
    int m_loadSamplingIntervalMinutes = 10; // 系统负载采样间隔（默认10分钟）
    int m_activitySummaryIntervalHours = 2; // 活动摘要生成间隔（默认2小时）
    bool m_enableAppMonitoring = true;      // 是否启用应用监控
    bool m_enableDeviceStateMonitoring = true; // 是否启用设备状态监控
    int m_topProcessCount = 5;              // TOP进程数量（默认5个）
    
    // macOS API 对象
    NSWorkspace* m_workspace;
    NSNotificationCenter* m_notificationCenter;
    
    // 当前状态缓存
    std::string m_currentActiveApp;
    std::string m_currentWindowTitle;
    NetworkType m_currentNetworkType;
    PowerState m_currentPowerState;
    ActivityPattern m_currentActivityPattern;
    
    // 状态变更时间戳
    std::chrono::steady_clock::time_point m_lastAppChange;
    std::chrono::steady_clock::time_point m_lastNetworkChange;
    std::chrono::steady_clock::time_point m_lastPowerChange;
    
    // 互斥锁保护状态访问
    mutable std::mutex m_stateMutex;
    
    /**
     * 用户情境感知处理器（回调函数）
     */
    void handleUserContextCollection(UserContextType type);
    
    /**
     * 收集当前用户活动情境
     */
    nlohmann::json collectActiveUserContext();
    
    /**
     * 收集设备状态信息
     */
    nlohmann::json collectDeviceState();
    
    
    /**
     * 发送用户情境数据到daemon
     */
    void sendUserContextData(const nlohmann::json& contextData, UserContextType type);
    
    // === 用户情境感知方法 ===
    
    /**
     * 获取当前活动应用信息
     */
    nlohmann::json getCurrentActiveApp();
    
    /**
     * 获取当前窗口标题（如果可访问）
     */
    std::string getCurrentWindowTitle();
    
    /**
     * 检测网络环境类型
     */
    NetworkType detectNetworkType();
    
    /**
     * 获取设备电源状态
     */
    PowerState getPowerState();
    
    /**
     * 分析用户活动模式
     */
    ActivityPattern analyzeActivityPattern();
    
    
    /**
     * 执行系统命令并获取输出
     */
    std::string executeCommand(const std::string& command);
    
    // === macOS事件处理方法 ===
    
    /**
     * 初始化macOS通知监听
     */
    void setupNotificationObservers();
    
    /**
     * 清理macOS通知监听
     */
    void cleanupNotificationObservers();
    
    /**
     * 处理应用切换通知
     */
    void handleAppActivationNotification(NSRunningApplication* app);
    
    /**
     * 处理窗口焦点变化通知
     */
    void handleWindowFocusNotification();
    
    /**
     * 处理设备状态变化通知（睡眠/唤醒）
     */
    void handleDeviceStateNotification();
    
    /**
     * 处理网络状态变化通知
     */
    void handleNetworkStateNotification();
    
    // === 辅助方法 ===
    
    /**
     * 转换网络类型为字符串
     */
    std::string networkTypeToString(NetworkType type);
    
    /**
     * 转换电源状态为字符串
     */
    std::string powerStateToString(PowerState state);
    
    /**
     * 转换活动模式为字符串
     */
    std::string activityPatternToString(ActivityPattern pattern);
};

} // namespace linch_connector