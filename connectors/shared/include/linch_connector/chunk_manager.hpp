#pragma once

#include <string>
#include <vector>
#include <chrono>
#include <memory>
#include <nlohmann/json.hpp>

namespace linch_connector {

/**
 * 分片传输管理器 - 遵循CLAUDE.md中的IPC架构铁律
 * 负责大数据的安全分片传输，确保IPC通信延迟<10ms
 */
class ChunkManager {
public:
    struct ChunkConfig {
        size_t maxChunkSize;
        size_t maxRetries;
        std::chrono::milliseconds retryDelay;
        size_t minChunkSize;
        double adaptiveThreshold;
        
        ChunkConfig() 
            : maxChunkSize(32 * 1024)
            , maxRetries(3)
            , retryDelay(std::chrono::milliseconds(50))
            , minChunkSize(1024)
            , adaptiveThreshold(0.8) {}
    };
    
    struct ChunkInfo {
        std::string sessionId;      // 分片会话ID
        size_t totalChunks;         // 总分片数
        size_t chunkIndex;          // 当前分片索引（从0开始）
        std::string data;           // 分片数据
        size_t originalSize;        // 原始数据总大小
        std::string checksum;       // 整体数据校验和
    };
    
    explicit ChunkManager(const ChunkConfig& config = ChunkConfig());
    ~ChunkManager() = default;
    
    // 禁用拷贝，确保资源管理最佳实践
    ChunkManager(const ChunkManager&) = delete;
    ChunkManager& operator=(const ChunkManager&) = delete;
    
    /**
     * 将JSON数据安全分片
     * @param jsonData 原始JSON数据
     * @param sessionId 分片会话ID（为空时自动生成）
     * @return 分片信息列表
     */
    std::vector<ChunkInfo> chunkifyJson(const nlohmann::json& jsonData, 
                                        const std::string& sessionId = "");
    
    /**
     * 创建分片传输消息（符合IPC协议）
     * @param chunk 分片信息
     * @return 符合IPC协议的JSON消息
     */
    nlohmann::json createChunkMessage(const ChunkInfo& chunk);
    
    /**
     * 从IPC消息解析分片信息
     * @param chunkMessage IPC格式的分片消息
     * @return 分片信息
     */
    ChunkInfo parseChunkMessage(const nlohmann::json& chunkMessage);
    
    /**
     * 验证分片完整性
     * @param chunks 分片列表
     * @return 验证结果
     */
    bool validateChunks(const std::vector<ChunkInfo>& chunks);
    
    /**
     * 重组分片数据
     * @param chunks 已排序的分片列表
     * @return 重组后的完整JSON字符串
     */
    std::string reassembleChunks(const std::vector<ChunkInfo>& chunks);
    
    /**
     * 根据错误自适应调整分片大小
     * @param errorType 错误类型
     * @return 新的分片大小
     */
    size_t adaptChunkSize(const std::string& errorType);
    
    /**
     * 生成唯一会话ID
     * @return 时间戳 + 随机数的会话ID
     */
    static std::string generateSessionId();
    
    /**
     * 计算数据校验和（使用高效哈希算法）
     * @param data 数据
     * @return 校验和
     */
    static std::string calculateChecksum(const std::string& data);
    
    // 配置管理
    const ChunkConfig& getConfig() const { return m_config; }
    void updateConfig(const ChunkConfig& config) { m_config = config; }
    
    // 性能统计
    struct PerformanceStats {
        size_t totalChunks = 0;
        size_t successfulChunks = 0;
        size_t failedChunks = 0;
        std::chrono::milliseconds totalTime{0};
        size_t avgChunkSize = 0;
    };
    
    const PerformanceStats& getStats() const { return m_stats; }
    void resetStats() { m_stats = PerformanceStats{}; }
    
private:
    ChunkConfig m_config;
    size_t m_currentChunkSize;
    PerformanceStats m_stats;
    
    // 内部工具函数
    std::vector<ChunkInfo> splitData(const std::string& data, const std::string& sessionId);
    void updateStats(size_t chunkSize, bool success, std::chrono::milliseconds duration);
};

} // namespace linch_connector