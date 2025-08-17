#include "user_context_connector.hpp"
#include <iostream>
#include <memory>
#include <thread>
#include <chrono>
#include <string>

using namespace linch_connector;

/**
 * 用户情境感知连接器入口点
 * 负责感知用户当前活动情境、设备状态、智能负载等用户相关数据
 */
int main(int argc, char* argv[]) {
    // 处理命令行参数
    if (argc > 1) {
        std::string arg = argv[1];
        
        // 版本检查 - daemon健康检查使用
        if (arg == "--version" || arg == "-v") {
            std::cout << "linch-mind-user-context-connector 1.0.0" << std::endl;
            return 0;
        }
        
        // 帮助信息
        if (arg == "--help" || arg == "-h") {
            std::cout << "Linch Mind User Context Connector" << std::endl;
            std::cout << "Usage: " << argv[0] << " [options]" << std::endl;
            std::cout << "Options:" << std::endl;
            std::cout << "  --version, -v    显示版本信息" << std::endl;
            std::cout << "  --help, -h       显示帮助信息" << std::endl;
            return 0;
        }
        
        // 未知参数警告但继续运行
        if (arg.size() > 0 && arg[0] == '-') {
            std::cerr << "⚠️ 未知参数: " << arg << std::endl;
            std::cerr << "使用 --help 查看可用选项" << std::endl;
        }
    }
    
    std::cout << "🧠 启动 Linch Mind 用户情境感知连接器" << std::endl;
    
    try {
        // 创建用户情境感知连接器实例
        auto connector = std::make_unique<UserContextConnector>();
        
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
        
        std::cout << "✅ 用户情境感知连接器运行中，按 Ctrl+C 停止..." << std::endl;
        
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
        std::cout << "🛑 正在停止用户情境感知连接器..." << std::endl;
        connector->stop();
        
        // 显示最终统计
        auto stats = connector->getStatistics();
        std::cout << "📊 最终统计:" << std::endl;
        std::cout << "   处理事件: " << stats.eventsProcessed << " 个" << std::endl;
        std::cout << "   过滤事件: " << stats.eventsFiltered << " 个" << std::endl;
        
        std::cout << "✅ 用户情境感知连接器已安全停止" << std::endl;
        return 0;
    }
    catch (const std::exception& e) {
        std::cerr << "❌ 用户情境感知连接器运行失败: " << e.what() << std::endl;
        return 1;
    }
}