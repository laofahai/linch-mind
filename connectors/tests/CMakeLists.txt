# CMakeLists.txt for Connector Tests
cmake_minimum_required(VERSION 3.16)
project(LinchMindConnectorTests)

# 设置C++标准
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 查找必要的包
find_package(PkgConfig REQUIRED)

# nlohmann/json
find_package(nlohmann_json REQUIRED)

# Google Test
find_package(GTest REQUIRED)

# 设置包含路径
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/../shared/include)

# 添加shared库
add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/../shared shared_build)

# 编译标志
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra -g")

# 测试源文件
set(TEST_SOURCES
    test_unified_client.cpp
    test_daemon_discovery.cpp
    test_config_manager.cpp
    test_connector_status.cpp
    test_ipc_communication.cpp
)

# 创建测试可执行文件
add_executable(connector_tests ${TEST_SOURCES})

# 链接库
target_link_libraries(connector_tests
    PRIVATE
    linch_connector_shared
    nlohmann_json::nlohmann_json
    GTest::GTest
    GTest::Main
    pthread
)

# 平台特定的链接
if(APPLE)
    target_link_libraries(connector_tests PRIVATE "-framework Foundation" "-framework AppKit")
elseif(WIN32)
    target_link_libraries(connector_tests PRIVATE user32 shell32)
elseif(UNIX)
    target_link_libraries(connector_tests PRIVATE X11)
endif()

# 启用测试
enable_testing()

# 添加测试
add_test(NAME ConnectorTests COMMAND connector_tests)

# 设置测试属性
set_tests_properties(ConnectorTests PROPERTIES
    TIMEOUT 300
    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
)

# 创建测试数据目录
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/test_data)

# 复制测试配置文件
configure_file(
    ${CMAKE_CURRENT_SOURCE_DIR}/test_config.json
    ${CMAKE_CURRENT_BINARY_DIR}/test_data/test_config.json
    COPYONLY
)