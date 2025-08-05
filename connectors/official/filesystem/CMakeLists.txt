cmake_minimum_required(VERSION 3.16)
project(filesystem-connector VERSION 0.1.0)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Build type specific settings
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

# Find required packages
find_package(PkgConfig REQUIRED)
pkg_check_modules(CURL REQUIRED libcurl)

# Find nlohmann_json
find_package(nlohmann_json QUIET)
if(NOT nlohmann_json_FOUND)
    # Try to find it with pkgconfig
    pkg_check_modules(NLOHMANN_JSON nlohmann_json)
    if(NOT NLOHMANN_JSON_FOUND)
        message(FATAL_ERROR "nlohmann_json not found. Install with: brew install nlohmann-json (macOS) or apt-get install nlohmann-json3-dev (Ubuntu)")
    endif()
endif()

# Find uuid library
if(APPLE)
    # macOS has uuid in System framework
    find_library(UUID_LIBRARY System)
    set(UUID_LIBRARIES ${UUID_LIBRARY})
elseif(UNIX)
    # Linux needs uuid library
    find_library(UUID_LIBRARY uuid)
    if(NOT UUID_LIBRARY)
        message(FATAL_ERROR "uuid library not found. Install with: apt-get install uuid-dev")
    endif()
    set(UUID_LIBRARIES ${UUID_LIBRARY})
endif()

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

# Source files
set(SOURCES
    src/main.cpp
    src/filesystem_monitor.cpp
    src/http_client.cpp
    src/config_manager.cpp
)

# Create executable
add_executable(filesystem-connector ${SOURCES})

# Include directories
target_include_directories(filesystem-connector PRIVATE
    src
    ${CURL_INCLUDE_DIRS}
)

# Link libraries
target_link_libraries(filesystem-connector
    ${CURL_LIBRARIES}
    ${PLATFORM_LIBS}
    ${UUID_LIBRARIES}
)

# Add nlohmann_json
if(nlohmann_json_FOUND)
    target_link_libraries(filesystem-connector nlohmann_json::nlohmann_json)
else()
    target_include_directories(filesystem-connector PRIVATE ${NLOHMANN_JSON_INCLUDE_DIRS})
endif()

# Compile definitions
target_compile_definitions(filesystem-connector PRIVATE ${PLATFORM_COMPILE_DEFINITIONS})

# Compiler flags
target_compile_options(filesystem-connector PRIVATE
    ${CURL_CFLAGS_OTHER}
    -Wall -Wextra
)

# Release build optimizations
if(CMAKE_BUILD_TYPE STREQUAL "Release")
    # Maximum optimization
    target_compile_options(filesystem-connector PRIVATE
        -O3 -DNDEBUG -flto
        -ffunction-sections -fdata-sections
    )
    
    # Link-time optimization and dead code elimination
    if(UNIX AND NOT APPLE)
        target_link_options(filesystem-connector PRIVATE
            -flto
            -Wl,--gc-sections
            -Wl,--strip-all
        )
    elseif(APPLE)
        target_link_options(filesystem-connector PRIVATE
            -flto
            -Wl,-dead_strip
        )
    endif()
    
    # Static linking for smaller, self-contained binary
    if(UNIX AND NOT APPLE)
        target_link_options(filesystem-connector PRIVATE
            -static-libgcc -static-libstdc++
        )
    endif()
endif()

# Install target
install(TARGETS filesystem-connector
    RUNTIME DESTINATION bin
)

# Print build information
message(STATUS "Build type: ${CMAKE_BUILD_TYPE}")
message(STATUS "Platform sources: ${PLATFORM_SOURCES}")
message(STATUS "Platform libs: ${PLATFORM_LIBS}")
message(STATUS "CURL found: ${CURL_FOUND}")
message(STATUS "nlohmann_json found: ${nlohmann_json_FOUND}")

# Create build info
configure_file(
    "${PROJECT_SOURCE_DIR}/build_info.hpp.in"
    "${PROJECT_BINARY_DIR}/build_info.hpp"
)