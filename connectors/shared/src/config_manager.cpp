#include "linch_connector/config_manager.hpp"
#include "linch_connector/unified_client.hpp"
#include "linch_connector/daemon_discovery.hpp"
#include "linch_connector/error_handler.hpp"
#include <cpptoml.h>
#include <nlohmann/json.hpp>
#include <iostream>
#include <thread>
#include <atomic>
#include <sstream>
#include <fstream>

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
    
    // 新增：TOML配置解析器
    std::map<std::string, std::string> parseTomlConfig(const std::string& tomlContent) {
        std::map<std::string, std::string> config;
        try {
            std::istringstream stream(tomlContent);
            auto tomlData = cpptoml::parser{stream}.parse();
            
            // 递归解析TOML数据到扁平化map
            parseTomlTable(tomlData, config, "");
            
        } catch (const std::exception& e) {
            std::cerr << "[ConfigManager] TOML解析错误: " << e.what() << std::endl;
        }
        return config;
    }
    
    // 递归解析TOML表
    void parseTomlTable(const std::shared_ptr<cpptoml::table>& table, 
                       std::map<std::string, std::string>& config, 
                       const std::string& prefix) {
        for (const auto& [key, value] : *table) {
            std::string fullKey = prefix.empty() ? key : prefix + "." + key;
            
            if (auto str = value->as<std::string>()) {
                config[fullKey] = str->get();
            } else if (auto num = value->as<double>()) {
                config[fullKey] = std::to_string(num->get());
            } else if (auto boolean = value->as<bool>()) {
                config[fullKey] = boolean->get() ? "true" : "false";
            } else if (auto arr = value->as_array()) {
                // 处理数组 - 转换为JSON字符串存储
                json jsonArray = json::array();
                for (size_t i = 0; i < arr->size(); ++i) {
                    if (auto str = arr->at(i)->as<std::string>()) {
                        jsonArray.push_back(str->get());
                    }
                }
                config[fullKey] = jsonArray.dump();
            } else if (auto subtable = value->as_table()) {
                // 递归处理子表
                parseTomlTable(subtable, config, fullKey);
            }
        }
    }
    
    // 专门解析config_default_values部分
    std::map<std::string, std::string> parseDefaultValuesFromToml(const std::string& tomlContent) {
        std::map<std::string, std::string> config;
        try {
            std::istringstream stream(tomlContent);
            auto tomlData = cpptoml::parser{stream}.parse();
            
            // 只提取[config_default_values]部分
            auto defaultValues = tomlData->get_table("config_default_values");
            if (defaultValues) {
                parseTomlTable(defaultValues, config, "");
                std::cout << "[ConfigManager] 从TOML提取默认配置值: " << config.size() << " 项" << std::endl;
            } else {
                std::cout << "[ConfigManager] TOML中未找到[config_default_values]段" << std::endl;
            }
            
        } catch (const std::exception& e) {
            std::cerr << "[ConfigManager] TOML默认值解析错误: " << e.what() << std::endl;
        }
        return config;
    }
    
    bool connectToDaemon() {
        if (daemonConnected && client->isConnected()) {
            return true;
        }
        
        HANDLE_IPC_ERROR("连接daemon失败", {
            // 发现daemon
            DaemonDiscovery discovery;
            auto daemonOpt = discovery.discoverDaemon();
            
            if (daemonOpt.has_value()) {
                daemonInfo = daemonOpt.value();
                if (client->connect(daemonInfo)) {
                    daemonConnected = true;
                    std::cout << "[ConfigManager] ✅ 已连接到daemon (IPC)" << std::endl;
                    return true;
                } else {
                    throw std::runtime_error("连接daemon失败");
                }
            } else {
                throw std::runtime_error("未找到运行的daemon");
            }
        });
        
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
            std::cerr << "[ConfigManager] 无法连接到daemon，尝试本地配置" << std::endl;
            return loadFromLocalToml();  // daemon连接失败时的回退
        }
        
        // 主要配置来源：从daemon数据库获取配置
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
                std::cout << "[ConfigManager] 数据库配置为空，尝试获取默认配置..." << std::endl;
                
                // 1. 尝试从daemon获取默认配置（基于connector.toml）
                std::string defaultPath = "/connector-config/defaults/" + m_connectorId;
                auto defaultResponse = pImpl->client->get(defaultPath);
                
                if (defaultResponse.isSuccess()) {
                    json defaultJson = json::parse(defaultResponse.body);
                    if (defaultJson.contains("default_config")) {
                        configData = defaultJson["default_config"];
                        std::cout << "[ConfigManager] ✅ 成功获取daemon默认配置" << std::endl;
                    }
                } else {
                    // 2. 回退到本地TOML配置
                    std::cout << "[ConfigManager] daemon默认配置不可用，使用本地TOML配置" << std::endl;
                    return loadFromLocalToml();
                }
            }
            
            // JSON配置回退处理（保持向后兼容）
            return parseJsonConfig(configData);
            
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

bool ConfigManager::loadFromLocalToml() {
    HANDLE_CONFIG_ERROR("TOML配置加载失败", {
        // 回退机制：从本地connector.toml的[config_default_values]加载默认配置
        // 注意：这只是应急回退，正常情况下配置应该从daemon数据库获取
        std::vector<std::string> searchPaths = {
            "./connector.toml",
            "./" + m_connectorId + "/connector.toml",
            "../" + m_connectorId + "/connector.toml"
        };
        
        for (const auto& path : searchPaths) {
            std::ifstream file(path);
            if (file.is_open()) {
                std::string content((std::istreambuf_iterator<char>(file)),
                                   std::istreambuf_iterator<char>());
                file.close();
                
                auto parsedConfig = pImpl->parseDefaultValuesFromToml(content);
                if (!parsedConfig.empty()) {
                    m_config = parsedConfig;
                    m_configLoaded = true;
                    m_lastConfigLoad = std::chrono::steady_clock::now();
                    
                    std::cout << "[ConfigManager] ✅ 从本地TOML默认值加载配置: " << path << std::endl;
                    return true;
                }
            }
        }
        
        return false;
    });
    return false;
}

bool ConfigManager::parseJsonConfig(const json& configData) {
    try {
        // 清空并更新配置
        m_config.clear();
        for (auto& [key, value] : configData.items()) {
            if (value.is_string()) {
                m_config[key] = value.get<std::string>();
            } else if (value.is_number()) {
                m_config[key] = std::to_string(value.get<double>());
            } else if (value.is_boolean()) {
                m_config[key] = value.get<bool>() ? "true" : "false";
            } else if (value.is_array()) {
                // 处理数组 - 将JSON数组转换为JSON字符串存储
                m_config[key] = value.dump();
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
                    } else if (nested_value.is_array()) {
                        // 处理嵌套数组
                        m_config[full_key] = nested_value.dump();
                    }
                }
            }
        }
        
        m_configLoaded = true;
        m_lastConfigLoad = std::chrono::steady_clock::now();
        
        std::cout << "✅ Configuration loaded from daemon: " << m_config.size() << " items" << std::endl;
        return true;
    } catch (const std::exception& e) {
        std::cerr << "❌ Error parsing JSON configuration: " << e.what() << std::endl;
        return false;
    }
}

} // namespace linch_connector