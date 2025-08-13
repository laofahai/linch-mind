cmake_minimum_required(VERSION 3.16)
project(linch-mind-clipboard VERSION 0.1.0)

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

# Platform specific settings for clipboard monitoring
if(WIN32)
    set(PLATFORM_SOURCES src/platform/windows_clipboard.cpp)
    set(PLATFORM_LIBS user32 kernel32)
    set(PLATFORM_COMPILE_DEFINITIONS WIN32_LEAN_AND_MEAN)
elseif(APPLE)
    set(PLATFORM_SOURCES src/platform/macos_clipboard.mm)
    set(PLATFORM_LIBS "-framework Cocoa")
    set(PLATFORM_COMPILE_DEFINITIONS)
else()
    set(PLATFORM_SOURCES src/platform/linux_clipboard.cpp)
    find_package(X11 REQUIRED)
    set(PLATFORM_LIBS ${X11_LIBRARIES})
    set(PLATFORM_COMPILE_DEFINITIONS)
endif()

# Set output directories based on build type BEFORE creating executable
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/bin)
if(CMAKE_BUILD_TYPE STREQUAL "Debug")
    set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/bin/debug)
else()
    set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/bin/release)
endif()

# Source files (使用新的统一架构)
set(SOURCES
    src/main.cpp
    src/clipboard_monitor.cpp
    src/clipboard_monitor_adapter.cpp
    src/clipboard_connector.cpp
    ${PLATFORM_SOURCES}
)

# Create executable
add_executable(linch-mind-clipboard ${SOURCES})

# Include directories
target_include_directories(linch-mind-clipboard PRIVATE
    src
    ../../shared/include  # shared库头文件
)

# Link libraries
target_link_libraries(linch-mind-clipboard
    linch_connector_shared  # 使用shared库
    nlohmann_json::nlohmann_json
    ${PLATFORM_LIBS}
)

# Compile definitions
target_compile_definitions(linch-mind-clipboard PRIVATE ${PLATFORM_COMPILE_DEFINITIONS})

# Compiler flags
if(UNIX)
    target_compile_options(linch-mind-clipboard PRIVATE -Wall -Wextra)
endif()

# Release build optimizations
if(CMAKE_BUILD_TYPE STREQUAL "Release")
    # Maximum optimization
    target_compile_options(linch-mind-clipboard PRIVATE
        -O3 -DNDEBUG
        -ffunction-sections -fdata-sections
    )
    
    # Link-time optimization and dead code elimination
    if(UNIX AND NOT APPLE)
        target_link_options(linch-mind-clipboard PRIVATE
            -Wl,--gc-sections
            -Wl,--strip-all
        )
    elseif(APPLE)
        target_link_options(linch-mind-clipboard PRIVATE
            -Wl,-dead_strip
        )
    endif()
endif()

# Install target
install(TARGETS linch-mind-clipboard
    RUNTIME DESTINATION bin
)

# Print build information
message(STATUS "Build type: ${CMAKE_BUILD_TYPE}")
message(STATUS "Platform sources: ${PLATFORM_SOURCES}")
message(STATUS "Platform libs: ${PLATFORM_LIBS}")
message(STATUS "Using shared library: linch_connector_shared")

# Create build info
configure_file(
    "${PROJECT_SOURCE_DIR}/build_info.hpp.in"
    "${PROJECT_BINARY_DIR}/build_info.hpp"
)