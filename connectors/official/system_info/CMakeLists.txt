cmake_minimum_required(VERSION 3.16)
project(linch-mind-system-info VERSION 1.0.0)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Build type specific settings
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

# 添加shared库目录
add_subdirectory(../../shared shared_build)

# Find required packages (shared库已经处理了大部分依赖)
find_package(nlohmann_json REQUIRED)

# Platform specific settings
if(WIN32)
    set(PLATFORM_LIBS)
    set(PLATFORM_COMPILE_DEFINITIONS WIN32_LEAN_AND_MEAN)
elseif(APPLE)
    # macOS基础框架
    find_library(FOUNDATION_FRAMEWORK Foundation)
    set(PLATFORM_LIBS ${FOUNDATION_FRAMEWORK})
    set(PLATFORM_COMPILE_DEFINITIONS)
else()
    # Linux基础库
    set(PLATFORM_LIBS pthread)
    set(PLATFORM_COMPILE_DEFINITIONS)
endif()

# 系统信息连接器源文件
set(SOURCES
    src/main.cpp
    src/system_info_connector.cpp
)

# Create executable
add_executable(linch-mind-system-info ${SOURCES})

# Include directories
target_include_directories(linch-mind-system-info PRIVATE
    src
    ../../shared/include  # shared库头文件
)

# Link libraries
target_link_libraries(linch-mind-system-info
    linch_connector_shared  # 使用shared库
    nlohmann_json::nlohmann_json
    ${PLATFORM_LIBS}
)

# Compile definitions
target_compile_definitions(linch-mind-system-info PRIVATE ${PLATFORM_COMPILE_DEFINITIONS})

# Compiler flags
if(UNIX)
    target_compile_options(linch-mind-system-info PRIVATE -Wall -Wextra -Wno-unused-parameter)
endif()

# Release build optimizations
if(CMAKE_BUILD_TYPE STREQUAL "Release")
    target_compile_options(linch-mind-system-info PRIVATE
        -O3 -DNDEBUG
        -ffunction-sections -fdata-sections
    )
    
    if(UNIX AND NOT APPLE)
        target_link_options(linch-mind-system-info PRIVATE
            -Wl,--gc-sections
            -Wl,--strip-all
        )
    elseif(APPLE)
        target_link_options(linch-mind-system-info PRIVATE
            -Wl,-dead_strip
        )
    endif()
endif()

# Debug build settings
if(CMAKE_BUILD_TYPE STREQUAL "Debug")
    target_compile_definitions(linch-mind-system-info PRIVATE DEBUG)
    if(UNIX)
        target_compile_options(linch-mind-system-info PRIVATE -g -O0)
    endif()
endif()

# Install target
install(TARGETS linch-mind-system-info
    RUNTIME DESTINATION bin
)

# Print build information
message(STATUS "Build type: ${CMAKE_BUILD_TYPE}")
message(STATUS "Platform libs: ${PLATFORM_LIBS}")
message(STATUS "Using shared library: linch_connector_shared")
message(STATUS "Architecture: System Information Monitoring (v1.0.0)")

# Create build info
configure_file(
    "${PROJECT_SOURCE_DIR}/build_info.hpp.in"
    "${PROJECT_BINARY_DIR}/build_info.hpp"
)