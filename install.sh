#!/bin/bash
set -e

# Install relevant packages system-wide
sudo apt update
sudo apt install -y python3-smbus python3-venv net-tools network-manager

# Create venv if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv ./venv
fi

# Permissions for I2C and serial
sudo usermod -aG i2c "$USER"
sudo usermod -aG dialout "$USER"

# Activate venv
source ./venv/bin/activate

# Install relevant packages in venv
python -m pip install --upgrade pip
python -m pip install colcon_common_extensions

# Build the workspace. The CMake arg ensures that colcon/cmake uses the venv's Python, and not any other python exe from
# e.g conda.
colcon build  --cmake-args -DPython3_FIND_VIRTUALENV="ONLY"
