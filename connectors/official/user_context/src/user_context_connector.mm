#include "user_context_connector.hpp"
#include <linch_connector/utils.hpp>
#include <nlohmann/json.hpp>
#include <iostream>
#include <chrono>
#include <thread>
#include <sstream>
#include <cstdio>
#include <stdexcept>
#include <unistd.h>
#include <sys/stat.h>

#import <Foundation/Foundation.h>
#import <AppKit/AppKit.h>
#import <SystemConfiguration/SystemConfiguration.h>
#import <IOKit/IOKitLib.h>
#import <IOKit/ps/IOPowerSources.h>

using json = nlohmann::json;

namespace linch_connector {


// ===============================
// UserContextConnector 实现
// ===============================

UserContextConnector::UserContextConnector() 
    : BaseConnector("user_context", "用户情境感知连接器")
{
    std::cout << "🧠 用户情境感知连接器初始化" << std::endl;
    
    // 初始化状态
    m_currentNetworkType = NetworkType::UNKNOWN;
    m_currentPowerState = PowerState::UNKNOWN;
    m_currentActivityPattern = ActivityPattern::BACKGROUND_IDLE;
    
    // 获取macOS API对象
    m_workspace = [NSWorkspace sharedWorkspace];
    m_notificationCenter = [NSWorkspace sharedWorkspace].notificationCenter;
}

std::unique_ptr<IConnectorMonitor> UserContextConnector::createMonitor() {
    // 使用空监控器，专注于事件驱动
    return std::make_unique<NullMonitor>();
}

bool UserContextConnector::loadConnectorConfig() {
    logInfo("📋 加载用户情境感知连接器配置");
    
    auto& configManager = getConfigManager();
    
    // 系统负载采样间隔
    std::string loadIntervalStr = configManager.getConfigValue("load_sampling_interval", "10");
    try {
        m_loadSamplingIntervalMinutes = std::stoi(loadIntervalStr);
        if (m_loadSamplingIntervalMinutes < 5) {
            m_loadSamplingIntervalMinutes = 5; // 最小5分钟
        }
    } catch (const std::exception&) {
        m_loadSamplingIntervalMinutes = 10; // 默认10分钟
    }
    
    // 活动摘要生成间隔
    std::string summaryIntervalStr = configManager.getConfigValue("activity_summary_interval", "2");
    try {
        m_activitySummaryIntervalHours = std::stoi(summaryIntervalStr);
        if (m_activitySummaryIntervalHours < 1) {
            m_activitySummaryIntervalHours = 1; // 最小1小时
        }
    } catch (const std::exception&) {
        m_activitySummaryIntervalHours = 2; // 默认2小时
    }
    
    // 是否启用应用监控
    std::string enableAppStr = configManager.getConfigValue("enable_app_monitoring", "true");
    m_enableAppMonitoring = (enableAppStr == "true" || enableAppStr == "1");
    
    // 是否启用设备状态监控
    std::string enableDeviceStr = configManager.getConfigValue("enable_device_state_monitoring", "true");
    m_enableDeviceStateMonitoring = (enableDeviceStr == "true" || enableDeviceStr == "1");
    
    // TOP进程数量
    std::string topProcessStr = configManager.getConfigValue("top_process_count", "5");
    try {
        m_topProcessCount = std::stoi(topProcessStr);
        if (m_topProcessCount < 3) {
            m_topProcessCount = 3; // 最小3个
        } else if (m_topProcessCount > 10) {
            m_topProcessCount = 10; // 最大10个
        }
    } catch (const std::exception&) {
        m_topProcessCount = 5; // 默认5个
    }
    
    logInfo("✅ 配置加载完成 - 负载采样间隔: " + std::to_string(m_loadSamplingIntervalMinutes) + 
            "分钟, 摘要间隔: " + std::to_string(m_activitySummaryIntervalHours) + "小时" +
            ", 应用监控: " + (m_enableAppMonitoring ? "启用" : "禁用") +
            ", 设备监控: " + (m_enableDeviceStateMonitoring ? "启用" : "禁用") +
            ", TOP进程数: " + std::to_string(m_topProcessCount));
    
    return true;
}

bool UserContextConnector::onInitialize() {
    logInfo("🔧 初始化用户情境感知系统");
    
    // 设置macOS通知监听
    if (m_enableAppMonitoring || m_enableDeviceStateMonitoring) {
        setupNotificationObservers();
    }
    
    logInfo("✅ 用户情境感知系统初始化成功");
    logInfo("🧠 监控策略：事件驱动的实时用户情境感知");
    
    return true;
}

bool UserContextConnector::onStart() {
    logInfo("🚀 启动用户情境感知连接器");
    
    // 立即收集一次当前用户活动情境
    handleUserContextCollection(UserContextType::ACTIVE_APP_CHANGED);
    
    // 立即收集一次设备状态
    handleUserContextCollection(UserContextType::DEVICE_STATE_CHANGED);
    
    logInfo("✅ 用户情境感知连接器启动成功");
    return true;
}

void UserContextConnector::onStop() {
    logInfo("🛑 停止用户情境感知连接器");
    
    // 清理macOS通知监听
    cleanupNotificationObservers();
    
    logInfo("✅ 用户情境感知连接器已停止");
}

void UserContextConnector::triggerUserContextCollection(UserContextType type) {
    handleUserContextCollection(type);
}

void UserContextConnector::handleUserContextCollection(UserContextType type) {
    try {
        switch (type) {
            case UserContextType::ACTIVE_APP_CHANGED: {
                logInfo("🧠 收集用户活动情境...");
                auto activeContext = collectActiveUserContext();
                sendUserContextData(activeContext, type);
                logInfo("✅ 用户活动情境收集完成");
                break;
            }
            case UserContextType::DEVICE_STATE_CHANGED: {
                logInfo("🔋 收集设备状态信息...");
                auto deviceState = collectDeviceState();
                sendUserContextData(deviceState, type);
                logInfo("✅ 设备状态信息收集完成");
                break;
            }
            default: {
                // 简化：其他事件统一处理为状态更新
                logInfo("🔄 处理状态变化事件");
                auto contextUpdate = collectActiveUserContext();
                sendUserContextData(contextUpdate, type);
                break;
            }
        }
    } catch (const std::exception& e) {
        logError("❌ 用户情境感知收集失败: " + std::string(e.what()));
    }
}

nlohmann::json UserContextConnector::collectActiveUserContext() {
    std::lock_guard<std::mutex> lock(m_stateMutex);
    
    json activeContext = {
        {"event_type", "active_user_context"},
        {"timestamp", std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::system_clock::now().time_since_epoch()).count()},
        {"active_app", getCurrentActiveApp()},
        {"window_title", getCurrentWindowTitle()},
        {"activity_pattern", activityPatternToString(analyzeActivityPattern())},
        {"session_duration_minutes", 0},
        {"focus_switches_per_hour", 0}
    };
    
    return activeContext;
}

nlohmann::json UserContextConnector::collectDeviceState() {
    std::lock_guard<std::mutex> lock(m_stateMutex);
    
    json deviceState = {
        {"event_type", "device_state"},
        {"timestamp", std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::system_clock::now().time_since_epoch()).count()},
        {"power_state", powerStateToString(getPowerState())},
        {"network_type", networkTypeToString(detectNetworkType())},
        {"screen_locked", false}, // TODO: 实现屏幕锁定检测
        {"user_idle_minutes", 0}  // TODO: 实现用户空闲时间检测
    };
    
    return deviceState;
}


void UserContextConnector::sendUserContextData(const nlohmann::json& contextData, UserContextType type) {
    std::string eventType;
    switch (type) {
        case UserContextType::ACTIVE_APP_CHANGED:
            eventType = "user_active_app_changed";
            break;
        case UserContextType::DEVICE_STATE_CHANGED:
            eventType = "user_device_state_changed";
            break;
        default:
            eventType = "user_context_update";
            break;
    }
    
    ConnectorEvent event = ConnectorEvent::create("user_context", eventType, contextData);
    sendEvent(event);
}

// ===============================
// 用户情境感知方法实现
// ===============================

nlohmann::json UserContextConnector::getCurrentActiveApp() {
    json appInfo = {
        {"name", "unknown"},
        {"bundle_id", "unknown"},
        {"pid", 0},
        {"is_frontmost", false}
    };
    
    @try {
        NSRunningApplication* frontApp = [m_workspace frontmostApplication];
        if (frontApp) {
            appInfo["name"] = std::string([[frontApp localizedName] UTF8String] ?: "unknown");
            appInfo["bundle_id"] = std::string([[frontApp bundleIdentifier] UTF8String] ?: "unknown");
            appInfo["pid"] = [frontApp processIdentifier];
            appInfo["is_frontmost"] = true;
            
            // 缓存当前活动应用
            m_currentActiveApp = appInfo["name"];
        }
    } @catch (NSException* exception) {
        logError("❌ 获取活动应用失败: " + std::string([[exception reason] UTF8String]));
    }
    
    return appInfo;
}

std::string UserContextConnector::getCurrentWindowTitle() {
    // macOS获取窗口标题需要无障碍权限，这里提供基础实现
    // 实际项目中可能需要用户授权无障碍访问
    return ""; // 暂时返回空，避免权限问题
}

NetworkType UserContextConnector::detectNetworkType() {
    NetworkType networkType = NetworkType::UNKNOWN;
    
    @try {
        // 简化的网络检测，避免使用废弃的API
        // 检查系统偏好中的网络设置
        std::string networkStatus = executeCommand("networksetup -getairportnetwork en0 2>/dev/null");
        if (!networkStatus.empty() && networkStatus.find("Wi-Fi Network") != std::string::npos) {
            networkType = NetworkType::WIFI;
        } else {
            // 检查以太网连接
            std::string ethernetStatus = executeCommand("ifconfig en0 | grep 'status: active' 2>/dev/null");
            if (!ethernetStatus.empty()) {
                networkType = NetworkType::ETHERNET;
            } else {
                // 检查是否有任何网络连接
                std::string pingTest = executeCommand("ping -c 1 -W 1000 8.8.8.8 >/dev/null 2>&1 && echo 'connected'");
                if (!pingTest.empty() && pingTest.find("connected") != std::string::npos) {
                    networkType = NetworkType::WIFI; // 默认假设为Wi-Fi
                } else {
                    networkType = NetworkType::DISCONNECTED;
                }
            }
        }
    } @catch (NSException* exception) {
        logError("❌ 网络类型检测失败: " + std::string([[exception reason] UTF8String]));
    }
    
    m_currentNetworkType = networkType;
    return networkType;
}

PowerState UserContextConnector::getPowerState() {
    PowerState powerState = PowerState::UNKNOWN;
    
    @try {
        // 简化的电源状态检测，使用命令行工具
        std::string pmsetOutput = executeCommand("pmset -g batt");
        if (!pmsetOutput.empty()) {
            if (pmsetOutput.find("AC Power") != std::string::npos || 
                pmsetOutput.find("'AC Power'") != std::string::npos) {
                powerState = PowerState::PLUGGED_IN;
            } else if (pmsetOutput.find("Battery Power") != std::string::npos ||
                       pmsetOutput.find("'Battery Power'") != std::string::npos) {
                powerState = PowerState::ON_BATTERY;
            }
            
            // 检查是否正在充电
            if (pmsetOutput.find("charging") != std::string::npos) {
                powerState = PowerState::CHARGING;
            } else if (pmsetOutput.find("100%") != std::string::npos && 
                       powerState == PowerState::PLUGGED_IN) {
                powerState = PowerState::FULLY_CHARGED;
            }
        }
    } @catch (NSException* exception) {
        logError("❌ 电源状态检测失败: " + std::string([[exception reason] UTF8String]));
    }
    
    m_currentPowerState = powerState;
    return powerState;
}

ActivityPattern UserContextConnector::analyzeActivityPattern() {
    // 简化的活动模式分析
    // 实际实现可能需要基于应用使用时间、切换频率等进行更复杂的分析
    
    ActivityPattern pattern = ActivityPattern::BACKGROUND_IDLE;
    
    @try {
        NSRunningApplication* frontApp = [m_workspace frontmostApplication];
        if (frontApp) {
            NSString* bundleId = [frontApp bundleIdentifier];
            
            // 基于应用类型简单分类
            if ([bundleId containsString:@"Xcode"] || 
                [bundleId containsString:@"Visual Studio Code"] ||
                [bundleId containsString:@"IntelliJ"]) {
                pattern = ActivityPattern::FOCUSED_DEEP; // 开发工具
            } else if ([bundleId containsString:@"Safari"] ||
                       [bundleId containsString:@"Chrome"] ||
                       [bundleId containsString:@"Firefox"]) {
                pattern = ActivityPattern::LIGHT_USAGE; // 浏览器
            } else if ([bundleId containsString:@"Slack"] ||
                       [bundleId containsString:@"Messages"] ||
                       [bundleId containsString:@"Mail"]) {
                pattern = ActivityPattern::ACTIVE_WORK; // 通讯工具
            }
        } else {
            pattern = ActivityPattern::AWAY; // 没有前台应用
        }
    } @catch (NSException* exception) {
        logError("❌ 活动模式分析失败: " + std::string([[exception reason] UTF8String]));
    }
    
    m_currentActivityPattern = pattern;
    return pattern;
}


std::string UserContextConnector::executeCommand(const std::string& command) {
    std::string result;
    
    try {
        FILE* pipe = popen(command.c_str(), "r");
        if (!pipe) {
            return "";
        }
        
        char buffer[256];
        while (fgets(buffer, sizeof(buffer), pipe) != nullptr) {
            result += buffer;
        }
        
        int status = pclose(pipe);
        if (status != 0) {
            return "";
        }
    } catch (const std::exception& e) {
        logError("❌ 执行命令失败: " + command + " - " + std::string(e.what()));
        return "";
    }
    
    return result;
}

// ===============================
// macOS事件处理方法实现
// ===============================

void UserContextConnector::setupNotificationObservers() {
    @try {
        if (m_enableAppMonitoring) {
            // 监听应用激活事件 - 使用C++桥接方法
            [[NSNotificationCenter defaultCenter] addObserverForName:NSWorkspaceDidActivateApplicationNotification
                                                               object:m_workspace
                                                                queue:[NSOperationQueue mainQueue]
                                                           usingBlock:^(NSNotification* notification) {
                NSRunningApplication* app = notification.userInfo[NSWorkspaceApplicationKey];
                handleAppActivationNotification(app);
            }];
            
            logInfo("✅ 应用切换监听已启用");
        }
        
        if (m_enableDeviceStateMonitoring) {
            // 监听系统睡眠事件
            [[NSNotificationCenter defaultCenter] addObserverForName:NSWorkspaceWillSleepNotification
                                                               object:m_workspace
                                                                queue:[NSOperationQueue mainQueue]
                                                           usingBlock:^(NSNotification* notification) {
                logInfo("🌙 系统即将睡眠");
                handleDeviceStateNotification();
            }];
            
            // 监听系统唤醒事件
            [[NSNotificationCenter defaultCenter] addObserverForName:NSWorkspaceDidWakeNotification
                                                               object:m_workspace
                                                                queue:[NSOperationQueue mainQueue]
                                                           usingBlock:^(NSNotification* notification) {
                logInfo("☀️ 系统已唤醒");
                handleDeviceStateNotification();
            }];
            
            logInfo("✅ 设备状态监听已启用");
        }
    } @catch (NSException* exception) {
        logError("❌ 设置通知监听失败: " + std::string([[exception reason] UTF8String]));
    }
}

void UserContextConnector::cleanupNotificationObservers() {
    @try {
        // 移除所有与NSWorkspace相关的观察者
        [[NSNotificationCenter defaultCenter] removeObserver:nil 
                                                         name:NSWorkspaceDidActivateApplicationNotification 
                                                       object:m_workspace];
        [[NSNotificationCenter defaultCenter] removeObserver:nil 
                                                         name:NSWorkspaceWillSleepNotification 
                                                       object:m_workspace];
        [[NSNotificationCenter defaultCenter] removeObserver:nil 
                                                         name:NSWorkspaceDidWakeNotification 
                                                       object:m_workspace];
        logInfo("✅ 通知监听已清理");
    } @catch (NSException* exception) {
        logError("❌ 清理通知监听失败: " + std::string([[exception reason] UTF8String]));
    }
}

void UserContextConnector::handleAppActivationNotification(NSRunningApplication* app) {
    if (app) {
        std::string appName = std::string([[app localizedName] UTF8String] ?: "unknown");
        logInfo("🔄 应用切换: " + appName);
        
        // 触发应用切换事件
        triggerUserContextCollection(UserContextType::ACTIVE_APP_CHANGED);
    }
}

void UserContextConnector::handleWindowFocusNotification() {
    logInfo("🔄 窗口焦点变化");
    triggerUserContextCollection(UserContextType::WINDOW_FOCUS_CHANGED);
}

void UserContextConnector::handleDeviceStateNotification() {
    logInfo("🔄 设备状态变化");
    triggerUserContextCollection(UserContextType::DEVICE_STATE_CHANGED);
}

void UserContextConnector::handleNetworkStateNotification() {
    logInfo("🔄 网络状态变化");
    triggerUserContextCollection(UserContextType::NETWORK_STATE_CHANGED);
}

// ===============================
// 辅助方法实现
// ===============================

std::string UserContextConnector::networkTypeToString(NetworkType type) {
    switch (type) {
        case NetworkType::WIFI: return "wifi";
        case NetworkType::ETHERNET: return "ethernet";
        case NetworkType::CELLULAR: return "cellular";
        case NetworkType::VPN: return "vpn";
        case NetworkType::DISCONNECTED: return "disconnected";
        default: return "unknown";
    }
}

std::string UserContextConnector::powerStateToString(PowerState state) {
    switch (state) {
        case PowerState::ON_BATTERY: return "on_battery";
        case PowerState::PLUGGED_IN: return "plugged_in";
        case PowerState::CHARGING: return "charging";
        case PowerState::FULLY_CHARGED: return "fully_charged";
        default: return "unknown";
    }
}

std::string UserContextConnector::activityPatternToString(ActivityPattern pattern) {
    switch (pattern) {
        case ActivityPattern::ACTIVE_WORK: return "active_work";
        case ActivityPattern::LIGHT_USAGE: return "light_usage";
        case ActivityPattern::BACKGROUND_IDLE: return "background_idle";
        case ActivityPattern::AWAY: return "away";
        case ActivityPattern::FOCUSED_DEEP: return "focused_deep";
        default: return "unknown";
    }
}

} // namespace linch_connector