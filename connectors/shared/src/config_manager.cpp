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
                std::cout << "[ConfigManager] 已连接到daemon (IPC)" << std::endl;
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

ConfigManager::ConfigManager(const std::string& connectorId, const std::string& daemonUrl)
    : pImpl(std::make_unique<Impl>()),
      m_daemonUrl(daemonUrl), 
      m_connectorId(connectorId),
      m_configLoaded(false) {
}

ConfigManager::~ConfigManager() {
    stopConfigMonitoring();
}

bool ConfigManager::loadFromDaemon() {
    try {
        if (!pImpl->connectToDaemon()) {
            std::cerr << "[ConfigManager] 无法连接到daemon" << std::endl;
            return false;
        }
        
        std::string path = "/connector-config/current/" + m_connectorId;
        auto response = pImpl->client->get(path);
        
        if (response.isSuccess()) {
            std::cout << "[ConfigManager] 配置加载响应: " << response.body.substr(0, 200) << "..." << std::endl;
            
            json configJson = json::parse(response.body);
            json configData;
            
            // 检查响应格式，提取config字段
            if (configJson.contains("config")) {
                configData = configJson["config"];
            } else {
                configData = configJson;
            }
            
            // 如果配置为空，尝试获取并应用默认配置
            if (configData.empty() || configData.is_null()) {
                std::cout << "[ConfigManager] 当前配置为空，尝试获取默认配置..." << std::endl;
                
                // 请求默认配置
                std::string defaultPath = "/connector-config/defaults/" + m_connectorId;
                auto defaultResponse = pImpl->client->get(defaultPath);
                
                if (defaultResponse.isSuccess()) {
                    json defaultJson = json::parse(defaultResponse.body);
                    if (defaultJson.contains("default_config")) {
                        configData = defaultJson["default_config"];
                        std::cout << "[ConfigManager] ✅ 成功获取默认配置" << std::endl;
                        
                        // 可选：将默认配置保存到daemon数据库
                        json applyData = {
                            {"connector_id", m_connectorId}
                        };
                        auto applyResponse = pImpl->client->post("/connector-config/apply-defaults", applyData.dump());
                        if (applyResponse.isSuccess()) {
                            std::cout << "[ConfigManager] ✅ 默认配置已应用到数据库" << std::endl;
                        }
                    }
                } else {
                    std::cerr << "[ConfigManager] ⚠️  无法获取默认配置，使用空配置" << std::endl;
                }
            }
            
            // 清空并更新配置
            m_config.clear();
            for (auto& [key, value] : configData.items()) {
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
            
            std::cout << "✅ Configuration loaded from daemon: " << m_config.size() << " items" << std::endl;
            return true;
        } else {
            std::cerr << "❌ Failed to load configuration: " << response.error_message 
                      << " (code: " << response.error_code << ")" << std::endl;
            return false;
        }
    } catch (const std::exception& e) {
        std::cerr << "❌ Error loading configuration: " << e.what() << std::endl;
        return false;
    }
}

void ConfigManager::startConfigMonitoring(int check_interval_seconds) {
    if (pImpl->monitoring.load()) {
        return;
    }
    
    pImpl->monitoring = true;
    pImpl->monitorThread = std::thread([this, check_interval_seconds]() {
        configMonitorLoop(check_interval_seconds);
    });
}

void ConfigManager::stopConfigMonitoring() {
    pImpl->monitoring = false;
    if (pImpl->monitorThread.joinable()) {
        pImpl->monitorThread.join();
    }
}

void ConfigManager::configMonitorLoop(int check_interval_seconds) {
    while (pImpl->monitoring.load()) {
        std::this_thread::sleep_for(std::chrono::seconds(check_interval_seconds));
        
        if (!pImpl->monitoring.load()) {
            break;
        }
        
        loadFromDaemon();
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
    std::string value = getConfigValue("content_filters.filter_urls", "true");
    return value == "true" || value == "1";
}

bool ConfigManager::getFilterSensitive() const {
    std::string value = getConfigValue("content_filters.filter_sensitive", "true");
    return value == "true" || value == "1";
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