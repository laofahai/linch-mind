#pragma once

#include <string>
#include <map>
#include <memory>
#include <chrono>

/**
 * Configuration manager for clipboard connector
 * Handles loading and monitoring configuration from daemon
 */
class ConfigManager {
public:
    ConfigManager(const std::string& daemonUrl, const std::string& connectorId = "clipboard");
    ~ConfigManager();

    /**
     * Load configuration from daemon
     * @return true if configuration loaded successfully
     */
    bool loadFromDaemon();

    /**
     * Start periodic configuration monitoring
     * @param check_interval_seconds Interval between config checks (default: 30)
     */
    void startConfigMonitoring(int check_interval_seconds = 30);

    /**
     * Stop configuration monitoring
     */
    void stopConfigMonitoring();

    // Configuration getters with default values
    double getCheckInterval() const;
    int getMinContentLength() const;
    int getMaxContentLength() const;
    bool getFilterUrls() const;
    bool getFilterSensitive() const;

    /**
     * Get raw configuration value
     * @param key Configuration key
     * @param defaultValue Default value if key not found
     * @return Configuration value as string
     */
    std::string getConfigValue(const std::string& key, const std::string& defaultValue = "") const;

    /**
     * Check if configuration has been loaded
     */
    bool isConfigLoaded() const;

    /**
     * Get daemon URL
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