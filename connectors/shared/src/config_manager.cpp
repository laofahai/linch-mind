#include "linch_connector/config_manager.hpp"
#include "linch_connector/unified_client.hpp"
#include "linch_connector/daemon_discovery.hpp"
#include <nlohmann/json.hpp>
#include <iostream>
#include <thread>
#include <atomic>

using json = nlohmann::json;

namespace linch_connector {

class ConfigManager::Impl {
public:
    std::thread monitorThread;
    std::atomic<bool> monitoring{false};
    std::unique_ptr<UnifiedClient> client;
    DaemonInfo daemonInfo;
    bool daemonConnected{false};
    
    Impl() {
        client = std::make_unique<UnifiedClient>();
    }
    
    bool connectToDaemon() {
        if (daemonConnected && client->isConnected()) {
            return true;
        }
        
        // 发现daemon
        DaemonDiscovery discovery;
        auto daemonOpt = discovery.discoverDaemon();
        
        if (daemonOpt.has_value()) {
            daemonInfo = daemonOpt.value();
            if (client->connect(daemonInfo)) {
                daemonConnected = true;
                std::cout << "[ConfigManager] 已连接到daemon (" 
                         << client->getConnectionMode() << ")" << std::endl;
                return true;
            } else {
                std::cerr << "[ConfigManager] 连接daemon失败" << std::endl;
            }
        } else {
            std::cerr << "[ConfigManager] 未找到运行的daemon" << std::endl;
        }
        
        daemonConnected = false;
        return false;
    }
};

ConfigManager::ConfigManager(const std::string& daemonUrl, const std::string& connectorId)
    : m_daemonUrl(daemonUrl)
    , m_connectorId(connectorId)
    , pImpl(std::make_unique<Impl>())
    , m_configLoaded(false) {
}

ConfigManager::~ConfigManager() {
    stopConfigMonitoring();
}

bool ConfigManager::loadFromDaemon() {
    try {
        // 连接到daemon
        if (!pImpl->connectToDaemon()) {
            std::cerr << "❌ Failed to connect to daemon for configuration" << std::endl;
            return false;
        }
        
        pImpl->client->setTimeout(30);
        
        std::string path = "/connector-config/current/" + m_connectorId;
        auto response = pImpl->client->get(path);
        
        if (response.statusCode >= 200 && response.statusCode < 300) {
            std::cout << "[ConfigManager] 配置加载响应: " << response.body.substr(0, 200) << "..." << std::endl;
            
            json configJson = json::parse(response.body);
            
            // 清空并更新配置
            m_config.clear();
            for (auto& [key, value] : configJson.items()) {
                if (value.is_string()) {
                    m_config[key] = value.get<std::string>();
                } else if (value.is_number()) {
                    m_config[key] = std::to_string(value.get<double>());
                } else if (value.is_boolean()) {
                    m_config[key] = value.get<bool>() ? "true" : "false";
                } else if (value.is_object()) {
                    // 处理嵌套对象（如content_filters）
                    for (auto& [nested_key, nested_value] : value.items()) {
                        std::string full_key = key + "." + nested_key;
                        if (nested_value.is_string()) {
                            m_config[full_key] = nested_value.get<std::string>();
                        } else if (nested_value.is_number()) {
                            m_config[full_key] = std::to_string(nested_value.get<double>());
                        } else if (nested_value.is_boolean()) {
                            m_config[full_key] = nested_value.get<bool>() ? "true" : "false";
                        }
                    }
                }
            }
            
            m_configLoaded = true;
            m_lastConfigLoad = std::chrono::steady_clock::now();
            
            std::cout << "✅ Configuration loaded from daemon (" 
                     << pImpl->client->getConnectionMode() << "): " 
                     << m_config.size() << " items" << std::endl;
            return true;
        } else {
            std::cerr << "❌ Failed to load configuration: Status " << response.statusCode 
                     << ", Response: " << response.body.substr(0, 200) << std::endl;
            return false;
        }
    } catch (const std::exception& e) {
        std::cerr << "❌ Error loading configuration: " << e.what() << std::endl;
        return false;
    }
}

void ConfigManager::startConfigMonitoring(int check_interval_seconds) {
    if (pImpl->monitoring.load()) {
        return; // 已经在监控中
    }
    
    pImpl->monitoring.store(true);
    pImpl->monitorThread = std::thread(&ConfigManager::configMonitorLoop, this, check_interval_seconds);
}

void ConfigManager::stopConfigMonitoring() {
    pImpl->monitoring.store(false);
    if (pImpl->monitorThread.joinable()) {
        pImpl->monitorThread.join();
    }
}

void ConfigManager::configMonitorLoop(int check_interval_seconds) {
    while (pImpl->monitoring.load()) {
        std::this_thread::sleep_for(std::chrono::seconds(check_interval_seconds));
        
        if (pImpl->monitoring.load()) {
            loadFromDaemon();
        }
    }
}

double ConfigManager::getCheckInterval() const {
    std::string value = getConfigValue("check_interval", "1.0");
    try {
        return std::stod(value);
    } catch (...) {
        return 1.0;
    }
}

int ConfigManager::getMinContentLength() const {
    std::string value = getConfigValue("min_content_length", "5");
    try {
        return std::stoi(value);
    } catch (...) {
        return 5;
    }
}

int ConfigManager::getMaxContentLength() const {
    std::string value = getConfigValue("max_content_length", "50000");
    try {
        return std::stoi(value);
    } catch (...) {
        return 50000;
    }
}

bool ConfigManager::getFilterUrls() const {
    std::string value = getConfigValue("content_filters.filter_urls", "false");
    return value == "true";
}

bool ConfigManager::getFilterSensitive() const {
    std::string value = getConfigValue("content_filters.filter_sensitive", "true");
    return value == "true";
}

std::string ConfigManager::getConfigValue(const std::string& key, const std::string& defaultValue) const {
    auto it = m_config.find(key);
    if (it != m_config.end()) {
        return it->second;
    }
    return defaultValue;
}

bool ConfigManager::isConfigLoaded() const {
    return m_configLoaded;
}

const std::string& ConfigManager::getDaemonUrl() const {
    return m_daemonUrl;
}

} // namespace linch_connector