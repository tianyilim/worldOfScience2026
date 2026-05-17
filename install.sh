#!/bin/bash
set -e

if [ -z "$RPI_ID" ]; then
    # RPI_ID is empty or completely unset.
    # Check that an argument is specified.
    if [ $# -eq 0 ]; then
        echo "Usage: $0 <RPI_ID>"
        exit 1
    fi

    # Argument is specified.
    RPI_ID="$1"
    echo "RPI_ID is set to '$RPI_ID' from argument."    
else
    echo "RPI_ID is set to '$RPI_ID' from env variables."
fi

if [[ ! $RPI_ID =~ ^[0-9]+$ ]] || [ "$RPI_ID" -lt 1 ] || [ "$RPI_ID" -gt 100 ]; then
    error_echo "Error: RPI_ID provided '$RPI_ID' must be an integer between 1 and 100."
    exit 1
fi

git submodule update --init --recursive

# Install relevant packages system-wide
sudo apt update
sudo apt install -y python3-smbus python3-venv python3-pip \
    net-tools network-manager build-essential cmake \
    python3-colcon-common-extensions ros-jazzy-slam-toolbox

# Permissions for I2C and serial
sudo usermod -aG i2c "$USER"
sudo usermod -aG dialout "$USER"

# Install relevant pip packages
python3 -m pip install --upgrade pip --break-system-packages
python3 -m pip install --break-system-packages catkin_pkg \
    smbus numpy \
    adafruit-circuitpython-bno055 adafruit-blinka \
    RPi.GPIO

# Build the workspace. The CMake arg ensures that colcon/cmake uses the venv's Python, and not any other python exe from
# e.g conda.
colcon build --symlink-install

# Add to .bashrc to auto-source this workspace and to set the correct ROS_DOMAIN_ID
{
    echo "source /opt/ros/jazzy/setup.bash"
    echo "source $(pwd)/install/setup.bash"
    echo "export ROS_DOMAIN_ID=$RPI_ID"
    echo "ROS_DOMAIN_ID is set to $ROS_DOMAIN_ID"
} >>~/.bashrc
