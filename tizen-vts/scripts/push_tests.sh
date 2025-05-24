#!/bin/bash

# Script to push compiled Tizen VTS test executables to a target device.

# Exit immediately if a command exits with a non-zero status.
set -e

# Project root and binaries directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOCAL_BIN_DIR="${PROJECT_ROOT}/build/bin"

# Target device configuration
# SDB executable path - use system SDB by default
SDB_EXE="sdb"
# Allow overriding SDB path via environment variable
if [ -n "$SDB_PATH_OVERRIDE" ]; then
    SDB_EXE="$SDB_PATH_OVERRIDE"
fi

# Target device ID (optional, passed as first argument to script)
TARGET_DEVICE_ID_ARG=""
if [ -n "$1" ]; then
    TARGET_DEVICE_ID_ARG="-s $1"
    echo "Using Target Device ID: $1"
fi

REMOTE_BASE_DIR="/opt/usr/devicetests/vts"
REMOTE_BIN_DIR="${REMOTE_BASE_DIR}/bin" # Executables will go here
REMOTE_RESULTS_DIR="${REMOTE_BASE_DIR}/results" # For test outputs

echo "Tizen VTS - Push Tests to Device"
echo "--------------------------------"
echo "Local Binaries Directory: ${LOCAL_BIN_DIR}"
echo "Remote Target Directory for Binaries: ${REMOTE_BIN_DIR}"
echo "Remote Target Directory for Results: ${REMOTE_RESULTS_DIR}"
echo "SDB Executable: ${SDB_EXE}"
echo ""

# Check if local binaries directory exists and has content
if [ ! -d "${LOCAL_BIN_DIR}" ] || [ -z "$(ls -A ${LOCAL_BIN_DIR})" ]; then
    echo "Error: Local binaries directory '${LOCAL_BIN_DIR}' does not exist or is empty."
    echo "Please build the tests first using 'scripts/build_tests.sh'."
    exit 1
fi

# Check SDB connection
echo "Checking SDB connection and device status..."
# Construct the SDB command with potential target ID
SDB_CMD_PREFIX="${SDB_EXE} ${TARGET_DEVICE_ID_ARG}"

if ! ${SDB_CMD_PREFIX} shell "echo 'SDB connection OK'" &>/dev/null; then
    echo "Error: SDB connection failed. Ensure Tizen device is connected, authorized, and SDB is working."
    ${SDB_EXE} devices # Show available devices for diagnostics
    exit 1
fi
echo "SDB connection successful."

# Create remote directories on the device
echo ""
echo "Creating remote directories on device (if they don't exist)..."
${SDB_CMD_PREFIX} shell "mkdir -p ${REMOTE_BIN_DIR}"
${SDB_CMD_PREFIX} shell "mkdir -p ${REMOTE_RESULTS_DIR}"
echo "Remote directories ensured."

# Push all files from local_bin_dir to remote_bin_dir
echo ""
echo "Pushing test executables to ${REMOTE_BIN_DIR}..."
for test_exe in $(find "${LOCAL_BIN_DIR}" -maxdepth 1 -type f -executable); do
    test_exe_name=$(basename "${test_exe}")
    echo "Pushing ${test_exe_name}..."
    ${SDB_CMD_PREFIX} push "${test_exe}" "${REMOTE_BIN_DIR}/${test_exe_name}"
    # Make executable on target, sdb push might not preserve permissions correctly from all host OSes
    ${SDB_CMD_PREFIX} shell "chmod +x ${REMOTE_BIN_DIR}/${test_exe_name}"
done

echo ""
echo "All test executables pushed to device."
echo "You can now run tests using 'harness/tizen_vts_cli.py' or directly via SDB."
echo "Example: ${SDB_CMD_PREFIX} shell ${REMOTE_BIN_DIR}/sample_hal_test --gtest_output=xml:${REMOTE_RESULTS_DIR}/sample_hal_test_results.xml"
