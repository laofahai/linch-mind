#include "macos_mdquery_provider.hpp"

#ifdef __APPLE__

#include <cstdlib>
#include <iostream>
#include <sstream>
#include <filesystem>
#include <sys/stat.h>
#include <optional>

namespace linch_connector {

MacOSMdqueryProvider::MacOSMdqueryProvider() {
    m_available = checkMdqueryAvailable();
    if (m_available) {
        std::cout << "✅ macOS mdquery provider initialized successfully" << std::endl;
    } else {
        std::cout << "❌ mdquery not available on this system" << std::endl;
    }
}

bool MacOSMdqueryProvider::isAvailable() const {
    return m_available;
}

std::string MacOSMdqueryProvider::getProviderName() const {
    return "macOS Spotlight (mdquery)";
}

std::vector<FileRecord> MacOSMdqueryProvider::queryDocuments() {
    std::string query = buildDocumentQuery();
    return executeMdquery(query);
}

std::vector<FileRecord> MacOSMdqueryProvider::queryByExtensions(const std::vector<std::string>& extensions) {
    std::string query = buildExtensionQuery(extensions);
    return executeMdquery(query);
}

std::vector<FileRecord> MacOSMdqueryProvider::queryByDirectory(const std::string& directory, bool recursive) {
    std::string query = buildDirectoryQuery(directory, recursive);
    return executeMdquery(query);
}

std::vector<FileRecord> MacOSMdqueryProvider::queryByNamePattern(const std::string& pattern) {
    std::string query = "kMDItemDisplayName == \"*" + pattern + "*\"c";
    return executeMdquery(query);
}

std::vector<FileRecord> MacOSMdqueryProvider::executeMdquery(const std::string& query) {
    std::vector<FileRecord> results;
    
    if (!m_available) {
        std::cout << "❌ mdquery not available" << std::endl;
        return results;
    }
    
    // 构建完整的mdfind命令
    std::string command = "mdfind \"" + query + "\"";
    std::cout << "🔍 Executing: " << command << std::endl;
    
    // 执行命令
    FILE* pipe = popen(command.c_str(), "r");
    if (!pipe) {
        std::cout << "❌ Failed to execute mdfind command" << std::endl;
        return results;
    }
    
    char buffer[4096];
    std::string output;
    
    // 读取命令输出
    while (fgets(buffer, sizeof(buffer), pipe) != nullptr) {
        output += buffer;
    }
    
    int result = pclose(pipe);
    if (result != 0) {
        std::cout << "❌ mdfind command failed with exit code: " << result << std::endl;
        return results;
    }
    
    // 解析输出
    std::istringstream stream(output);
    std::string line;
    
    while (std::getline(stream, line)) {
        // 跳过空行
        if (line.empty()) continue;
        
        // 解析文件信息
        auto fileRecord = parseFileInfo(line);
        if (fileRecord.has_value()) {
            results.push_back(fileRecord.value());
        }
    }
    
    std::cout << "📊 Found " << results.size() << " files" << std::endl;
    return results;
}

std::optional<FileRecord> MacOSMdqueryProvider::parseFileInfo(const std::string& filePath) {
    // 移除路径中的换行符和空白字符
    std::string cleanPath = filePath;
    cleanPath.erase(cleanPath.find_last_not_of(" \n\r\t") + 1);
    
    if (cleanPath.empty()) {
        return std::nullopt;
    }
    
    // 客户端过滤：排除开发缓存、临时文件、系统文件
    if (// 开发工具缓存
        cleanPath.find("/node_modules/") != std::string::npos ||
        cleanPath.find("/__pycache__/") != std::string::npos ||
        // cleanPath.find("/.git/") != std::string::npos ||  // 保留.git，用户可能需要搜索git信息
        cleanPath.find("/.svn/") != std::string::npos ||
        cleanPath.find("/.hg/") != std::string::npos ||
        cleanPath.find("/target/debug/") != std::string::npos ||
        cleanPath.find("/target/release/") != std::string::npos ||
        cleanPath.find("/.gradle/") != std::string::npos ||
        cleanPath.find("/build/") != std::string::npos ||
        cleanPath.find("/dist/") != std::string::npos ||
        cleanPath.find("/.venv/") != std::string::npos ||
        cleanPath.find("/venv/") != std::string::npos ||
        cleanPath.find("/.cache/") != std::string::npos ||
        cleanPath.find("/.npm/") != std::string::npos ||
        cleanPath.find("/.yarn/") != std::string::npos ||
        cleanPath.find("/.pnpm/") != std::string::npos ||
        
        // IDE和编辑器文件
        cleanPath.find("/.vscode/") != std::string::npos ||
        cleanPath.find("/.idea/") != std::string::npos ||
        cleanPath.find("/.vs/") != std::string::npos ||
        cleanPath.find("/.settings/") != std::string::npos ||
        cleanPath.find("/.metadata/") != std::string::npos ||
        
        // 系统临时和虚拟文件
        cleanPath.find("/System/Volumes/VM/") != std::string::npos ||
        cleanPath.find("/System/Volumes/Preboot/") != std::string::npos ||
        cleanPath.find("/private/tmp/") != std::string::npos ||
        cleanPath.find("/private/var/tmp/") != std::string::npos ||
        cleanPath.find("/private/var/log/") != std::string::npos ||
        cleanPath.find("/private/var/db/") != std::string::npos ||
        cleanPath.find("/private/var/run/") != std::string::npos ||
        
        // 回收站和备份
        cleanPath.find("/Trash/") != std::string::npos ||
        cleanPath.find("/.Trash/") != std::string::npos ||
        cleanPath.find("/.Trashes/") != std::string::npos ||
        cleanPath.find("/Time Machine Backups/") != std::string::npos ||
        cleanPath.find("/.TemporaryItems/") != std::string::npos ||
        
        // 应用缓存和临时文件
        cleanPath.find("/Library/Caches/") != std::string::npos ||
        cleanPath.find("/Library/Logs/") != std::string::npos ||
        cleanPath.find("/Library/Application Support/Crash Reports/") != std::string::npos ||
        
        // 隐藏系统文件
        cleanPath.find("/.DS_Store") != std::string::npos ||
        cleanPath.find("/.localized") != std::string::npos ||
        cleanPath.find("/.fseventsd/") != std::string::npos ||
        cleanPath.find("/.Spotlight-V100/") != std::string::npos ||
        cleanPath.find("/.DocumentRevisions-V100/") != std::string::npos) {
        return std::nullopt;
    }
    
    try {
        // 检查文件是否存在
        if (!std::filesystem::exists(cleanPath)) {
            return std::nullopt;
        }
        
        // 跳过目录
        if (std::filesystem::is_directory(cleanPath)) {
            return std::nullopt;
        }
        
        std::filesystem::path path(cleanPath);
        FileRecord record;
        record.path = cleanPath;
        record.name = path.filename().string();
        
        // 获取扩展名
        if (path.has_extension()) {
            std::string ext = path.extension().string();
            if (!ext.empty() && ext[0] == '.') {
                ext = ext.substr(1); // 移除开头的点
            }
            record.extension = ext;
        }
        
        // 获取文件大小和修改时间
        std::error_code ec;
        auto fileSize = std::filesystem::file_size(cleanPath, ec);
        if (!ec) {
            record.size = static_cast<uint64_t>(fileSize);
        }
        
        auto lastWriteTime = std::filesystem::last_write_time(cleanPath, ec);
        if (!ec) {
            auto sctp = std::chrono::time_point_cast<std::chrono::system_clock::duration>(
                lastWriteTime - std::filesystem::file_time_type::clock::now() + std::chrono::system_clock::now()
            );
            record.modified_time = std::chrono::system_clock::to_time_t(sctp);
        }
        
        return record;
    }
    catch (const std::exception& e) {
        std::cout << "⚠️  Error parsing file info for " << cleanPath << ": " << e.what() << std::endl;
        return std::nullopt;
    }
}

std::string MacOSMdqueryProvider::buildDocumentQuery() {
    // 全盘索引：查询所有文件，使用客户端过滤排除不需要的文件
    // 简单查询，让Spotlight返回所有文件，然后在parseFileInfo中过滤
    return "*";  // 最简单的查询，匹配所有文件
}

std::string MacOSMdqueryProvider::buildExtensionQuery(const std::vector<std::string>& extensions) {
    if (extensions.empty()) {
        return "";
    }
    
    std::string query;
    for (size_t i = 0; i < extensions.size(); ++i) {
        if (i > 0) {
            query += " || ";
        }
        query += "kMDItemDisplayName == '*." + extensions[i] + "'";
    }
    
    return query;
}

std::string MacOSMdqueryProvider::buildDirectoryQuery(const std::string& directory, bool recursive) {
    std::string query = "kMDItemPath == '" + directory;
    if (recursive) {
        query += "/*'";
    } else {
        query += "/*' && kMDItemPath != '" + directory + "/*/*'";
    }
    return query;
}

bool MacOSMdqueryProvider::checkMdqueryAvailable() {
    // 检查mdfind命令是否存在
    int result = system("which mdfind > /dev/null 2>&1");
    return result == 0;
}

} // namespace linch_connector

#endif // __APPLE__