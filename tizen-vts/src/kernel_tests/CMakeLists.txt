# CMakeLists.txt for Kernel Tests

# Find GTest (should be available from the parent CMakeLists.txt)
if(NOT GTest_FOUND)
    message(FATAL_ERROR "GTest not found by parent CMake. Check root CMakeLists.txt")
endif()

# Add include directories for GTest
include_directories(${GTEST_INCLUDE_DIRS})

# Define the test executable
add_executable(sample_kernel_test sample_kernel_test.cpp)

# Link the test executable against GTest and GTest_Main
target_link_libraries(sample_kernel_test PRIVATE GTest::gtest GTest::gtest_main)

# Add this test to CTest for execution via 'ctest' command
add_test(NAME SampleKernelTest COMMAND sample_kernel_test)

message(STATUS "Added Kernel test: sample_kernel_test")
