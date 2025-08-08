cmake_minimum_required(VERSION 3.16)
project(linch-mind-filesystem VERSION 0.1.0)

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

# Platform specific settings (simplified for cross-platform build)
if(WIN32)
    set(PLATFORM_LIBS)
    set(PLATFORM_COMPILE_DEFINITIONS WIN32_LEAN_AND_MEAN)
elseif(APPLE)
    set(PLATFORM_LIBS)
    set(PLATFORM_COMPILE_DEFINITIONS)
else()
    set(PLATFORM_LIBS pthread)
    set(PLATFORM_COMPILE_DEFINITIONS)
endif()

# Source files (移除了重复的http_client.cpp和config_manager.cpp)
set(SOURCES
    src/main.cpp
    src/filesystem_monitor.cpp
)

# Create executable
add_executable(linch-mind-filesystem ${SOURCES})

# Include directories
target_include_directories(linch-mind-filesystem PRIVATE
    src
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
    target_compile_options(linch-mind-filesystem PRIVATE -Wall -Wextra)
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

# Install target
install(TARGETS linch-mind-filesystem
    RUNTIME DESTINATION bin
)

# Print build information
message(STATUS "Build type: ${CMAKE_BUILD_TYPE}")
message(STATUS "Platform libs: ${PLATFORM_LIBS}")
message(STATUS "Using shared library: linch_connector_shared")

# Create build info
configure_file(
    "${PROJECT_SOURCE_DIR}/build_info.hpp.in"
    "${PROJECT_BINARY_DIR}/build_info.hpp"
)