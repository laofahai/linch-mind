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
// UserContextScheduler 实现
// ===============================

UserContextScheduler::UserContextScheduler() {
    m_lastLoadSampling = std::chrono::steady_clock::now();
    m_lastActivitySummary = std::chrono::steady_clock::now();
}

UserContextScheduler::~UserContextScheduler() {
    stop();
}

void UserContextScheduler::start() {
    if (m_schedulerThread) {
        return; // 已经启动
    }
    
    m_shouldStop = false;
    m_schedulerThread = std::make_unique<std::thread>([this]() {
        schedulerLoop();
    });
}

void UserContextScheduler::stop() {
    if (m_schedulerThread) {
        m_shouldStop = true;
        if (m_schedulerThread->joinable()) {
            m_schedulerThread->join();
        }
        m_schedulerThread.reset();
    }
}

void UserContextScheduler::triggerContextCollection(UserContextType type) {
    if (m_contextCallback) {
        m_contextCallback(type);
    }
}

void UserContextScheduler::setLoadSamplingInterval(int minutes) {
    m_loadSamplingIntervalMinutes = std::max(5, minutes); // 最少5分钟
}

void UserContextScheduler::setActivitySummaryInterval(int hours) {
    m_activitySummaryIntervalHours = std::max(1, hours); // 最少1小时
}

void UserContextScheduler::setContextCallback(std::function<void(UserContextType)> callback) {
    m_contextCallback = callback;
}

void UserContextScheduler::schedulerLoop() {
    while (!m_shouldStop) {
        // 每5分钟检查一次是否需要收集信息
        std::this_thread::sleep_for(std::chrono::minutes(5));
        
        if (m_shouldStop) break;
        
        std::lock_guard<std::mutex> lock(m_schedulerMutex);
        
        // 检查系统负载采样
        if (shouldSampleSystemLoad()) {
            triggerContextCollection(UserContextType::SYSTEM_LOAD_UPDATE);
            m_lastLoadSampling = std::chrono::steady_clock::now();
        }
        
        // 检查活动摘要生成
        if (shouldGenerateActivitySummary()) {
            triggerContextCollection(UserContextType::USER_ACTIVITY_SUMMARY);
            m_lastActivitySummary = std::chrono::steady_clock::now();
        }
    }
}

bool UserContextScheduler::shouldSampleSystemLoad() const {
    auto now = std::chrono::steady_clock::now();
    auto elapsed = std::chrono::duration_cast<std::chrono::minutes>(now - m_lastLoadSampling);
    return elapsed.count() >= m_loadSamplingIntervalMinutes.load();
}

bool UserContextScheduler::shouldGenerateActivitySummary() const {
    auto now = std::chrono::steady_clock::now();
    auto elapsed = std::chrono::duration_cast<std::chrono::hours>(now - m_lastActivitySummary);
    return elapsed.count() >= m_activitySummaryIntervalHours.load();
}

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
    
    // 创建调度器
    m_scheduler = std::make_unique<UserContextScheduler>();
    m_scheduler->setLoadSamplingInterval(m_loadSamplingIntervalMinutes);
    m_scheduler->setActivitySummaryInterval(m_activitySummaryIntervalHours);
    
    // 设置回调函数
    m_scheduler->setContextCallback([this](UserContextType type) {
        handleUserContextCollection(type);
    });
    
    // 设置macOS通知监听
    if (m_enableAppMonitoring || m_enableDeviceStateMonitoring) {
        setupNotificationObservers();
    }
    
    logInfo("✅ 用户情境感知系统初始化成功");
    logInfo("🧠 监控策略：事件驱动应用切换，负载采样每" + std::to_string(m_loadSamplingIntervalMinutes) + "分钟");
    logInfo("📊 摘要策略：用户活动模式每" + std::to_string(m_activitySummaryIntervalHours) + "小时生成摘要");
    
    return true;
}

bool UserContextConnector::onStart() {
    logInfo("🚀 启动用户情境感知连接器");
    
    // 立即收集一次当前用户活动情境
    handleUserContextCollection(UserContextType::ACTIVE_APP_CHANGED);
    
    // 立即收集一次设备状态
    handleUserContextCollection(UserContextType::DEVICE_STATE_CHANGED);
    
    // 立即收集一次系统负载
    handleUserContextCollection(UserContextType::SYSTEM_LOAD_UPDATE);
    
    // 启动调度器
    m_scheduler->start();
    
    logInfo("✅ 用户情境感知连接器启动成功");
    return true;
}

void UserContextConnector::onStop() {
    logInfo("🛑 停止用户情境感知连接器");
    
    if (m_scheduler) {
        m_scheduler->stop();
    }
    
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
            case UserContextType::SYSTEM_LOAD_UPDATE: {
                logInfo("📊 收集智能负载信息...");
                auto loadInfo = collectIntelligentLoad();
                sendUserContextData(loadInfo, type);
                logInfo("✅ 智能负载信息收集完成");
                break;
            }
            case UserContextType::USER_ACTIVITY_SUMMARY: {
                logInfo("📋 生成用户活动摘要...");
                auto activitySummary = generateActivitySummary();
                sendUserContextData(activitySummary, type);
                logInfo("✅ 用户活动摘要生成完成");
                break;
            }
            case UserContextType::WINDOW_FOCUS_CHANGED:
            case UserContextType::NETWORK_STATE_CHANGED: {
                // 这些事件由通知触发，此处处理状态更新
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

nlohmann::json UserContextConnector::collectIntelligentLoad() {
    json loadInfo = {
        {"event_type", "intelligent_load"},
        {"timestamp", std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::system_clock::now().time_since_epoch()).count()},
        {"system_load", collectSystemLoadLight()},
        {"top_processes", collectTopProcessesLight()},
        {"storage_space", collectStorageSpace()},
        {"load_trend", "stable"}, // 简化的趋势分析
        {"resource_pressure", "normal"} // 简化的资源压力评估
    };
    
    return loadInfo;
}

nlohmann::json UserContextConnector::generateActivitySummary() {
    json activitySummary = {
        {"event_type", "activity_summary"},
        {"timestamp", std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::system_clock::now().time_since_epoch()).count()},
        {"summary_period_hours", m_activitySummaryIntervalHours},
        {"dominant_activity", activityPatternToString(m_currentActivityPattern)},
        {"app_switches", 0}, // TODO: 统计应用切换次数
        {"focused_apps", json::array()}, // TODO: 统计主要使用的应用
        {"productivity_score", 75}, // 简化的生产力评分
        {"recommendations", json::array()} // TODO: 基于模式的建议
    };
    
    return activitySummary;
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
        case UserContextType::SYSTEM_LOAD_UPDATE:
            eventType = "user_system_load_update";
            break;
        case UserContextType::USER_ACTIVITY_SUMMARY:
            eventType = "user_activity_summary";
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

nlohmann::json UserContextConnector::collectTopProcessesLight() {
    json topProcesses = {
        {"top_cpu_processes", json::array()},
        {"top_memory_processes", json::array()},
        {"process_count", 0}
    };
    
    try {
        // 轻量级版本：只获取前N个进程
        std::string topCpuOutput = executeCommand("top -l 1 -o cpu -n " + std::to_string(m_topProcessCount) + 
                                                  " -stats pid,command,cpu | tail -" + std::to_string(m_topProcessCount));
        
        if (!topCpuOutput.empty()) {
            json topCpuProcesses = json::array();
            std::istringstream stream(topCpuOutput);
            std::string line;
            int count = 0;
            
            while (std::getline(stream, line) && count < m_topProcessCount) {
                if (!line.empty() && line.find("PID") == std::string::npos) {
                    std::istringstream lineStream(line);
                    std::string pid, command, cpuStr;
                    
                    if (lineStream >> pid && lineStream >> command && lineStream >> cpuStr) {
                        try {
                            double cpuPercent = std::stod(cpuStr);
                            if (cpuPercent > 5.0) { // 只关注CPU使用率>5%的进程
                                topCpuProcesses.push_back({
                                    {"pid", std::stoi(pid)},
                                    {"command", command},
                                    {"cpu_percent", cpuPercent}
                                });
                                count++;
                            }
                        } catch (const std::exception&) {
                            // 忽略解析错误
                        }
                    }
                }
            }
            topProcesses["top_cpu_processes"] = topCpuProcesses;
        }
        
        // 获取进程总数
        std::string processCount = executeCommand("ps -e | wc -l");
        if (!processCount.empty()) {
            topProcesses["process_count"] = std::stoi(processCount) - 1; // 减去标题行
        }
        
    } catch (const std::exception& e) {
        logError("❌ TOP进程信息收集失败: " + std::string(e.what()));
    }
    
    return topProcesses;
}

nlohmann::json UserContextConnector::collectSystemLoadLight() {
    json loadInfo = {
        {"load_average_1min", 0.0},
        {"load_average_5min", 0.0},
        {"cpu_usage_percent", 0.0},
        {"memory_usage_percent", 0.0}
    };
    
    try {
        // 系统负载平均值
        std::string uptimeOutput = executeCommand("uptime");
        if (!uptimeOutput.empty()) {
            size_t loadPos = uptimeOutput.find("load averages:");
            if (loadPos != std::string::npos) {
                std::string loadPart = uptimeOutput.substr(loadPos + 14);
                std::istringstream loadStream(loadPart);
                std::string load1, load5;
                
                if (loadStream >> load1 >> load5) {
                    // 移除可能的逗号
                    if (!load1.empty() && load1.back() == ',') load1.pop_back();
                    if (!load5.empty() && load5.back() == ',') load5.pop_back();
                    
                    loadInfo["load_average_1min"] = std::stod(load1);
                    loadInfo["load_average_5min"] = std::stod(load5);
                }
            }
        }
        
        // 简化的CPU使用率获取
        std::string topOutput = executeCommand("top -l 1 -n 0 | grep 'CPU usage' | head -1");
        if (!topOutput.empty()) {
            size_t userPos = topOutput.find("% user");
            size_t sysPos = topOutput.find("% sys");
            
            if (userPos != std::string::npos && sysPos != std::string::npos) {
                // 简化解析，只获取大概的CPU使用率
                size_t startPos = topOutput.rfind(' ', userPos - 2);
                if (startPos != std::string::npos) {
                    std::string userPercent = topOutput.substr(startPos + 1, userPos - startPos - 1);
                    loadInfo["cpu_usage_percent"] = std::stod(userPercent);
                }
            }
        }
        
        // 简化的内存使用率获取
        std::string vmStatOutput = executeCommand("vm_stat | head -5");
        if (!vmStatOutput.empty()) {
            // 简化处理，实际实现需要更精确的计算
            loadInfo["memory_usage_percent"] = 60.0; // 占位值
        }
        
    } catch (const std::exception& e) {
        logError("❌ 系统负载信息收集失败: " + std::string(e.what()));
    }
    
    return loadInfo;
}

nlohmann::json UserContextConnector::collectStorageSpace() {
    json storageInfo = {
        {"main_disk_usage_percent", 0.0},
        {"available_gb", 0.0},
        {"total_gb", 0.0}
    };
    
    try {
        std::string dfOutput = executeCommand("df -h / | tail -1");
        if (!dfOutput.empty()) {
            std::istringstream stream(dfOutput);
            std::string filesystem, size, used, avail, usePercent, mountPoint;
            
            if (stream >> filesystem >> size >> used >> avail >> usePercent >> mountPoint) {
                // 解析使用百分比
                if (!usePercent.empty() && usePercent.back() == '%') {
                    std::string percentStr = usePercent.substr(0, usePercent.length() - 1);
                    storageInfo["main_disk_usage_percent"] = std::stod(percentStr);
                }
                
                // 简化的容量解析（实际需要处理G、T等单位）
                storageInfo["total_size_human"] = size;
                storageInfo["available_size_human"] = avail;
            }
        }
    } catch (const std::exception& e) {
        logError("❌ 存储空间信息收集失败: " + std::string(e.what()));
    }
    
    return storageInfo;
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
            // 监听应用激活事件
            [m_notificationCenter addObserver:[[NSNotificationCenter alloc] init]
                                     selector:@selector(handleAppActivation:)
                                         name:NSWorkspaceDidActivateApplicationNotification
                                       object:m_workspace];
            
            logInfo("✅ 应用切换监听已启用");
        }
        
        if (m_enableDeviceStateMonitoring) {
            // 监听系统睡眠/唤醒事件
            [m_notificationCenter addObserver:[[NSNotificationCenter alloc] init]
                                     selector:@selector(handleSleepNotification:)
                                         name:NSWorkspaceWillSleepNotification
                                       object:m_workspace];
            
            [m_notificationCenter addObserver:[[NSNotificationCenter alloc] init]
                                     selector:@selector(handleWakeNotification:)
                                         name:NSWorkspaceDidWakeNotification
                                       object:m_workspace];
            
            logInfo("✅ 设备状态监听已启用");
        }
    } @catch (NSException* exception) {
        logError("❌ 设置通知监听失败: " + std::string([[exception reason] UTF8String]));
    }
}

void UserContextConnector::cleanupNotificationObservers() {
    @try {
        [m_notificationCenter removeObserver:[[NSNotificationCenter alloc] init]];
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