cmake_minimum_required(VERSION 3.16)
project(connector_scripts)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find nlohmann/json
find_package(PkgConfig REQUIRED)
pkg_check_modules(JSON REQUIRED nlohmann_json)

# Version manager executable
add_executable(version_manager version_manager.cpp)
target_link_libraries(version_manager ${JSON_LIBRARIES})
target_include_directories(version_manager PRIVATE ${JSON_INCLUDE_DIRS})

# Registry generator executable
add_executable(registry_generator registry_generator.cpp)
target_link_libraries(registry_generator ${JSON_LIBRARIES})
target_include_directories(registry_generator PRIVATE ${JSON_INCLUDE_DIRS})

# Install to project scripts directory
install(TARGETS version_manager registry_generator DESTINATION ${CMAKE_CURRENT_SOURCE_DIR})