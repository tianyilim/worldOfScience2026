# World Of Science ROS Code Repository

This repo contains the software stack for the reference WOS robots, as well as the sim environment to evaluate that they work.

## Raspberry Pi Setup

### Flashing Ubuntu on the Raspberry Pi

Using a Linux laptop with sudo rights and a SD card slot, run the [flashing script](./rpi_flashing/`flash.sh`):

```bash
./flash.sh $RPI_ID # 1-100
```

<details>
<summary>
This performs the following actions:
</summary>

1. Download the relevant Linux image from [this repo](https://github.com/ros-realtime/ros-realtime-rpi4-image).
   1. The release link containing the ROS Jazzy image (Ubuntu 24.04)
      [is here](https://github.com/ros-realtime/ros-realtime-rpi4-image/archive/refs/tags/24.04.2_v6.8.4-rt11-raspi_ros2_jazzy.zip).

2. The image is compressed with the zstd compression format.
   Decompresses it via the command `zstd -d filename.img.zst`. You may need to install zstd, with `sudo apt-get install zstd` on Ubuntu.

3. Flashes image to the specified SD card using Raspberry Pi imager (which is automatically downloaded if not present).

</details>

It then sets up username and password for the default user based on the `RPI_ID` specified:

> user: `rpi_$ID`
>
> pass: `robotics`

It automatically sets a wifi connection to `PLACEHOLDER` network.

[TODO] Need to copy out the MAC address of the RPi for static IP settings.

### Installing ROS and software stack

1. SSH into the RPi.
2. Clone this repo:

   ```bash
   git clone git@github.com:tianyilim/worldOfScience2026
   ```

3. Install the workspace using [`./install.sh`](./install.sh).

## Dev PC Setup
