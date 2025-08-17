#pragma once

#include <vector>
#include <string>
#include <memory>

namespace linch_connector {

/**
 * 文件基础信息
 */
struct FileRecord {
    std::string path;           // 文件完整路径
    std::string name;           // 文件名
    std::string extension;      // 文件扩展名
    uint64_t size = 0;         // 文件大小（字节）
    int64_t modified_time = 0; // 修改时间（Unix时间戳）
    
    FileRecord() = default;
    FileRecord(const std::string& p, const std::string& n) 
        : path(p), name(n) {}
};

/**
 * 跨平台文件索引查询接口
 * 
 * 支持的平台实现：
 * - macOS: mdquery (Spotlight)
 * - Windows: 文件搜索API
 * - Linux: locate/updatedb
 */
class IFileIndexQuery {
public:
    virtual ~IFileIndexQuery() = default;
    
    /**
     * 查询所有文档文件
     * @return 文档文件列表
     */
    virtual std::vector<FileRecord> queryDocuments() = 0;
    
    /**
     * 查询指定类型的文件
     * @param extensions 文件扩展名列表，如 {"pdf", "doc", "txt"}
     * @return 匹配的文件列表
     */
    virtual std::vector<FileRecord> queryByExtensions(const std::vector<std::string>& extensions) = 0;
    
    /**
     * 查询指定目录下的文件
     * @param directory 目录路径
     * @param recursive 是否递归查询子目录
     * @return 目录下的文件列表
     */
    virtual std::vector<FileRecord> queryByDirectory(const std::string& directory, bool recursive = true) = 0;
    
    /**
     * 根据文件名模糊查询
     * @param pattern 文件名模式，支持通配符
     * @return 匹配的文件列表
     */
    virtual std::vector<FileRecord> queryByNamePattern(const std::string& pattern) = 0;
    
    /**
     * 检查索引系统是否可用
     * @return 是否可用
     */
    virtual bool isAvailable() const = 0;
    
    /**
     * 获取查询提供者名称
     * @return 提供者名称
     */
    virtual std::string getProviderName() const = 0;
};

/**
 * 创建平台特定的文件索引查询器
 * @return 查询器实例，如果平台不支持则返回nullptr
 */
std::unique_ptr<IFileIndexQuery> createFileIndexQuery();

} // namespace linch_connector