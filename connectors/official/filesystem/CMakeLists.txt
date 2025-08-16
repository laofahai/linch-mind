cmake_minimum_required(VERSION 3.16)
project(linch-mind-filesystem VERSION 0.2.0)

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
    # macOS需要CoreServices框架用于FSEvents，Foundation用于快速扫描
    find_library(CORE_SERVICES_FRAMEWORK CoreServices)
    find_library(FOUNDATION_FRAMEWORK Foundation)
    set(PLATFORM_LIBS ${CORE_SERVICES_FRAMEWORK} ${FOUNDATION_FRAMEWORK})
    set(PLATFORM_COMPILE_DEFINITIONS)
else()
    # Linux需要pthread
    set(PLATFORM_LIBS pthread)
    set(PLATFORM_COMPILE_DEFINITIONS)
endif()

# Source files - 使用零扫描索引架构 + 进度管理
set(SOURCES
    src/main.cpp
    src/native_monitor.hpp
    src/monitor_factory.cpp
    src/filesystem_monitor_adapter.cpp
    src/filesystem_connector.cpp
    src/file_index_provider.cpp
    src/zero_scan/zero_scan_factory.cpp
    src/progress/scan_progress_manager.cpp
)

# 平台特定源文件
if(APPLE)
    list(APPEND SOURCES
        src/platform/macos_fsevents_monitor.cpp
        src/platform/macos_file_index_provider.cpp
        src/zero_scan/platform/macos/macos_zero_scan_provider.mm
    )
elseif(UNIX)
    list(APPEND SOURCES
        src/platform/linux_inotify_monitor.cpp
        src/platform/linux_file_index_provider.cpp
    )
elseif(WIN32)
    list(APPEND SOURCES
        src/platform/windows_rdcw_monitor.cpp
        src/platform/windows_file_index_provider.cpp
    )
endif()

# Create executable
add_executable(linch-mind-filesystem ${SOURCES})

# Include directories
target_include_directories(linch-mind-filesystem PRIVATE
    src
    src/platform
    src/zero_scan
    src/progress
    ../../shared/include  # shared库头文件
)

# Link libraries
target_link_libraries(linch-mind-filesystem
    linch_connector_shared  # 使用shared库
    nlohmann_json::nlohmann_json
    ${PLATFORM_LIBS}
)

# Compile definitions
target_compile_definitions(linch-mind-filesystem PRIVATE ${PLATFORM_COMPILE_DEFINITIONS})

# Compiler flags
if(UNIX)
    target_compile_options(linch-mind-filesystem PRIVATE -Wall -Wextra -Wno-unused-parameter)
endif()

# Release build optimizations
if(CMAKE_BUILD_TYPE STREQUAL "Release")
    # Maximum optimization
    target_compile_options(linch-mind-filesystem PRIVATE
        -O3 -DNDEBUG
        -ffunction-sections -fdata-sections
    )
    
    # Link-time optimization and dead code elimination
    if(UNIX AND NOT APPLE)
        target_link_options(linch-mind-filesystem PRIVATE
            -Wl,--gc-sections
            -Wl,--strip-all
        )
    elseif(APPLE)
        target_link_options(linch-mind-filesystem PRIVATE
            -Wl,-dead_strip
        )
    endif()
endif()

# Debug build settings
if(CMAKE_BUILD_TYPE STREQUAL "Debug")
    target_compile_definitions(linch-mind-filesystem PRIVATE DEBUG)
    if(UNIX)
        target_compile_options(linch-mind-filesystem PRIVATE -g -O0)
    endif()
endif()

# Install target
install(TARGETS linch-mind-filesystem
    RUNTIME DESTINATION bin
)

# Print build information
message(STATUS "Build type: ${CMAKE_BUILD_TYPE}")
message(STATUS "Platform libs: ${PLATFORM_LIBS}")
message(STATUS "Using shared library: linch_connector_shared")
message(STATUS "Architecture: Native Event-Driven (v0.2.0)")

# Create build info
configure_file(
    "${PROJECT_SOURCE_DIR}/build_info.hpp.in"
    "${PROJECT_BINARY_DIR}/build_info.hpp"
)