cmake_minimum_required(VERSION 3.10)

project(TizenVTS CXX C)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Enable testing with CTest
enable_testing()

# --- Google Test Configuration ---
# Attempt to find an existing GTest installation
find_package(GTest QUIET)

if(NOT GTest_FOUND)
    message(STATUS "GTest not found. Fetching from source...")
    include(FetchContent)
    FetchContent_Declare(
        googletest
        GIT_REPOSITORY https://github.com/google/googletest.git
        GIT_TAG main # Or a specific release tag e.g., release-1.12.1
    )
    # For Windows: Prevent overriding the parent project's compiler/linker settings
    set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
    FetchContent_MakeAvailable(googletest)
    message(STATUS "GTest fetched and built.")
else()
    message(STATUS "Found GTest: ${GTEST_LIBRARY}")
endif()
# --- End Google Test Configuration ---

# Output directory for binaries (test executables)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib) # For static libs if any

# Add subdirectories for different test modules
add_subdirectory(src/hal_tests)
add_subdirectory(src/kernel_tests)
# add_subdirectory(src/api_tests) # Uncomment when api_tests are added
# add_subdirectory(src/capability_tests) # Uncomment when capability_tests are added

# Example: How to add a test to CTest (will be done in module CMakeLists.txt)
# add_test(NAME MySampleTest COMMAND MySampleTestExecutable)

# Print some useful paths
message(STATUS "Project Source Directory: ${PROJECT_SOURCE_DIR}")
message(STATUS "Project Binary Directory: ${PROJECT_BINARY_DIR}")
message(STATUS "Test executables will be built in: ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}")
