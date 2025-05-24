#!/bin/bash

# Basic Host Setup Script for Tizen VTS
# This script provides guidance on installing common dependencies.
# It does not execute all commands automatically but shows what is typically needed.

echo "Tizen VTS - Host Setup Helper"
echo "--------------------------------"
echo "This script will guide you through installing common dependencies."
echo "It's recommended to run these commands manually or adapt them to your specific Linux distribution."
echo ""

# Check for root privileges
if [ "$EUID" -ne 0 ]; then
  echo "Some commands (like apt-get or dnf) may require root privileges (sudo)."
fi
echo ""

echo "Essential Development Tools (gcc, g++, make):"
echo "  Debian/Ubuntu: sudo apt-get update && sudo apt-get install build-essential"
echo "  Fedora: sudo dnf groupinstall \"Development Tools\""
echo "  Please ensure you have a C++ compiler (g++) and make."
echo ""

echo "CMake (Build System):"
echo "  Debian/Ubuntu: sudo apt-get install cmake"
echo "  Fedora: sudo dnf install cmake"
echo "  Verify: cmake --version"
echo ""

echo "Python 3 and Pip:"
echo "  Debian/Ubuntu: sudo apt-get install python3 python3-pip"
echo "  Fedora: sudo dnf install python3 python3-pip"
echo "  Verify: python3 --version"
echo ""

echo "Git (Version Control):"
echo "  Debian/Ubuntu: sudo apt-get install git"
echo "  Fedora: sudo dnf install git"
echo "  Verify: git --version"
echo ""

echo "Tizen SDB (Smart Development Bridge):"
echo "  SDB is part of the Tizen SDK or Tizen Studio."
echo "  Ensure Tizen Studio is installed and its 'tools' directory (containing sdb) is in your PATH."
echo "  Alternatively, ensure sdb is accessible if installed via other means."
echo "  Verify: sdb version"
echo ""

echo "Google Test (GTest) Development Libraries:"
echo "  GTest is often best compiled from source alongside your project or installed system-wide."
echo "  The VTS build system (CMake) will attempt to download and build GTest if not found."
echo "  Alternatively, on Debian/Ubuntu: sudo apt-get install libgtest-dev"
echo "  Note: If using libgtest-dev, you might need to compile it yourself:"
echo "    cd /usr/src/googletest"
echo "    sudo cmake ."
echo "    sudo make"
echo "    sudo cp lib/*.a /usr/lib/  # Or use lib64 on some systems"
echo "  It's often simpler to let the project's CMake handle GTest."
echo ""

echo "Setup complete. Please verify each dependency is installed correctly."
echo "Refer to tizen-vts/docs/SETUP.md for more detailed instructions."
