#pragma once

#include "file_index_query.hpp"
#include <optional>

#ifdef __APPLE__

namespace linch_connector {

/**
 * macOS Spotlight mdquery 实现
 * 利用系统已有的Spotlight索引进行文件查询
 */
class MacOSMdqueryProvider : public IFileIndexQuery {
public:
    MacOSMdqueryProvider();
    ~MacOSMdqueryProvider() override = default;
    
    // 实现基础查询接口
    std::vector<FileRecord> queryDocuments() override;
    std::vector<FileRecord> queryByExtensions(const std::vector<std::string>& extensions) override;
    std::vector<FileRecord> queryByDirectory(const std::string& directory, bool recursive = true) override;
    std::vector<FileRecord> queryByNamePattern(const std::string& pattern) override;
    
    bool isAvailable() const override;
    std::string getProviderName() const override;

private:
    /**
     * 执行mdquery命令并解析结果
     * @param query mdquery查询语句
     * @return 解析后的文件记录列表
     */
    std::vector<FileRecord> executeMdquery(const std::string& query);
    
    /**
     * 解析mdquery输出的文件路径，获取文件信息
     * @param filePath 文件路径
     * @return 文件记录，如果文件无效则返回空optional
     */
    std::optional<FileRecord> parseFileInfo(const std::string& filePath);
    
    /**
     * 构建文档类型的mdquery查询语句
     * @return 查询语句
     */
    std::string buildDocumentQuery();
    
    /**
     * 构建扩展名查询语句
     * @param extensions 扩展名列表
     * @return 查询语句
     */
    std::string buildExtensionQuery(const std::vector<std::string>& extensions);
    
    /**
     * 构建目录查询语句
     * @param directory 目录路径
     * @param recursive 是否递归
     * @return 查询语句
     */
    std::string buildDirectoryQuery(const std::string& directory, bool recursive);
    
    /**
     * 验证mdquery命令是否可用
     */
    bool checkMdqueryAvailable();
    
    bool m_available = false;
};

} // namespace linch_connector

#endif // __APPLE__