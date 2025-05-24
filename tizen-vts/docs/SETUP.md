# Tizen VTS Setup Guide

This guide provides instructions for setting up your host machine and Tizen target device(s) to use the Tizen Vendor Test Suite (VTS).

## Host Environment Setup

It is recommended to use a Linux-based operating system for the host machine, as Tizen development tools are well-supported on Linux.

### Prerequisites:

1.  **Tizen SDK or Tizen Studio:**
    *   Install the latest Tizen Studio with its CLI tools. This will provide the Smart Development Bridge (`sdb`) utility, which is essential for communicating with Tizen devices.
    *   Ensure the Tizen SDK's `tools` directory (containing `sdb`) is added to your system's PATH environment variable.
    *   Alternatively, a standalone Tizen CLI tools package might be available.

2.  **C/C++ Build Tools:**
    *   **GCC/G++:** A C++ compiler (e.g., g++) is required to build the GTest-based test cases.
    *   **CMake:** CMake is used as the build system for the test cases.
    *   **Make:** The `make` utility is used to drive the build process.
    *   On Debian/Ubuntu: `sudo apt-get update && sudo apt-get install build-essential cmake g++`
    *   On Fedora: `sudo dnf groupinstall "Development Tools" && sudo dnf install cmake g++`

3.  **Python:**
    *   Python 3.6+ is required for the test harness CLI script.
    *   Pip (Python package installer) is also needed.
    *   On Debian/Ubuntu: `sudo apt-get install python3 python3-pip`
    *   On Fedora: `sudo dnf install python3 python3-pip`

4.  **Git:**
    *   Git is required to clone the Tizen VTS repository.
    *   On Debian/Ubuntu: `sudo apt-get install git`
    *   On Fedora: `sudo dnf install git`

### Obtaining Tizen VTS:

Clone the Tizen VTS repository from its source location (e.g., GitHub):

```bash
git clone <repository_url> tizen-vts
cd tizen-vts
```
(Replace `<repository_url>` with the actual URL when available.)

### Host Sanity Check:

Verify that the essential tools are accessible from your terminal:

```bash
sdb version
g++ --version
cmake --version
make --version
python3 --version
git --version
```

## Tizen Target (Device) Preparation

### 1. Enable Developer Mode:

*   On your Tizen device, navigate to **Settings > About device** (or similar).
*   Tap multiple times on a specific item (e.g., "Software version" or "Build number") until Developer Mode is enabled. The exact method can vary slightly between Tizen versions and device types.
*   Once enabled, you should find "Developer options" in the Settings menu.

### 2. Enable SDB Connection:

*   In "Developer options," ensure that "USB debugging" or "SDB debugging" is enabled.
*   Connect your Tizen device to your host machine via a USB cable.

### 3. Authorize Host Machine:

*   When you connect the device for the first time, the device may prompt you to authorize the connected PC for debugging. Accept this prompt.
*   On the host machine, you can check the list of connected devices:

    ```bash
    sdb devices
    ```
    Your device should be listed with a status of `device` (not `unauthorized` or `offline`). If it shows `unauthorized`, check the device screen for an authorization prompt.

### 4. Target Device Storage:

*   Ensure your Tizen device has sufficient free storage space to accommodate test executables and any temporary files they might create. A common location for deploying tests might be `/opt/usr/devicetests/` or a similar directory with write/execute permissions.

### 5. (Optional) Install GTest libraries on Target:
*   For some Tizen profiles or setups, the GTest libraries (`libgtest.so`, `libgtest_main.so`) might already be present.
*   If not, they might need to be cross-compiled for the Tizen target architecture and pushed to a standard library path on the device (e.g., `/usr/lib/`) or bundled with the tests. The VTS build system will aim to handle this.

This setup guide provides the initial steps. More specific configurations or dependencies might be required as the Tizen VTS evolves.
