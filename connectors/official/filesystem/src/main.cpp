#include <iostream>
#include <memory>
#include <thread>
#include <chrono>

// 新的统一架构
#include "filesystem_connector.hpp"

using namespace linch_connector;

int main(int argc, char* argv[]) {
    std::cout << "🚀 Starting Linch Mind Filesystem Connector (Unified Architecture)" << std::endl;
    
    // 创建文件系统连接器
    auto connector = std::make_unique<FilesystemConnector>();
    
    // 初始化连接器
    if (!connector->initialize()) {
        std::cerr << "❌ 连接器初始化失败" << std::endl;
        return 1;
    }
    
    // 启动连接器
    if (!connector->start()) {
        std::cerr << "❌ 连接器启动失败" << std::endl;
        return 1;
    }
    
    std::cout << "✅ 文件系统连接器运行中，按 Ctrl+C 停止..." << std::endl;
    
    // 主循环 - 等待停止信号
    while (!BaseConnector::s_shouldStop.load()) {
        std::this_thread::sleep_for(std::chrono::seconds(1));
        
        // 检查连接器状态
        if (!connector->isRunning()) {
            std::cerr << "⚠️ 连接器意外停止" << std::endl;
            break;
        }
    }
    
    // 停止连接器
    std::cout << "🛑 正在停止文件系统连接器..." << std::endl;
    connector->stop();
    
    // 显示最终统计
    auto stats = connector->getStatistics();
    std::cout << "📊 最终统计:" << std::endl;
    std::cout << "   处理事件: " << stats.eventsProcessed << " 个" << std::endl;
    std::cout << "   过滤事件: " << stats.eventsFiltered << " 个" << std::endl;
    std::cout << "   监控路径: " << stats.pathsMonitored << " 个" << std::endl;
    
    std::cout << "✅ 文件系统连接器已安全停止" << std::endl;
    return 0;
}