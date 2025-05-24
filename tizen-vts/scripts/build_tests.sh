#!/bin/bash

# Script to build all Tizen VTS test executables

# Exit immediately if a command exits with a non-zero status.
set -e

# Get the root directory of the Tizen VTS project
# This assumes the script is in tizen-vts/scripts/
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="${PROJECT_ROOT}/build"
BIN_DIR="${BUILD_DIR}/bin" # Expected output directory for executables

echo "Tizen VTS - Build All Tests"
echo "---------------------------"
echo "Project Root: ${PROJECT_ROOT}"
echo "Build Directory: ${BUILD_DIR}"
echo ""

# Create the build directory if it doesn't exist
echo "Creating build directory..."
mkdir -p "${BUILD_DIR}"

# Navigate to the build directory
cd "${BUILD_DIR}"

# Run CMake to configure the project
# This assumes CMakeLists.txt is in PROJECT_ROOT
echo ""
echo "Running CMake..."
cmake "${PROJECT_ROOT}"

# Run Make to compile the tests
# The -j flag can be used to parallelize the build, e.g., make -j$(nproc)
echo ""
echo "Building tests with make..."
make

echo ""
echo "Build process completed."
if [ -d "${BIN_DIR}" ] && [ "$(ls -A ${BIN_DIR})" ]; then
   echo "Test executables should be in: ${BIN_DIR}"
   echo "Executables found:"
   ls -l "${BIN_DIR}"
else
   echo "Warning: No executables found in ${BIN_DIR}. Check the build process for errors."
fi

# Return to the original directory (optional)
cd "${PROJECT_ROOT}"
