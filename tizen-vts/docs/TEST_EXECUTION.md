# Executing Tizen VTS Tests

This guide explains how to use the Tizen Vendor Test Suite (VTS) Command Line Interface (CLI) harness (`tizen_vts_cli.py`) to execute tests on a connected Tizen device and interpret the results.

## Prerequisites

1.  **Host and Target Setup:** Ensure your host machine and Tizen target device(s) are correctly set up as per the `SETUP.md` guide.
2.  **SDB Connection:** Verify that your Tizen device is connected to the host via USB and that SDB is operational (`sdb devices` should list your device).
3.  **Tests Built:** All VTS tests must be compiled using the build script:
    ```bash
    ./scripts/build_tests.sh
    ```
    This populates the `build/bin/` directory with test executables.

## Tizen VTS CLI Harness Overview

The primary tool for running tests is `tizen_vts_cli.py`, located in the `harness/` directory. It provides functionalities to:

*   List available test executables.
*   Deploy and run selected tests on a Tizen target device.
*   Fetch test results (GTest XML output) from the device.
*   Generate an HTML report summarizing the test outcomes.

## Using the CLI Harness

Navigate to the `tizen-vts` root directory in your terminal.

### Common CLI Options

The harness supports several command-line options:

*   `--test-dir <path>`: Specifies the directory on the host where compiled test executables are located. Defaults to `tizen-vts/build/bin/` (relative to the `tizen-vts` root).
*   `--sdb-path <path>`: Path to the `sdb` executable if it's not in your system's PATH.
*   `--target-id <device_serial>` or `-s <device_serial>`: Specifies the target Tizen device by its serial number if multiple devices are connected.
*   `--gtest_filter <GTEST_FILTER_PATTERN>`: An optional argument for the `run_test` command that allows you to pass a filter pattern directly to the GTest executable. This is useful for running a subset of tests within a larger test executable. The pattern follows GTest's filter syntax (e.g., `TestSuiteName.*` to run all tests in `TestSuiteName`, `*Positive*` to run tests containing "Positive", or `-TestSuiteName.TestToExclude` to exclude a specific test). Example: `python3 harness/tizen_vts_cli.py run_test sample_hal_test --gtest_filter="*Power*"`
*   `-v`, `--verbose`: Increase output verbosity. Use multiple times for more detail (e.g., `-v` for basic verbose messages including SDB commands, `-vv` for more detailed SDB command outputs like stderr). Useful for debugging or understanding harness operations.

**Note on Paths:**
*   **Host Results Directory:** XML results and HTML reports are saved in `tizen-vts/results/` on the host machine. This is currently a fixed path.
*   **Remote Test Root:** Tests are pushed to and executed from `/opt/usr/devicetests/vts/` on the Tizen target device. Binaries are placed in a `bin` subdirectory, and GTest XML results are temporarily stored in a `results` subdirectory within this remote root. This is also currently a fixed path in the harness.

### Listing Available Tests

To see which test executables are available (i.e., present in the build output directory):

```bash
python3 harness/tizen_vts_cli.py list_tests
# Example with custom test directory:
# python3 harness/tizen_vts_cli.py --test-dir my_custom_build/bin list_tests
```

### Running Tests (Single or Multiple)

To run a specific test executable (e.g., `sample_hal_test`) or a group of tests matching a pattern:

```bash
python3 harness/tizen_vts_cli.py run_test sample_hal_test
python3 harness/tizen_vts_cli.py run_test sample_*_test
python3 harness/tizen_vts_cli.py run_test *_kernel_*
```

If the pattern matches multiple test executables, the harness will run each one sequentially.

The `--gtest_filter` option can be used in conjunction with patterns. The GTest filter will be applied to *each* test executable that matches the `test_pattern`. For example:

```bash
python3 harness/tizen_vts_cli.py run_test sample_*_test --gtest_filter="*Power*"
```
This would run all tests containing "Power" within `sample_hal_test` (if it matches the `sample_*_test` pattern) and then all tests containing "Power" within `sample_kernel_test` (if it also matches), etc.

If you have multiple devices connected, specify the target:

```bash
python3 harness/tizen_vts_cli.py -s <your_device_serial> run_test sample_*_test --gtest_filter="*Power*"
```

The harness will:
1.  Push the test executable (`sample_hal_test`) to the device (e.g., `/opt/usr/devicetests/vts/bin/`).
2.  Execute the test on the device. GTest will be instructed to save its XML output on the device (e.g., in `/opt/usr/devicetests/vts/results/`).
3.  Fetch the XML result file back to the host (e.g., `tizen-vts/results/`).
4.  Parse the XML and generate an HTML report (e.g., in `tizen-vts/results/`).

### Understanding Test Output

*   **Console Output:** The CLI will show real-time status messages, including SDB commands being executed, test progress (if the test prints to stdout/stderr on the device), and paths to result files.
*   **XML Results:** Raw GTest XML output files (e.g., `sample_hal_test_results.xml`) are stored in the host results directory (default: `tizen-vts/results/`). These are useful for detailed analysis or integration with other tools.
*   **HTML Report:** A human-readable HTML report (e.g., `sample_hal_test_report_YYYYMMDD_HHMMSS.html`) is generated in the host results directory. Open this file in a web browser to see a summary of test suites, test cases, pass/fail status, execution times, and failure messages.

### Running Multiple Tests (Current Approach)

The `run_test` command now supports patterns for the test executable name. It can execute a single test if the pattern is an exact name, or multiple tests if the pattern uses wildcards (e.g., `*`, `?`). Each matched test executable will be run sequentially.

A single test executable can contain multiple test cases and test suites (as defined by GTest). The `--gtest_filter` can be used to run a subset of these test cases within each matched executable.

## Troubleshooting

*   **"SDB command failed" / "sdb: command not found":**
    *   Ensure Tizen Studio (or Tizen SDK tools) is installed and the directory containing `sdb` is in your system's PATH.
    *   Alternatively, use the `--sdb-path /path/to/your/sdb` option.
    *   Check device connection with `sdb devices`. Ensure the device is listed and 'authorized'. If it says 'offline' or 'unauthorized', check USB connection and device screen for authorization prompts.
*   **"Test executable ... not found in ...":**
    *   Ensure you have run `./scripts/build_tests.sh` successfully.
    *   Verify the test executable exists in the directory specified by `--test-dir` (default `build/bin/`).
*   **Permissions Issues on Device:**
    *   The harness attempts to `chmod +x` tests after pushing. If execution still fails due to permissions, it might indicate issues with the remote mount point or user privileges under which `sdbd` is running on the device. The default `/opt/usr/` location is generally chosen for its writability.
*   **Test Failures:**
    *   Examine the HTML report for failure messages.
    *   Look at the GTest XML output for more raw details.
    *   Check `dlogutil` (Tizen's device log) on the target device for any relevant system messages or crashes related to the test.
```
