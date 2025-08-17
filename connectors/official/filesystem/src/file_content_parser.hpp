#pragma once

#include <string>
#include <vector>
#include <memory>
#include <unordered_map>

namespace linch_connector {

/**
 * 文件内容信息
 */
struct FileContent {
    std::string filePath;           // 文件路径
    std::string fileName;           // 文件名
    std::string extension;          // 文件扩展名
    uint64_t fileSize = 0;         // 文件大小
    int64_t modifiedTime = 0;      // 修改时间
    
    std::string textContent;        // 文本内容（如果可提取）
    std::string encoding = "utf-8"; // 编码格式
    std::unordered_map<std::string, std::string> metadata; // 额外元数据
    
    bool contentExtracted = false;  // 是否成功提取内容
    std::string errorMessage;       // 错误信息（如果有）
};

/**
 * 支持的文件类型
 */
enum class FileType {
    PLAIN_TEXT,     // 纯文本文件 (.txt, .md, .log, .json, .xml, .csv)
    SOURCE_CODE,    // 源代码文件 (.cpp, .py, .js, .java, .html, .css)
    DOCUMENT,       // 文档文件 (.pdf, .doc, .docx)
    SPREADSHEET,    // 电子表格 (.xls, .xlsx, .csv)
    IMAGE,          // 图片文件 (.jpg, .png, .gif) - 可能支持OCR
    UNKNOWN         // 未知类型
};

/**
 * 文件内容解析器接口
 * 
 * 支持多种文件格式的内容提取和解析
 */
class IFileContentParser {
public:
    virtual ~IFileContentParser() = default;
    
    /**
     * 解析文件内容
     * @param filePath 文件路径
     * @param maxSize 最大读取大小限制（字节）
     * @return 文件内容信息
     */
    virtual FileContent parseFile(const std::string& filePath, size_t maxSize = 10 * 1024 * 1024) = 0;
    
    /**
     * 检查是否支持该文件类型
     * @param filePath 文件路径
     * @return 是否支持
     */
    virtual bool isSupported(const std::string& filePath) const = 0;
    
    /**
     * 获取文件类型
     * @param filePath 文件路径
     * @return 文件类型
     */
    virtual FileType getFileType(const std::string& filePath) const = 0;
    
    /**
     * 获取支持的文件扩展名列表
     * @return 扩展名列表
     */
    virtual std::vector<std::string> getSupportedExtensions() const = 0;
    
    /**
     * 设置解析选项
     * @param options 选项映射
     */
    virtual void setOptions(const std::unordered_map<std::string, std::string>& options) = 0;
    
    /**
     * 获取解析器名称
     * @return 解析器名称
     */
    virtual std::string getParserName() const = 0;
};

/**
 * 基础文件内容解析器实现
 * 支持纯文本和源代码文件的基本解析
 */
class BasicFileContentParser : public IFileContentParser {
public:
    BasicFileContentParser();
    ~BasicFileContentParser() override = default;
    
    FileContent parseFile(const std::string& filePath, size_t maxSize = 10 * 1024 * 1024) override;
    bool isSupported(const std::string& filePath) const override;
    FileType getFileType(const std::string& filePath) const override;
    std::vector<std::string> getSupportedExtensions() const override;
    void setOptions(const std::unordered_map<std::string, std::string>& options) override;
    std::string getParserName() const override { return "BasicFileContentParser"; }

private:
    // 支持的扩展名映射
    std::unordered_map<std::string, FileType> m_extensionMap;
    
    // 解析选项
    bool m_extractBinaryAsHex = false;      // 是否将二进制文件转换为十六进制
    bool m_detectEncoding = true;           // 是否自动检测编码
    size_t m_maxLineLength = 1000;          // 最大行长度
    
    /**
     * 初始化支持的文件扩展名
     */
    void initializeSupportedExtensions();
    
    /**
     * 解析纯文本文件
     */
    FileContent parsePlainText(const std::string& filePath, size_t maxSize);
    
    /**
     * 解析源代码文件
     */
    FileContent parseSourceCode(const std::string& filePath, size_t maxSize);
    
    /**
     * 检测文件编码
     */
    std::string detectEncoding(const std::string& filePath);
    
    /**
     * 读取文件内容
     */
    std::string readFileContent(const std::string& filePath, size_t maxSize, const std::string& encoding);
    
    /**
     * 获取文件基础信息
     */
    void getFileBasicInfo(const std::string& filePath, FileContent& content);
    
    /**
     * 提取文件扩展名
     */
    std::string getFileExtension(const std::string& filePath) const;
    
    /**
     * 检查是否为文本文件（基于内容）
     */
    bool isTextFile(const std::string& filePath) const;
};

/**
 * 创建默认的文件内容解析器
 * @return 解析器实例
 */
std::unique_ptr<IFileContentParser> createDefaultFileContentParser();

} // namespace linch_connector