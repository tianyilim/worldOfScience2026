#!/bin/bash
set -e

git submodule update --init --recursive

# Install relevant packages system-wide
sudo apt update
sudo apt install -y python3-smbus python3-venv python3-pip \
    net-tools network-manager build-essential cmake \
    python3-colcon-common-extensions

# Permissions for I2C and serial
sudo usermod -aG i2c "$USER"
sudo usermod -aG dialout "$USER"

# Install relevant pip packages
python3 -m pip install --upgrade pip --break-system-packages
python3 -m pip install --break-system-packages catkin_pkg smbus numpy

# Build the workspace. The CMake arg ensures that colcon/cmake uses the venv's Python, and not any other python exe from
# e.g conda.
colcon build --symlink-install
