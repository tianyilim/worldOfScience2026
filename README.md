# World Of Science ROS Code Repository

This repo contains the software stack for the reference WOS robots, as well as the sim environment to evaluate that they work.

## Raspberry Pi Setup

1. Download the relevant Linux image from [this repo](https://github.com/ros-realtime/ros-realtime-rpi4-image).
   1. The release link containing the ROS Jazzy image (Ubuntu 24.04)
      [is here](https://github.com/ros-realtime/ros-realtime-rpi4-image/archive/refs/tags/24.04.2_v6.8.4-rt11-raspi_ros2_jazzy.zip).
2. The image is compressed with the zstd compression format.
   You will need to decompress it via the command `zstd -d filename.img.zst`. You may need to install zstd, with `sudo apt-get install zstd` on Ubuntu.
3. After decompressing the image: the easiest way to flash the image to an SD card is via the Raspberry Pi imager.
   1. Using the Raspberry Pi Image, click CHOOSE OS.
   2. Scroll all the way down and click Use custom.
   3. Browse and select the image file.
   4. Select the storage device.
   5. Click Write to flash the image.
   6. Wait for it to be done.
4. [TODO] Need some way to set the username, password, enable password SSH login just by editing the SD card image.
5. [TODO] Need to set up connection to wifi using the SD card image.
6. [TODO] Need to copy out the MAC address of the RPi for static IP settings.
7. SSH into the RPi. Clone this repo.
8. Install the workspace using [`./install.sh`](./install.sh).

## Dev PC Setup
