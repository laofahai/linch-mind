#include "linch_connector/file_filter.hpp"
#include "linch_connector/utils.hpp"
#include <iostream>
#include <algorithm>
#include <cctype>

namespace linch_connector {

FileFilter::FileFilter(bool enablePlatformSpecific)
    : m_enablePlatformSpecific(enablePlatformSpecific)
    , m_maxFileSize(100 * 1024 * 1024) // 默认100MB
{
    initializePredefinedRules();
}

bool FileFilter::shouldFilter(const std::string& path) const {
    m_stats.totalChecked++;

    // 1. 验证路径有效性
    if (!isValidPath(path)) {
        m_stats.invalidPaths++;
        m_stats.filtered++;
        return true;
    }

    // 2. 检查文件大小
    if (isOversized(path)) {
        m_stats.oversizedFiles++;
        m_stats.filtered++;
        return true;
    }

    // 3. 检查扩展名白名单
    if (!m_includeExtensions.empty() && !isIncludedExtension(path)) {
        m_stats.extensionFiltered++;
        m_stats.filtered++;
        return true;
    }

    // 4. 检查常见排除目录
    std::filesystem::path fsPath(path);
    for (const auto& part : fsPath) {
        if (isCommonExcludeDir(part.string())) {
            m_stats.patternFiltered++;
            m_stats.filtered++;
            return true;
        }
    }

    // 5. 检查常见排除文件
    if (isCommonExcludeFile(getFileName(path))) {
        m_stats.patternFiltered++;
        m_stats.filtered++;
        return true;
    }

    // 6. 检查二进制文件
    if (isBinaryFile(path)) {
        m_stats.patternFiltered++;
        m_stats.filtered++;
        return true;
    }

    // 7. 检查临时文件
    if (isTemporaryFile(path)) {
        m_stats.patternFiltered++;
        m_stats.filtered++;
        return true;
    }

    // 8. 检查平台特定排除规则
    if (m_enablePlatformSpecific && isPlatformSpecificExclude(path)) {
        m_stats.patternFiltered++;
        m_stats.filtered++;
        return true;
    }

    // 9. 检查自定义排除模式
    if (matchesExcludePattern(path)) {
        m_stats.patternFiltered++;
        m_stats.filtered++;
        return true;
    }

    return false;
}

bool FileFilter::isIncludedExtension(const std::string& path) const {
    if (m_includeExtensions.empty()) {
        return true; // 如果没有设置扩展名过滤，则包含所有文件
    }

    std::string ext = getExtension(path);
    return m_includeExtensions.find(ext) != m_includeExtensions.end();
}

bool FileFilter::isValidPath(const std::string& path) const {
    return utils::isValidFilePath(path);
}

std::string FileFilter::cleanPath(const std::string& path) const {
    return utils::cleanString(path);
}

void FileFilter::setIncludeExtensions(const std::set<std::string>& extensions) {
    m_includeExtensions = extensions;
    
    // 确保扩展名以点开头并且是小写
    for (auto it = m_includeExtensions.begin(); it != m_includeExtensions.end();) {
        std::string ext = *it;
        if (!ext.empty() && ext[0] != '.') {
            ext = "." + ext;
        }
        std::transform(ext.begin(), ext.end(), ext.begin(), ::tolower);
        
        it = m_includeExtensions.erase(it);
        m_includeExtensions.insert(ext);
    }
}

void FileFilter::addExcludePattern(const std::string& pattern) {
    try {
        m_excludePatterns.emplace_back(pattern);
    } catch (const std::regex_error& e) {
        std::cerr << "⚠️ 无效的排除正则表达式: " << pattern << " - " << e.what() << std::endl;
    }
}

void FileFilter::setExcludePatterns(const std::vector<std::string>& patterns) {
    m_excludePatterns.clear();
    for (const auto& pattern : patterns) {
        addExcludePattern(pattern);
    }
}

void FileFilter::setMaxFileSize(size_t maxSize) {
    m_maxFileSize = maxSize;
}

FileFilter::Statistics FileFilter::getStatistics() const {
    return m_stats;
}

void FileFilter::resetStatistics() {
    m_stats = Statistics{};
}

void FileFilter::initializePredefinedRules() {
    // 常见排除目录
    m_commonExcludeDirs = {
        ".git", ".svn", ".hg", ".bzr",                    // 版本控制
        "node_modules", "__pycache__", ".pytest_cache",   // 依赖和缓存
        ".vscode", ".idea", ".vs",                        // IDE配置
        "build", "dist", "target", "bin", "obj",          // 构建目录
        ".cache", ".tmp", "temp", "tmp",                  // 临时目录
        "vendor", "third_party", "3rdparty",             // 第三方库
        ".gradle", ".maven", ".npm",                      // 构建工具缓存
        "coverage", ".coverage", ".nyc_output",           // 测试覆盖率
        ".sass-cache", ".parcel-cache"                    // 前端构建缓存
    };

    // 常见排除文件
    m_commonExcludeFiles = {
        ".gitignore", ".gitkeep", ".gitmodules",          // Git相关
        ".dockerignore", "Dockerfile",                    // Docker相关
        ".env", ".env.local", ".env.example",             // 环境变量
        "package-lock.json", "yarn.lock", "pnpm-lock.yaml", // 包管理器锁文件
        "Pipfile.lock", "poetry.lock",                    // Python包管理器
        "Gemfile.lock", "composer.lock",                  // 其他语言包管理器
        "thumbs.db", "desktop.ini"                        // Windows系统文件
    };

    // 二进制文件扩展名
    m_binaryExtensions = {
        // 可执行文件
        ".exe", ".dll", ".so", ".dylib", ".bin", ".app",
        // 图像文件
        ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".ico", ".webp",
        // 音频文件
        ".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a",
        // 视频文件
        ".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm",
        // 压缩文件
        ".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz",
        // 数据库文件
        ".db", ".sqlite", ".mdb", ".accdb",
        // 字体文件
        ".ttf", ".otf", ".woff", ".woff2", ".eot",
        // Office文档（可选，根据需求决定是否包含）
        ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".pdf"
    };

    // 临时文件扩展名
    m_temporaryExtensions = {
        ".tmp", ".temp", ".bak", ".backup", ".old", ".orig",
        ".swp", ".swo", ".swap",                          // Vim临时文件
        ".DS_Store", ".Thumbs.db",                        // 系统临时文件
        ".log", ".out", ".err",                           // 日志文件
        ".cache", ".pid", ".lock"                         // 缓存和锁文件
    };

    // macOS特定排除文件
    m_macosSpecificExcludes = {
        ".DS_Store", ".AppleDouble", ".LSOverride",
        "._*", ".Spotlight-V100", ".Trashes",
        ".VolumeIcon.icns", ".com.apple.timemachine.donotpresent",
        ".fseventsd", ".TemporaryItems", ".apdisk"
    };

    // Windows特定排除文件
    m_windowsSpecificExcludes = {
        "Thumbs.db", "Thumbs.db:encryptable", "ehthumbs.db", "ehthumbs_vista.db",
        "Desktop.ini", "$RECYCLE.BIN", "System Volume Information",
        "hiberfil.sys", "pagefile.sys", "swapfile.sys"
    };

    // Linux特定排除文件
    m_linuxSpecificExcludes = {
        ".directory", ".Trash-*", ".gvfs", ".fuse_hidden*",
        ".nfs*", "lost+found"
    };
}

bool FileFilter::isCommonExcludeDir(const std::string& dirName) const {
    return m_commonExcludeDirs.find(dirName) != m_commonExcludeDirs.end();
}

bool FileFilter::isCommonExcludeFile(const std::string& fileName) const {
    return m_commonExcludeFiles.find(fileName) != m_commonExcludeFiles.end();
}

bool FileFilter::isBinaryFile(const std::string& path) const {
    std::string ext = getExtension(path);
    return m_binaryExtensions.find(ext) != m_binaryExtensions.end();
}

bool FileFilter::isTemporaryFile(const std::string& path) const {
    std::string ext = getExtension(path);
    if (m_temporaryExtensions.find(ext) != m_temporaryExtensions.end()) {
        return true;
    }

    std::string fileName = getFileName(path);
    
    // 检查临时文件命名模式
    if (fileName.find("~") == 0 ||                       // ~开头的临时文件
        fileName.find("#") == 0 ||                       // #开头的临时文件
        fileName.find(".#") == 0 ||                      // .#开头的临时文件
        fileName.find("~$") != std::string::npos) {      // ~$包含的临时文件
        return true;
    }

    return false;
}

bool FileFilter::isPlatformSpecificExclude(const std::string& path) const {
    std::string fileName = getFileName(path);

#ifdef __APPLE__
    if (m_macosSpecificExcludes.find(fileName) != m_macosSpecificExcludes.end()) {
        return true;
    }
    // 检查._开头的文件（Apple Double文件）
    if (fileName.find("._") == 0) {
        return true;
    }
#elif defined(_WIN32)
    if (m_windowsSpecificExcludes.find(fileName) != m_windowsSpecificExcludes.end()) {
        return true;
    }
#else // Linux/Unix
    if (m_linuxSpecificExcludes.find(fileName) != m_linuxSpecificExcludes.end()) {
        return true;
    }
#endif

    return false;
}

bool FileFilter::isOversized(const std::string& path) const {
    try {
        std::filesystem::path fsPath(path);
        if (std::filesystem::exists(fsPath) && std::filesystem::is_regular_file(fsPath)) {
            auto size = std::filesystem::file_size(fsPath);
            return size > m_maxFileSize;
        }
    } catch (const std::filesystem::filesystem_error&) {
        // 如果无法获取文件大小，认为文件可能有问题，过滤掉
        return true;
    }
    return false;
}

bool FileFilter::matchesExcludePattern(const std::string& path) const {
    for (const auto& pattern : m_excludePatterns) {
        try {
            if (std::regex_search(path, pattern)) {
                return true;
            }
        } catch (const std::regex_error&) {
            // 忽略正则表达式错误
            continue;
        }
    }
    return false;
}

std::string FileFilter::getExtension(const std::string& path) const {
    std::filesystem::path fsPath(path);
    std::string ext = fsPath.extension().string();
    std::transform(ext.begin(), ext.end(), ext.begin(), ::tolower);
    return ext;
}

std::string FileFilter::getFileName(const std::string& path) const {
    std::filesystem::path fsPath(path);
    return fsPath.filename().string();
}

// FileFilterConfig implementation

FileFilterConfig FileFilterConfig::createDefault() {
    FileFilterConfig config;
    config.includeExtensions = {
        ".txt", ".md", ".rst",                            // 文档
        ".cpp", ".hpp", ".c", ".h", ".cc", ".cxx",        // C/C++
        ".py", ".pyx", ".pyi",                            // Python
        ".js", ".ts", ".jsx", ".tsx", ".mjs",             // JavaScript/TypeScript
        ".java", ".kt", ".scala",                         // JVM语言
        ".rs", ".go", ".swift",                           // 现代语言
        ".php", ".rb", ".pl", ".sh", ".bash",             // 脚本语言
        ".html", ".htm", ".css", ".scss", ".sass",        // Web
        ".xml", ".json", ".yaml", ".yml", ".toml",        // 配置文件
        ".sql", ".graphql", ".proto"                      // 数据查询语言
    };
    
    config.excludePatterns = {
        R"(^\..*)",                                       // 隐藏文件
        R"(.*\.tmp$)",                                    // 临时文件
        R"(.*\.log$)",                                    // 日志文件
        R"(.*/\.git/.*)",                                 // Git目录
        R"(.*/node_modules/.*)",                          // Node.js模块
        R"(.*/__pycache__/.*)",                           // Python缓存
        R"(.*/\.DS_Store$)",                              // macOS系统文件
        R"(.*/\.Trash/.*)",                               // 废纸篓
        R"(.*/build/.*)",                                 // 构建目录
        R"(.*/dist/.*)",                                  // 分发目录
        R"(.*/target/.*)",                                // 目标目录
        R"(.*/bin/.*)",                                   // 二进制目录
        R"(.*/obj/.*)"                                    // 对象目录
    };
    
    return config;
}

FileFilterConfig FileFilterConfig::createDevelopment() {
    auto config = createDefault();
    
    // 开发环境包含更多代码文件类型
    config.includeExtensions.insert({
        ".cmake", ".make", ".dockerfile",                 // 构建文件
        ".gitignore", ".gitattributes",                   // Git配置
        ".editorconfig", ".clang-format",                 // 编辑器配置
        ".env", ".env.example",                           // 环境配置
        ".ini", ".conf", ".config"                        // 配置文件
    });
    
    return config;
}

FileFilterConfig FileFilterConfig::createDocuments() {
    FileFilterConfig config;
    
    // 文档环境主要关注文档文件
    config.includeExtensions = {
        ".txt", ".md", ".rst", ".adoc",                   // 纯文本文档
        ".doc", ".docx", ".odt",                          // Word文档
        ".pdf", ".rtf",                                   // 其他文档格式
        ".html", ".htm", ".xml",                          // 标记语言
        ".csv", ".tsv",                                   // 数据文件
        ".json", ".yaml", ".yml", ".toml"                 // 结构化数据
    };
    
    config.excludePatterns = {
        R"(^\..*)",                                       // 隐藏文件
        R"(.*/\.Trash/.*)",                               // 废纸篓
        R"(.*/temp/.*)",                                  // 临时目录
        R"(.*/cache/.*)"                                  // 缓存目录
    };
    
    // 文档通常较大，增加文件大小限制
    config.maxFileSize = 50 * 1024 * 1024; // 50MB
    
    return config;
}

} // namespace linch_connector