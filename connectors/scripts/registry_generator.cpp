#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <filesystem>
#include <chrono>
#include <iomanip>
#include <sstream>
#include <getopt.h>
#include <nlohmann/json.hpp>

using json = nlohmann::json;
namespace fs = std::filesystem;

std::string getCurrentTimestamp() {
    auto now = std::chrono::system_clock::now();
    auto time_t = std::chrono::system_clock::to_time_t(now);
    std::stringstream ss;
    ss << std::put_time(std::gmtime(&time_t), "%Y-%m-%dT%H:%M:%SZ");
    return ss.str();
}

std::string getEnvVar(const std::string& name, const std::string& defaultValue = "") {
    const char* value = std::getenv(name.c_str());
    return value ? std::string(value) : defaultValue;
}

json generateRegistry(const std::string& connectorsDir, const std::string& outputFile) {
    fs::current_path(connectorsDir);
    
    // Find all connector.json files
    std::vector<std::string> configFiles;
    
    if (fs::exists("official")) {
        for (const auto& entry : fs::recursive_directory_iterator("official")) {
            if (entry.path().filename() == "connector.json") {
                configFiles.push_back(entry.path().string());
            }
        }
    }
    
    if (fs::exists("community")) {
        for (const auto& entry : fs::recursive_directory_iterator("community")) {
            if (entry.path().filename() == "connector.json") {
                configFiles.push_back(entry.path().string());
            }
        }
    }
    
    std::cout << "Found " << configFiles.size() << " connector configs" << std::endl;
    
    // Read existing registry if it exists
    json existingRegistry;
    if (fs::exists(outputFile)) {
        try {
            std::ifstream file(outputFile);
            file >> existingRegistry;
            std::cout << "📖 Loaded existing registry with " 
                      << existingRegistry.value("connectors", json::object()).size() 
                      << " connectors" << std::endl;
        } catch (const std::exception& e) {
            std::cout << "⚠️ Failed to load existing registry: " << e.what() 
                      << ", creating new one" << std::endl;
        }
    }
    
    // Initialize new registry structure
    json registry;
    registry["schema_version"] = "1.0";
    registry["last_updated"] = getCurrentTimestamp();
    registry["connectors"] = existingRegistry.value("connectors", json::object());
    registry["metadata"] = {
        {"repository", getEnvVar("GITHUB_REPOSITORY", "laofahai/linch-mind")},
        {"commit", getEnvVar("GITHUB_SHA", "unknown")},
        {"total_count", 0}
    };
    
    // Process each connector config
    for (const auto& configPath : configFiles) {
        try {
            std::ifstream file(configPath);
            json config;
            file >> config;
            
            std::string connectorId = config["id"];
            std::string connectorType = configPath.substr(0, configPath.find('/'));
            std::string currentVersion = config["version"];
            
            // Check if connector already exists
            json existingConnector = registry["connectors"].value(connectorId, json::object());
            std::string action;
            
            if (!existingConnector.empty()) {
                std::string existingVersion = existingConnector.value("version", "0.0.0");
                if (existingVersion != currentVersion) {
                    std::cout << "🔄 Updating " << connectorId << ": " 
                              << existingVersion << " -> " << currentVersion << std::endl;
                    action = "updated";
                } else {
                    std::cout << "✅ Keeping " << connectorId << " v" << currentVersion 
                              << " (no changes)" << std::endl;
                    action = "kept";
                }
            } else {
                std::cout << "🆕 Adding new connector: " << connectorId 
                          << " v" << currentVersion << std::endl;
                action = "added";
            }
            
            // Build connector info
            json connectorInfo = {
                {"id", config["id"]},
                {"name", config["name"]},
                {"version", config["version"]},
                {"description", config["description"]},
                {"author", config["author"]},
                {"category", config["category"]},
                {"type", connectorType},
                {"platforms", config.value("platforms", json::object())},
                {"permissions", config.value("permissions", json::array())},
                {"capabilities", config.value("capabilities", json::object())},
                {"config_path", configPath},
                {"last_updated", getCurrentTimestamp()},
                {"action", action}
            };
            
            // Preserve existing download URL if exists
            if (!existingConnector.empty() && existingConnector.contains("download_url")) {
                connectorInfo["download_url"] = existingConnector["download_url"];
            }
            
            registry["connectors"][connectorId] = connectorInfo;
            
        } catch (const std::exception& e) {
            std::cout << "❌ Error processing " << configPath << ": " << e.what() << std::endl;
            continue;
        }
    }
    
    registry["metadata"]["total_count"] = registry["connectors"].size();
    
    // Save registry
    std::ofstream outFile(outputFile);
    outFile << registry.dump(2) << std::endl;
    
    std::cout << "✅ Registry generated with " << registry["connectors"].size() 
              << " connectors" << std::endl;
    std::cout << "📄 Registry saved to: " << outputFile << std::endl;
    
    return registry;
}

bool updateDownloadUrls(const std::string& registryFile, const std::string& releaseTag, 
                       const std::string& baseUrl = "") {
    if (!fs::exists(registryFile)) {
        std::cout << "❌ Registry file not found: " << registryFile << std::endl;
        return false;
    }
    
    std::string finalBaseUrl = baseUrl;
    if (finalBaseUrl.empty()) {
        std::string repo = getEnvVar("GITHUB_REPOSITORY", "laofahai/linch-mind");
        finalBaseUrl = "https://github.com/" + repo + "/releases/download/" + releaseTag;
    }
    
    try {
        std::ifstream file(registryFile);
        json registry;
        file >> registry;
        file.close();
        
        int updatedCount = 0;
        for (auto& [connectorId, connectorInfo] : registry["connectors"].items()) {
            // Support multi-platform downloads
            json platforms = json::object();
            
            // Check for platform-specific packages
            std::vector<std::string> supportedPlatforms = {"linux-x64", "macos-x64", "windows-x64"};
            
            for (const std::string& platform : supportedPlatforms) {
                std::string zipFilename = connectorId + "-connector-" + platform + ".zip";
                std::string downloadUrl = finalBaseUrl + "/" + zipFilename;
                
                platforms[platform] = {
                    {"download_url", downloadUrl},
                    {"supported", true},
                    {"last_updated", getCurrentTimestamp()}
                };
            }
            
            // Update connector info with platform support
            json oldPlatforms = connectorInfo.value("platforms", json::object());
            connectorInfo["platforms"] = platforms;
            
            // Keep backward compatibility with single download_url
            std::string defaultZip = connectorId + "-connector-linux-x64.zip";
            std::string defaultUrl = finalBaseUrl + "/" + defaultZip;
            connectorInfo["download_url"] = defaultUrl;
            
            if (oldPlatforms != platforms) {
                std::cout << "🔗 Updated platform URLs for " << connectorId << std::endl;
                updatedCount++;
            }
        }
        
        registry["last_updated"] = getCurrentTimestamp();
        registry["metadata"]["release_tag"] = releaseTag;
        
        std::ofstream outFile(registryFile);
        outFile << registry.dump(2) << std::endl;
        
        std::cout << "✅ Updated " << updatedCount << " download URLs in registry" << std::endl;
        return true;
        
    } catch (const std::exception& e) {
        std::cout << "❌ Error updating download URLs: " << e.what() << std::endl;
        return false;
    }
}

void printUsage(const char* programName) {
    std::cout << "Usage: " << programName << " [options]" << std::endl;
    std::cout << "Options:" << std::endl;
    std::cout << "  --dir <path>        Connectors directory path (default: .)" << std::endl;
    std::cout << "  --output <file>     Output file name (default: registry.json)" << std::endl;
    std::cout << "  --format            Format output with summary" << std::endl;
    std::cout << "  --update-urls <tag> Update download URLs with release tag" << std::endl;
    std::cout << "  --base-url <url>    Custom base URL for downloads" << std::endl;
    std::cout << "  --help              Show this help message" << std::endl;
}

int main(int argc, char* argv[]) {
    std::string connectorsDir = ".";
    std::string outputFile = "registry.json";
    bool formatOutput = false;
    std::string updateUrls;
    std::string baseUrl;
    
    static struct option longOptions[] = {
        {"dir", required_argument, 0, 'd'},
        {"output", required_argument, 0, 'o'},
        {"format", no_argument, 0, 'f'},
        {"update-urls", required_argument, 0, 'u'},
        {"base-url", required_argument, 0, 'b'},
        {"help", no_argument, 0, 'h'},
        {0, 0, 0, 0}
    };
    
    int optionIndex = 0;
    int c;
    
    while ((c = getopt_long(argc, argv, "d:o:fu:b:h", longOptions, &optionIndex)) != -1) {
        switch (c) {
            case 'd':
                connectorsDir = optarg;
                break;
            case 'o':
                outputFile = optarg;
                break;
            case 'f':
                formatOutput = true;
                break;
            case 'u':
                updateUrls = optarg;
                break;
            case 'b':
                baseUrl = optarg;
                break;
            case 'h':
                printUsage(argv[0]);
                return 0;
            default:
                printUsage(argv[0]);
                return 1;
        }
    }
    
    try {
        // Update URLs mode
        if (!updateUrls.empty()) {
            if (!fs::exists(outputFile)) {
                std::cout << "❌ Registry file does not exist: " << outputFile << std::endl;
                return 1;
            }
            
            bool success = updateDownloadUrls(outputFile, updateUrls, baseUrl);
            return success ? 0 : 1;
        }
        
        // Normal generation mode
        if (!fs::exists(connectorsDir)) {
            std::cout << "❌ Directory does not exist: " << connectorsDir << std::endl;
            return 1;
        }
        
        json registry = generateRegistry(connectorsDir, outputFile);
        
        if (formatOutput) {
            std::cout << "\n📋 Registry Summary:" << std::endl;
            std::cout << "   Total connectors: " << registry["metadata"]["total_count"] << std::endl;
            
            for (const auto& [connectorId, info] : registry["connectors"].items()) {
                std::string action = info.value("action", "kept");
                std::string actionEmoji = "🔧";
                if (action == "added") actionEmoji = "🆕";
                else if (action == "updated") actionEmoji = "🔄";
                else if (action == "kept") actionEmoji = "✅";
                
                std::string downloadStatus = info.contains("download_url") ? "📥" : "❓";
                
                std::cout << "   " << actionEmoji << " " << connectorId 
                          << " v" << info["version"] << " (" << info["type"] << ") " 
                          << downloadStatus << std::endl;
                
                if (info.contains("download_url")) {
                    std::cout << "      📍 " << info["download_url"] << std::endl;
                }
            }
        }
        
        return 0;
        
    } catch (const std::exception& e) {
        std::cout << "❌ Error: " << e.what() << std::endl;
        return 1;
    }
}