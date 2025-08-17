#include "file_content_parser.hpp"
#include <fstream>
#include <sstream>
#include <iostream>
#include <algorithm>
#include <filesystem>
#include <sys/stat.h>
#include <cctype>

namespace linch_connector {

BasicFileContentParser::BasicFileContentParser() {
    initializeSupportedExtensions();
}

void BasicFileContentParser::initializeSupportedExtensions() {
    // 纯文本文件
    m_extensionMap[".txt"] = FileType::PLAIN_TEXT;
    m_extensionMap[".md"] = FileType::PLAIN_TEXT;
    m_extensionMap[".log"] = FileType::PLAIN_TEXT;
    m_extensionMap[".json"] = FileType::PLAIN_TEXT;
    m_extensionMap[".xml"] = FileType::PLAIN_TEXT;
    m_extensionMap[".csv"] = FileType::PLAIN_TEXT;
    m_extensionMap[".yaml"] = FileType::PLAIN_TEXT;
    m_extensionMap[".yml"] = FileType::PLAIN_TEXT;
    m_extensionMap[".ini"] = FileType::PLAIN_TEXT;
    m_extensionMap[".cfg"] = FileType::PLAIN_TEXT;
    m_extensionMap[".conf"] = FileType::PLAIN_TEXT;
    m_extensionMap[".toml"] = FileType::PLAIN_TEXT;
    
    // 源代码文件
    m_extensionMap[".cpp"] = FileType::SOURCE_CODE;
    m_extensionMap[".hpp"] = FileType::SOURCE_CODE;
    m_extensionMap[".c"] = FileType::SOURCE_CODE;
    m_extensionMap[".h"] = FileType::SOURCE_CODE;
    m_extensionMap[".py"] = FileType::SOURCE_CODE;
    m_extensionMap[".js"] = FileType::SOURCE_CODE;
    m_extensionMap[".ts"] = FileType::SOURCE_CODE;
    m_extensionMap[".java"] = FileType::SOURCE_CODE;
    m_extensionMap[".html"] = FileType::SOURCE_CODE;
    m_extensionMap[".css"] = FileType::SOURCE_CODE;
    m_extensionMap[".scss"] = FileType::SOURCE_CODE;
    m_extensionMap[".php"] = FileType::SOURCE_CODE;
    m_extensionMap[".go"] = FileType::SOURCE_CODE;
    m_extensionMap[".rs"] = FileType::SOURCE_CODE;
    m_extensionMap[".swift"] = FileType::SOURCE_CODE;
    m_extensionMap[".kt"] = FileType::SOURCE_CODE;
    m_extensionMap[".dart"] = FileType::SOURCE_CODE;
    m_extensionMap[".rb"] = FileType::SOURCE_CODE;
    m_extensionMap[".sh"] = FileType::SOURCE_CODE;
    m_extensionMap[".sql"] = FileType::SOURCE_CODE;
    m_extensionMap[".r"] = FileType::SOURCE_CODE;
    m_extensionMap[".m"] = FileType::SOURCE_CODE;
    m_extensionMap[".mm"] = FileType::SOURCE_CODE;
}

FileContent BasicFileContentParser::parseFile(const std::string& filePath, size_t maxSize) {
    FileContent content;
    content.filePath = filePath;
    
    // 获取文件基础信息
    getFileBasicInfo(filePath, content);
    
    // 检查文件是否存在和可读
    if (!std::filesystem::exists(filePath)) {
        content.errorMessage = "文件不存在";
        return content;
    }
    
    if (!std::filesystem::is_regular_file(filePath)) {
        content.errorMessage = "不是常规文件";
        return content;
    }
    
    // 检查文件大小
    auto fileSize = std::filesystem::file_size(filePath);
    if (fileSize > maxSize) {
        content.errorMessage = "文件过大，超过限制：" + std::to_string(maxSize) + " 字节";
        return content;
    }
    
    // 获取文件类型
    FileType fileType = getFileType(filePath);
    
    try {
        switch (fileType) {
            case FileType::PLAIN_TEXT:
                content = parsePlainText(filePath, maxSize);
                break;
            case FileType::SOURCE_CODE:
                content = parseSourceCode(filePath, maxSize);
                break;
            default:
                // 对于未知类型，尝试作为文本文件处理
                if (isTextFile(filePath)) {
                    content = parsePlainText(filePath, maxSize);
                } else {
                    content.errorMessage = "不支持的文件类型";
                }
                break;
        }
    } catch (const std::exception& e) {
        content.errorMessage = "解析文件时出错: " + std::string(e.what());
        content.contentExtracted = false;
    }
    
    return content;
}

bool BasicFileContentParser::isSupported(const std::string& filePath) const {
    std::string extension = getFileExtension(filePath);
    std::transform(extension.begin(), extension.end(), extension.begin(), ::tolower);
    
    auto it = m_extensionMap.find(extension);
    if (it != m_extensionMap.end()) {
        return true;
    }
    
    // 对于未知扩展名，检查是否为文本文件
    return isTextFile(filePath);
}

FileType BasicFileContentParser::getFileType(const std::string& filePath) const {
    std::string extension = getFileExtension(filePath);
    std::transform(extension.begin(), extension.end(), extension.begin(), ::tolower);
    
    auto it = m_extensionMap.find(extension);
    if (it != m_extensionMap.end()) {
        return it->second;
    }
    
    return FileType::UNKNOWN;
}

std::vector<std::string> BasicFileContentParser::getSupportedExtensions() const {
    std::vector<std::string> extensions;
    for (const auto& pair : m_extensionMap) {
        extensions.push_back(pair.first);
    }
    return extensions;
}

void BasicFileContentParser::setOptions(const std::unordered_map<std::string, std::string>& options) {
    for (const auto& [key, value] : options) {
        if (key == "extract_binary_as_hex") {
            m_extractBinaryAsHex = (value == "true" || value == "1");
        } else if (key == "detect_encoding") {
            m_detectEncoding = (value == "true" || value == "1");
        } else if (key == "max_line_length") {
            try {
                m_maxLineLength = std::stoull(value);
            } catch (const std::exception&) {
                // 使用默认值
                m_maxLineLength = 1000;
            }
        }
    }
}

FileContent BasicFileContentParser::parsePlainText(const std::string& filePath, size_t maxSize) {
    FileContent content;
    content.filePath = filePath;
    getFileBasicInfo(filePath, content);
    
    // 检测编码
    std::string encoding = "utf-8";
    if (m_detectEncoding) {
        encoding = detectEncoding(filePath);
        content.encoding = encoding;
    }
    
    // 读取文件内容
    content.textContent = readFileContent(filePath, maxSize, encoding);
    content.contentExtracted = !content.textContent.empty();
    
    // 添加元数据
    content.metadata["file_type"] = "plain_text";
    content.metadata["encoding"] = content.encoding;
    
    // 统计行数
    size_t lineCount = std::count(content.textContent.begin(), content.textContent.end(), '\n') + 1;
    content.metadata["line_count"] = std::to_string(lineCount);
    
    return content;
}

FileContent BasicFileContentParser::parseSourceCode(const std::string& filePath, size_t maxSize) {
    FileContent content;
    content.filePath = filePath;
    getFileBasicInfo(filePath, content);
    
    // 源代码文件通常使用UTF-8编码
    std::string encoding = "utf-8";
    if (m_detectEncoding) {
        encoding = detectEncoding(filePath);
    }
    content.encoding = encoding;
    
    // 读取文件内容
    content.textContent = readFileContent(filePath, maxSize, encoding);
    content.contentExtracted = !content.textContent.empty();
    
    // 添加源代码特有的元数据
    content.metadata["file_type"] = "source_code";
    content.metadata["encoding"] = content.encoding;
    content.metadata["language"] = content.extension;
    
    // 统计行数和大致代码行数（非空行）
    size_t lineCount = 0;
    size_t codeLineCount = 0;
    std::istringstream stream(content.textContent);
    std::string line;
    
    while (std::getline(stream, line)) {
        lineCount++;
        // 简单的非空行检测
        std::string trimmed = line;
        trimmed.erase(0, trimmed.find_first_not_of(" \t\r\n"));
        trimmed.erase(trimmed.find_last_not_of(" \t\r\n") + 1);
        if (!trimmed.empty()) {
            codeLineCount++;
        }
    }
    
    content.metadata["line_count"] = std::to_string(lineCount);
    content.metadata["code_line_count"] = std::to_string(codeLineCount);
    
    return content;
}

std::string BasicFileContentParser::detectEncoding(const std::string& filePath) {
    // 简单的编码检测实现
    // 在实际项目中，可能需要使用更复杂的编码检测库
    
    std::ifstream file(filePath, std::ios::binary);
    if (!file.is_open()) {
        return "utf-8"; // 默认编码
    }
    
    // 读取文件开头的一些字节来检测编码
    char buffer[4096];
    file.read(buffer, sizeof(buffer));
    std::streamsize bytesRead = file.gcount();
    file.close();
    
    if (bytesRead >= 3) {
        // 检测UTF-8 BOM
        if (static_cast<unsigned char>(buffer[0]) == 0xEF && 
            static_cast<unsigned char>(buffer[1]) == 0xBB && 
            static_cast<unsigned char>(buffer[2]) == 0xBF) {
            return "utf-8-bom";
        }
        
        // 检测UTF-16 BOM
        if ((static_cast<unsigned char>(buffer[0]) == 0xFF && static_cast<unsigned char>(buffer[1]) == 0xFE) ||
            (static_cast<unsigned char>(buffer[0]) == 0xFE && static_cast<unsigned char>(buffer[1]) == 0xFF)) {
            return "utf-16";
        }
    }
    
    // 简单的UTF-8有效性检查
    bool isValidUTF8 = true;
    for (std::streamsize i = 0; i < bytesRead; ++i) {
        unsigned char byte = static_cast<unsigned char>(buffer[i]);
        
        // ASCII范围
        if (byte <= 0x7F) {
            continue;
        }
        
        // 多字节UTF-8序列
        int extraBytes = 0;
        if ((byte & 0xE0) == 0xC0) extraBytes = 1;
        else if ((byte & 0xF0) == 0xE0) extraBytes = 2;
        else if ((byte & 0xF8) == 0xF0) extraBytes = 3;
        else {
            isValidUTF8 = false;
            break;
        }
        
        // 检查后续字节
        for (int j = 1; j <= extraBytes && (i + j) < bytesRead; ++j) {
            unsigned char nextByte = static_cast<unsigned char>(buffer[i + j]);
            if ((nextByte & 0xC0) != 0x80) {
                isValidUTF8 = false;
                break;
            }
        }
        
        if (!isValidUTF8) break;
        i += extraBytes;
    }
    
    return isValidUTF8 ? "utf-8" : "latin-1";
}

std::string BasicFileContentParser::readFileContent(const std::string& filePath, size_t maxSize, const std::string& encoding) {
    std::ifstream file(filePath, std::ios::binary);
    if (!file.is_open()) {
        throw std::runtime_error("无法打开文件: " + filePath);
    }
    
    // 确定实际读取大小
    file.seekg(0, std::ios::end);
    size_t fileSize = file.tellg();
    file.seekg(0, std::ios::beg);
    
    size_t readSize = std::min(fileSize, maxSize);
    
    std::string content;
    content.resize(readSize);
    
    file.read(&content[0], readSize);
    file.close();
    
    // 处理BOM - 内存优化：原地移除而非创建副本
    if (encoding == "utf-8-bom" && content.size() >= 3) {
        content.erase(0, 3); // 原地移除UTF-8 BOM，避免创建副本
    }
    
    // 限制行长度 - 内存优化：预先保留空间，减少重新分配
    if (m_maxLineLength > 0) {
        std::string result;
        result.reserve(content.size()); // 预分配空间
        
        size_t pos = 0;
        const std::string truncatedSuffix = "... [truncated]";
        
        while (pos < content.size()) {
            size_t lineEnd = content.find('\n', pos);
            bool hasNewline = (lineEnd != std::string::npos);
            if (!hasNewline) lineEnd = content.size();
            
            size_t lineLen = lineEnd - pos;
            
            if (lineLen > m_maxLineLength) {
                // 截断行
                result.append(content, pos, m_maxLineLength);
                result += truncatedSuffix;
            } else {
                // 保留完整行
                result.append(content, pos, lineLen);
            }
            
            // 保留换行符
            if (hasNewline) {
                result += '\n';
            }
            
            pos = lineEnd + 1;
        }
        
        content = std::move(result); // 移动语义避免副本
    }
    
    return content;
}

void BasicFileContentParser::getFileBasicInfo(const std::string& filePath, FileContent& content) {
    content.filePath = filePath;
    
    // 获取文件名
    auto path = std::filesystem::path(filePath);
    content.fileName = path.filename().string();
    content.extension = getFileExtension(filePath);
    
    try {
        // 获取文件大小
        content.fileSize = std::filesystem::file_size(filePath);
        
        // 获取修改时间
        auto ftime = std::filesystem::last_write_time(filePath);
        auto sctp = std::chrono::time_point_cast<std::chrono::system_clock::duration>(
            ftime - std::filesystem::file_time_type::clock::now() + std::chrono::system_clock::now()
        );
        content.modifiedTime = std::chrono::duration_cast<std::chrono::seconds>(sctp.time_since_epoch()).count();
    } catch (const std::exception& e) {
        content.errorMessage = "获取文件信息失败: " + std::string(e.what());
    }
}

std::string BasicFileContentParser::getFileExtension(const std::string& filePath) const {
    auto path = std::filesystem::path(filePath);
    std::string extension = path.extension().string();
    std::transform(extension.begin(), extension.end(), extension.begin(), ::tolower);
    return extension;
}

bool BasicFileContentParser::isTextFile(const std::string& filePath) const {
    // 简单的文本文件检测
    std::ifstream file(filePath, std::ios::binary);
    if (!file.is_open()) {
        return false;
    }
    
    // 读取文件开头的一些字节
    char buffer[512];
    file.read(buffer, sizeof(buffer));
    std::streamsize bytesRead = file.gcount();
    file.close();
    
    if (bytesRead == 0) {
        return true; // 空文件视为文本文件
    }
    
    // 检查是否包含过多的非文本字符
    size_t nonTextBytes = 0;
    for (std::streamsize i = 0; i < bytesRead; ++i) {
        unsigned char byte = static_cast<unsigned char>(buffer[i]);
        
        // ASCII控制字符（除了常见的空白字符）
        if (byte < 32 && byte != '\t' && byte != '\n' && byte != '\r') {
            nonTextBytes++;
        }
        // 高位字节（可能是二进制数据）
        else if (byte > 126 && byte < 128) {
            nonTextBytes++;
        }
    }
    
    // 如果非文本字节比例超过30%，则认为是二进制文件
    double nonTextRatio = static_cast<double>(nonTextBytes) / bytesRead;
    return nonTextRatio < 0.3;
}

// 工厂函数实现
std::unique_ptr<IFileContentParser> createDefaultFileContentParser() {
    return std::make_unique<BasicFileContentParser>();
}

} // namespace linch_connector