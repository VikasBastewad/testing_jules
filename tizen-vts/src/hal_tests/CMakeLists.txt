# CMakeLists.txt for HAL Tests

# Find GTest (should be available from the parent CMakeLists.txt)
# Ensure GTest is found and include directories are available
if(NOT GTest_FOUND)
    message(FATAL_ERROR "GTest not found by parent CMake. Check root CMakeLists.txt")
endif()

# Add include directories for GTest
include_directories(${GTEST_INCLUDE_DIRS} ${PROJECT_SOURCE_DIR}/src/hal_tests)

# Define the test executable
add_executable(sample_hal_test sample_hal_test.cpp)

# Link the test executable against GTest and GTest_Main (which includes main())
# Use gtest_main for convenience, or gtest if you provide your own main()
target_link_libraries(sample_hal_test PRIVATE GTest::gtest GTest::gtest_main)

# Add this test to CTest for execution via 'ctest' command
add_test(NAME SampleHALTest COMMAND sample_hal_test)

# You can set properties for tests if needed
# set_tests_properties(SampleHALTest PROPERTIES TIMEOUT 10)

message(STATUS "Added HAL test: sample_hal_test")
