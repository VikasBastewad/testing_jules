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

### Running a Single Test

To run a specific test executable (e.g., `sample_hal_test`):

```bash
python3 harness/tizen_vts_cli.py run_test sample_hal_test
```

If you have multiple devices connected, specify the target:

```bash
python3 harness/tizen_vts_cli.py -s <your_device_serial> run_test sample_hal_test
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

Currently, the `run_test` command executes one test *executable* at a time. A single test executable can contain multiple test cases and test suites (as defined by GTest).

To run all tests or a subset of tests defined in different executables, you would typically use a shell script or another automation layer to call `python3 harness/tizen_vts_cli.py run_test ...` multiple times.

Example (in a bash script):
```bash
#!/bin/bash
# tests_to_run.sh
python3 harness/tizen_vts_cli.py run_test sample_hal_test
python3 harness/tizen_vts_cli.py run_test sample_kernel_test
# Add more tests as needed
```

Future enhancements to the harness may include support for test plans to manage execution of multiple test executables.

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
