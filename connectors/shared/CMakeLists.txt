cmake_minimum_required(VERSION 3.16)
project(linch_connector_shared VERSION 1.0.0)

# 设置C++标准
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 查找依赖库
find_package(PkgConfig REQUIRED)
find_package(nlohmann_json REQUIRED)
# find_package(CURL REQUIRED)  # 已移除 - HTTP客户端不再需要

# Windows特殊处理
if(WIN32)
    find_library(UUID_LIBRARY ole32)
else()
    pkg_check_modules(UUID REQUIRED uuid)
endif()

# 包含目录
include_directories(include)

# 源文件
set(SOURCES
    src/ipc_client.cpp
    src/unified_client.cpp
    src/daemon_discovery.cpp
    src/config_manager.cpp
    src/utils.cpp
    src/connector_status.cpp
    src/base_connector.cpp
)

# 创建静态库
add_library(linch_connector_shared STATIC ${SOURCES})

# 链接库
target_link_libraries(linch_connector_shared
    nlohmann_json::nlohmann_json
    
)

if(WIN32)
    target_link_libraries(linch_connector_shared ${UUID_LIBRARY} ws2_32)
else()
    target_link_libraries(linch_connector_shared ${UUID_LIBRARIES})
    target_include_directories(linch_connector_shared PRIVATE ${UUID_INCLUDE_DIRS})
endif()

# 设置包含目录
target_include_directories(linch_connector_shared
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
)

# 编译选项
if(UNIX)
    target_compile_options(linch_connector_shared PRIVATE -Wall -Wextra)
endif()

# 安装规则
install(TARGETS linch_connector_shared
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
    RUNTIME DESTINATION bin
)

install(DIRECTORY include/
    DESTINATION include
    FILES_MATCHING PATTERN "*.hpp"
)