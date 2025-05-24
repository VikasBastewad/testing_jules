# Writing Tests for Tizen VTS

This guide provides instructions and best practices for developers looking to write new test cases for the Tizen Vendor Test Suite (VTS).

## Prerequisites

Before you start writing tests, ensure you have:

*   A solid understanding of C++.
*   Basic familiarity with the Google Test (GTest) framework. (See [GTest Primer](https://google.github.io/googletest/primer.html))
*   Knowledge of the specific Tizen component or interface you intend to test (e.g., a particular HAL, kernel subsystem, or native API).
*   A working Tizen VTS host setup (see `SETUP.md`).

## Test Structure and Environment

Tizen VTS tests are organized into modules, typically based on the component they target (e.g., `hal_tests`, `kernel_tests`). Each test module compiles into one or more test executables.

## Setting up a New Test Module

Let's say you want to create a new set of tests called `my_feature_tests`.

1.  **Create Directory Structure:**
    Create a new directory for your module within the `src/` directory:
    ```bash
    mkdir src/my_feature_tests
    ```

2.  **Create `CMakeLists.txt` for the Module:**
    Add a `CMakeLists.txt` file inside `src/my_feature_tests/`:
    ```cmake
    # src/my_feature_tests/CMakeLists.txt

    # Find GTest (should be available from the parent CMakeLists.txt)
    if(NOT GTest_FOUND)
        message(FATAL_ERROR "GTest not found by parent CMake. Check root CMakeLists.txt")
    endif()

    # Add include directories for GTest and any specific headers for your tests
    include_directories(
        ${GTEST_INCLUDE_DIRS}
        ${PROJECT_SOURCE_DIR}/src/my_feature_tests # For local headers
        # Add other necessary include paths here
    )

    # Define your test executable(s)
    # List all .cpp files that are part of this test executable
    add_executable(my_feature_test_executable
        my_feature_test.cpp
        another_test_file.cpp  # If you have multiple source files
    )

    # Link the test executable against GTest and GTest_Main
    target_link_libraries(my_feature_test_executable PRIVATE GTest::gtest GTest::gtest_main)

    # Add this test to CTest for execution via 'ctest' command
    # The first argument to add_test is the CTest name, the second is the command (executable name)
    add_test(NAME MyFeatureTest COMMAND my_feature_test_executable)

    message(STATUS "Added My Feature test: my_feature_test_executable")
    ```

3.  **Add to Root `CMakeLists.txt`:**
    Open the main `tizen-vts/CMakeLists.txt` file and add your new module subdirectory:
    ```cmake
    # ... other add_subdirectory lines ...
    add_subdirectory(src/my_feature_tests)
    ```

## Writing Test Code with GTest

### GTest Basics Recap

*   **Test Fixtures:** Use classes that inherit from `::testing::Test` to group related tests and share setup/teardown code.
    ```cpp
    #include "gtest/gtest.h"
    // Include headers for the component you are testing

    class MyFeatureTestFixture : public ::testing::Test {
    protected:
        // Runs before each test in this fixture
        void SetUp() override {
            // Initialize resources, set up mock objects, etc.
        }

        // Runs after each test in this fixture
        void TearDown() override {
            // Clean up resources
        }

        // Shared variables or helper methods can be defined here
        int shared_variable;
    };
    ```
*   **Test Cases:** Use `TEST_F` for tests using a fixture, or `TEST` for simple tests.
    ```cpp
    TEST_F(MyFeatureTestFixture, TestSomething) {
        // Test logic using GTest assertions
        shared_variable = 10;
        EXPECT_EQ(shared_variable, 10);
        ASSERT_TRUE(some_function_to_test());
    }

    TEST(MySimpleTest, HandlesPositiveInput) {
        EXPECT_GT(another_function(10), 0);
    }
    ```
*   **Assertions:**
    *   `EXPECT_*`: Non-fatal assertions. The test continues if an `EXPECT_*` fails.
    *   `ASSERT_*`: Fatal assertions. The current function (and thus the test) terminates if an `ASSERT_*` fails.
    *   Common assertions: `EXPECT_TRUE(condition)`, `EXPECT_FALSE(condition)`, `EXPECT_EQ(expected, actual)`, `EXPECT_NE`, `EXPECT_LT`, `EXPECT_LE`, `EXPECT_GT`, `EXPECT_GE`, `EXPECT_STREQ(str1, str2)`, `EXPECT_THROW`, `FAIL()`, `SUCCEED()`.

### Interacting with Tizen Interfaces

*   **HALs:** Your test will likely include header files for the specific HAL and call its functions. You might need to use mock objects or specific test HAL implementations if direct hardware interaction is complex or risky for automated tests.
*   **Kernel Interfaces:** Tests may involve reading/writing to `/proc` or `/sys` files using standard C++ file I/O (`<fstream>`). Ensure your tests handle permissions issues gracefully.
*   **Native APIs:** Link against the necessary Tizen libraries and call the native APIs as per their documentation.

### Best Practices

*   **Clear Naming:** Test suite names (fixtures) and test case names should be descriptive.
*   **Focused Tests:** Each test case should verify a specific aspect of the component. Avoid overly long or complex test cases.
*   **Idempotence:** Tests should be runnable multiple times with the same outcome, ideally without leaving side effects that affect other tests. Use `SetUp` and `TearDown` to manage state.
*   **Check Preconditions:** If a test relies on certain device features or states, check these explicitly at the beginning of the test or fixture setup. GTest's `GTEST_SKIP()` can be useful.
*   **Error Messages:** Provide meaningful messages in your assertions: `EXPECT_EQ(expected, actual) << "Descriptive message if this fails";`

## Building and Running Tests

1.  **Build All Tests:**
    Use the provided script:
    ```bash
    ./scripts/build_tests.sh
    ```
    This will compile your new test module along with others. Your test executable will appear in `tizen-vts/build/bin/`.

2.  **Running a Single Test (Development/Debugging):**
    You can push and run your test executable directly using SDB for quick debugging:
    ```bash
    # Assuming sdb is in your PATH and device is connected
    # Push the specific test
    sdb push tizen-vts/build/bin/my_feature_test_executable /opt/usr/devicetests/vts/bin/
    sdb shell chmod +x /opt/usr/devicetests/vts/bin/my_feature_test_executable

    # Run it and generate XML output
    sdb shell "/opt/usr/devicetests/vts/bin/my_feature_test_executable --gtest_output=xml:/opt/usr/devicetests/vts/results/my_feature_test_results.xml"
    
    # Pull the results
    sdb pull /opt/usr/devicetests/vts/results/my_feature_test_results.xml tizen-vts/results/
    ```

## Integration with the VTS Harness

*   The `tizen_vts_cli.py` harness automatically discovers any executable files in the `build/bin/` directory (as configured by its `--test-dir` option, which defaults to `../build/bin` relative to the harness).
*   To be properly processed by the harness for result reporting, your GTest executable **must** be run with the `--gtest_output=xml:<output_path>` flag. The harness handles this automatically when you use `run_test`.

## Result Generation

The harness expects GTest to produce an XML output file. This XML file is then fetched from the device, parsed, and used to generate an HTML report. Ensure your tests don't interfere with GTest's ability to generate this XML (e.g., by crashing prematurely without GTest handling it).

Happy testing!
```
