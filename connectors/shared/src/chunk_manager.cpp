#include "linch_connector/chunk_manager.hpp"
#include "linch_connector/utils.hpp"
#include <random>
#include <sstream>
#include <iomanip>
#include <algorithm>
#include <functional>

namespace linch_connector {

ChunkManager::ChunkManager(const ChunkConfig& config) 
    : m_config(config), m_currentChunkSize(config.maxChunkSize) {
}

std::vector<ChunkManager::ChunkInfo> ChunkManager::chunkifyJson(
    const nlohmann::json& jsonData, const std::string& sessionId) {
    
    auto start = std::chrono::steady_clock::now();
    
    try {
        // 使用安全的JSON序列化
        std::string jsonString = utils::safeJsonDump(jsonData);
        
        // 使用实际的会话ID
        std::string actualSessionId = sessionId.empty() ? generateSessionId() : sessionId;
        
        // 分片数据
        auto chunks = splitData(jsonString, actualSessionId);
        
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::steady_clock::now() - start);
        updateStats(m_currentChunkSize, true, duration);
        
        return chunks;
        
    } catch (const std::exception& e) {
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::steady_clock::now() - start);
        updateStats(m_currentChunkSize, false, duration);
        
        // 返回空列表，调用者需要处理这种情况
        return {};
    }
}

std::vector<ChunkManager::ChunkInfo> ChunkManager::splitData(
    const std::string& data, const std::string& sessionId) {
    
    std::vector<ChunkInfo> chunks;
    
    if (data.empty()) {
        return chunks;
    }
    
    // 计算分片数量
    size_t totalChunks = (data.size() + m_currentChunkSize - 1) / m_currentChunkSize;
    std::string checksum = calculateChecksum(data);
    
    // 创建分片
    for (size_t i = 0; i < totalChunks; ++i) {
        ChunkInfo chunk;
        chunk.sessionId = sessionId;
        chunk.totalChunks = totalChunks;
        chunk.chunkIndex = i;
        chunk.originalSize = data.size();
        chunk.checksum = checksum;
        
        // 计算当前分片的数据范围
        size_t startPos = i * m_currentChunkSize;
        size_t endPos = std::min(startPos + m_currentChunkSize, data.size());
        
        chunk.data = data.substr(startPos, endPos - startPos);
        chunks.push_back(std::move(chunk));
    }
    
    return chunks;
}

nlohmann::json ChunkManager::createChunkMessage(const ChunkInfo& chunk) {
    nlohmann::json message = {
        {"type", "chunk_data"},
        {"session_id", chunk.sessionId},
        {"chunk_index", chunk.chunkIndex},
        {"total_chunks", chunk.totalChunks},
        {"original_size", chunk.originalSize},
        {"checksum", chunk.checksum},
        {"data", chunk.data},
        {"timestamp", utils::getCurrentTimestamp()}
    };
    
    return message;
}

ChunkManager::ChunkInfo ChunkManager::parseChunkMessage(const nlohmann::json& chunkMessage) {
    ChunkInfo chunk;
    
    try {
        chunk.sessionId = chunkMessage.value("session_id", "");
        chunk.chunkIndex = chunkMessage.value("chunk_index", 0);
        chunk.totalChunks = chunkMessage.value("total_chunks", 0);
        chunk.originalSize = chunkMessage.value("original_size", 0);
        chunk.checksum = chunkMessage.value("checksum", "");
        chunk.data = chunkMessage.value("data", "");
        
        return chunk;
        
    } catch (const std::exception& e) {
        // 返回空的chunk表示解析失败
        return ChunkInfo{};
    }
}

bool ChunkManager::validateChunks(const std::vector<ChunkInfo>& chunks) {
    if (chunks.empty()) {
        return false;
    }
    
    // 检查会话ID一致性
    std::string sessionId = chunks[0].sessionId;
    size_t totalChunks = chunks[0].totalChunks;
    size_t originalSize = chunks[0].originalSize;
    std::string checksum = chunks[0].checksum;
    
    // 验证数量是否正确
    if (chunks.size() != totalChunks) {
        return false;
    }
    
    // 验证每个分片的元数据
    for (size_t i = 0; i < chunks.size(); ++i) {
        const auto& chunk = chunks[i];
        
        if (chunk.sessionId != sessionId ||
            chunk.totalChunks != totalChunks ||
            chunk.originalSize != originalSize ||
            chunk.checksum != checksum ||
            chunk.chunkIndex != i) {
            return false;
        }
    }
    
    return true;
}

std::string ChunkManager::reassembleChunks(const std::vector<ChunkInfo>& chunks) {
    if (!validateChunks(chunks)) {
        return "";
    }
    
    // 创建排序副本（按chunkIndex排序）
    auto sortedChunks = chunks;
    std::sort(sortedChunks.begin(), sortedChunks.end(),
              [](const ChunkInfo& a, const ChunkInfo& b) {
                  return a.chunkIndex < b.chunkIndex;
              });
    
    // 重组数据
    std::string result;
    result.reserve(sortedChunks[0].originalSize);
    
    for (const auto& chunk : sortedChunks) {
        result += chunk.data;
    }
    
    // 验证校验和
    if (calculateChecksum(result) != sortedChunks[0].checksum) {
        return "";  // 校验失败
    }
    
    return result;
}

size_t ChunkManager::adaptChunkSize(const std::string& errorType) {
    // 根据错误类型调整分片大小
    if (errorType.find("MEMORY") != std::string::npos ||
        errorType.find("SIZE") != std::string::npos ||
        errorType.find("TIMEOUT") != std::string::npos) {
        
        // 减小分片大小
        m_currentChunkSize = static_cast<size_t>(
            m_currentChunkSize * m_config.adaptiveThreshold);
        
        // 确保不小于最小值
        if (m_currentChunkSize < m_config.minChunkSize) {
            m_currentChunkSize = m_config.minChunkSize;
        }
    }
    
    return m_currentChunkSize;
}

std::string ChunkManager::generateSessionId() {
    // 使用时间戳 + 随机数生成唯一ID
    auto now = std::chrono::system_clock::now();
    auto timestamp = std::chrono::duration_cast<std::chrono::milliseconds>(
        now.time_since_epoch()).count();
    
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<> dis(1000, 9999);
    
    std::stringstream ss;
    ss << "chunk_" << timestamp << "_" << dis(gen);
    return ss.str();
}

std::string ChunkManager::calculateChecksum(const std::string& data) {
    // 使用简单但高效的哈希算法
    std::hash<std::string> hasher;
    size_t hashValue = hasher(data);
    
    std::stringstream ss;
    ss << std::hex << hashValue;
    return ss.str();
}

void ChunkManager::updateStats(size_t chunkSize, bool success, 
                               std::chrono::milliseconds duration) {
    m_stats.totalChunks++;
    if (success) {
        m_stats.successfulChunks++;
    } else {
        m_stats.failedChunks++;
    }
    
    m_stats.totalTime += duration;
    
    // 计算平均分片大小
    m_stats.avgChunkSize = (m_stats.avgChunkSize * (m_stats.totalChunks - 1) + chunkSize) 
                          / m_stats.totalChunks;
}

} // namespace linch_connector