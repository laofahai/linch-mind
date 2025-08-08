#include <gtest/gtest.h>
#include <linch_connector/unified_client.hpp>
#include <linch_connector/daemon_discovery.hpp>
#include <nlohmann/json.hpp>
#include <thread>
#include <chrono>

using json = nlohmann::json;
using namespace linch_connector;

class UnifiedClientTest : public ::testing::Test {
protected:
    void SetUp() override {
        // 设置测试环境
        client = std::make_unique<UnifiedClient>();
    }

    void TearDown() override {
        // 清理测试环境
        if (client && client->isConnected()) {
            client->disconnect();
        }
    }

    std::unique_ptr<UnifiedClient> client;
};

// 测试连接器发现功能
TEST_F(UnifiedClientTest, TestDaemonDiscovery) {
    DaemonDiscovery discovery;
    auto daemon_info = discovery.discoverDaemon();
    
    // 如果没有daemon运行，这是正常的
    // 测试主要验证发现机制不会崩溃
    EXPECT_NO_THROW({
        if (daemon_info.has_value()) {
            EXPECT_FALSE(daemon_info->socket_path.empty());
            EXPECT_GT(daemon_info->pid, 0);
        }
    });
}

// 测试客户端创建和初始化
TEST_F(UnifiedClientTest, TestClientCreation) {
    EXPECT_NE(client, nullptr);
    EXPECT_FALSE(client->isConnected());
}

// 测试连接功能（模拟）
TEST_F(UnifiedClientTest, TestConnectionAttempt) {
    // 创建一个假的daemon信息用于测试
    DaemonInfo fake_daemon;
    fake_daemon.socket_type = "unix";
    fake_daemon.socket_path = "/tmp/test_linch_mind.sock";
    fake_daemon.pid = 12345;
    
    // 尝试连接（预期会失败，因为没有真实的daemon）
    bool connected = client->connect(fake_daemon);
    EXPECT_FALSE(connected); // 预期失败，因为没有daemon
}

// 测试消息格式化
TEST_F(UnifiedClientTest, TestMessageFormatting) {
    json test_data = {
        {"action", "test"},
        {"timestamp", 1234567890},
        {"data", {
            {"key1", "value1"},
            {"key2", 42}
        }}
    };
    
    std::string formatted = test_data.dump();
    EXPECT_FALSE(formatted.empty());
    EXPECT_TRUE(formatted.find("test") != std::string::npos);
}

// 测试心跳功能
TEST_F(UnifiedClientTest, TestHeartbeatMessage) {
    json heartbeat = {
        {"type", "heartbeat"},
        {"timestamp", std::chrono::system_clock::now().time_since_epoch().count()},
        {"client_id", "test_client"}
    };
    
    EXPECT_EQ(heartbeat["type"], "heartbeat");
    EXPECT_TRUE(heartbeat.contains("timestamp"));
    EXPECT_TRUE(heartbeat.contains("client_id"));
}

// 测试配置数据处理
TEST_F(UnifiedClientTest, TestConfigDataHandling) {
    json config = {
        {"enabled", true},
        {"interval", 5000},
        {"targets", json::array({"target1", "target2"})},
        {"settings", {
            {"debug", false},
            {"log_level", "info"}
        }}
    };
    
    // 验证配置结构
    EXPECT_TRUE(config["enabled"].is_boolean());
    EXPECT_TRUE(config["interval"].is_number());
    EXPECT_TRUE(config["targets"].is_array());
    EXPECT_EQ(config["targets"].size(), 2);
    EXPECT_TRUE(config["settings"].is_object());
}

// 测试错误处理
TEST_F(UnifiedClientTest, TestErrorHandling) {
    // 测试无效的socket路径
    DaemonInfo invalid_daemon;
    invalid_daemon.socket_type = "invalid";
    invalid_daemon.socket_path = "";
    invalid_daemon.pid = -1;
    
    bool result = client->connect(invalid_daemon);
    EXPECT_FALSE(result);
    EXPECT_FALSE(client->isConnected());
}

// 测试数据验证
TEST_F(UnifiedClientTest, TestDataValidation) {
    // 测试有效的JSON数据
    std::string valid_json = R"({"status": "ok", "message": "test"})";
    json parsed;
    EXPECT_NO_THROW(parsed = json::parse(valid_json));
    
    // 测试无效的JSON数据
    std::string invalid_json = R"({"status": "ok", "message":})";
    EXPECT_THROW(json::parse(invalid_json), json::exception);
}

// 测试连接状态管理
TEST_F(UnifiedClientTest, TestConnectionState) {
    // 初始状态应该是未连接
    EXPECT_FALSE(client->isConnected());
    
    // 断开一个未连接的客户端应该是安全的
    EXPECT_NO_THROW(client->disconnect());
    
    // 状态应该保持未连接
    EXPECT_FALSE(client->isConnected());
}

// 测试线程安全性（基本测试）
TEST_F(UnifiedClientTest, TestThreadSafety) {
    bool test_completed = false;
    
    std::thread test_thread([&]() {
        // 在另一个线程中操作客户端
        auto thread_client = std::make_unique<UnifiedClient>();
        EXPECT_FALSE(thread_client->isConnected());
        test_completed = true;
    });
    
    test_thread.join();
    EXPECT_TRUE(test_completed);
}

// 性能基准测试
TEST_F(UnifiedClientTest, TestPerformanceBenchmark) {
    const int iterations = 1000;
    auto start = std::chrono::high_resolution_clock::now();
    
    // 执行1000次JSON解析操作
    for (int i = 0; i < iterations; ++i) {
        json test_data = {
            {"id", i},
            {"timestamp", std::chrono::system_clock::now().time_since_epoch().count()},
            {"data", "test_data_" + std::to_string(i)}
        };
        std::string serialized = test_data.dump();
        json parsed = json::parse(serialized);
    }
    
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
    
    // 验证性能（每次操作应该在合理时间内完成）
    double avg_time_per_op = static_cast<double>(duration.count()) / iterations;
    EXPECT_LT(avg_time_per_op, 1000.0); // 每次操作应该少于1毫秒
    
    std::cout << "Average time per JSON operation: " << avg_time_per_op << " microseconds" << std::endl;
}