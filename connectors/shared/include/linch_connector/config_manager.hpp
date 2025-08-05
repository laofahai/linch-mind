#pragma once

#include <string>
#include <map>
#include <memory>
#include <chrono>

namespace linch_connector {

/**
 * 配置管理器 - 从daemon加载和监控配置
 */
class ConfigManager {
public:
    ConfigManager(const std::string& daemonUrl, const std::string& connectorId);
    ~ConfigManager();

    /**
     * 从daemon加载配置
     * @return 是否加载成功
     */
    bool loadFromDaemon();

    /**
     * 开始配置监控
     * @param check_interval_seconds 检查间隔（秒）
     */
    void startConfigMonitoring(int check_interval_seconds = 30);

    /**
     * 停止配置监控
     */
    void stopConfigMonitoring();

    // 通用配置获取方法
    double getCheckInterval() const;
    int getMinContentLength() const;
    int getMaxContentLength() const;
    bool getFilterUrls() const;
    bool getFilterSensitive() const;

    /**
     * 获取原始配置值
     * @param key 配置键
     * @param defaultValue 默认值
     * @return 配置值字符串
     */
    std::string getConfigValue(const std::string& key, const std::string& defaultValue = "") const;

    /**
     * 检查配置是否已加载
     */
    bool isConfigLoaded() const;

    /**
     * 获取daemon URL
     */
    const std::string& getDaemonUrl() const;

private:
    class Impl;
    std::unique_ptr<Impl> pImpl;
    
    std::string m_daemonUrl;
    std::string m_connectorId;
    std::map<std::string, std::string> m_config;
    bool m_configLoaded;
    std::chrono::steady_clock::time_point m_lastConfigLoad;

    void configMonitorLoop(int check_interval_seconds);
};

} // namespace linch_connector