cmake_minimum_required(VERSION 3.16)
project(linch-mind-user-context VERSION 1.0.0)

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
    # macOS需要Objective-C++框架
    find_library(FOUNDATION_FRAMEWORK Foundation)
    find_library(APPKIT_FRAMEWORK AppKit)
    set(PLATFORM_LIBS ${FOUNDATION_FRAMEWORK} ${APPKIT_FRAMEWORK})
    set(PLATFORM_COMPILE_DEFINITIONS)
    enable_language(OBJCXX)
else()
    # Linux基础库
    set(PLATFORM_LIBS pthread)
    set(PLATFORM_COMPILE_DEFINITIONS)
endif()

# 用户情境感知连接器源文件
set(SOURCES
    src/main.cpp
    src/user_context_connector.mm
)

# Create executable
add_executable(linch-mind-user-context ${SOURCES})

# Include directories
target_include_directories(linch-mind-user-context PRIVATE
    src
    ../../shared/include  # shared库头文件
)

# Link libraries
target_link_libraries(linch-mind-user-context
    linch_connector_shared  # 使用shared库
    nlohmann_json::nlohmann_json
    ${PLATFORM_LIBS}
)

# Compile definitions
target_compile_definitions(linch-mind-user-context PRIVATE ${PLATFORM_COMPILE_DEFINITIONS})

# Compiler flags
if(UNIX)
    target_compile_options(linch-mind-user-context PRIVATE -Wall -Wextra -Wno-unused-parameter)
endif()

# Release build optimizations
if(CMAKE_BUILD_TYPE STREQUAL "Release")
    target_compile_options(linch-mind-user-context PRIVATE
        -O3 -DNDEBUG
        -ffunction-sections -fdata-sections
    )
    
    if(UNIX AND NOT APPLE)
        target_link_options(linch-mind-user-context PRIVATE
            -Wl,--gc-sections
            -Wl,--strip-all
        )
    elseif(APPLE)
        target_link_options(linch-mind-user-context PRIVATE
            -Wl,-dead_strip
        )
    endif()
endif()

# Debug build settings
if(CMAKE_BUILD_TYPE STREQUAL "Debug")
    target_compile_definitions(linch-mind-user-context PRIVATE DEBUG)
    if(UNIX)
        target_compile_options(linch-mind-user-context PRIVATE -g -O0)
    endif()
endif()

# Install target
install(TARGETS linch-mind-user-context
    RUNTIME DESTINATION bin
)

# Print build information
message(STATUS "Build type: ${CMAKE_BUILD_TYPE}")
message(STATUS "Platform libs: ${PLATFORM_LIBS}")
message(STATUS "Using shared library: linch_connector_shared")
message(STATUS "Architecture: User Context Awareness (v1.0.0)")

# Create build info
configure_file(
    "${PROJECT_SOURCE_DIR}/build_info.hpp.in"
    "${PROJECT_BINARY_DIR}/build_info.hpp"
)