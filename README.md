# World Of Science ROS Code Repository

This repo contains the software stack for the reference WOS robots, as well as the sim environment to evaluate that they work.

## Raspberry Pi Setup

### Flashing Ubuntu on the Raspberry Pi

Using a Linux laptop with sudo rights and a SD card slot, run the [flashing script](./rpi_flashing/`flash.sh`):

```bash
./flash.sh $RPI_ID \ # 1-100
   --wifi_ssid $WIFI_SSID --wifi_pass $WIFI_PASS
# Fill in WIFI_SSID, WIFI_PASS for the actual system
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

### Setting up static IP of Raspberry Pi

To obtain the MAC address of the RPi for setting static IP, you can run `ifconfig`.
The MAC address of note is in `wlan0`.

<details>
<summary>
Example ifconfig output:
</summary>

```
rpi_11@rpi11:~$ ifconfig
eth0: flags=4099<UP,BROADCAST,MULTICAST>  mtu 1500
        ether e4:5f:01:9c:f3:35  txqueuelen 1000  (Ethernet)
        RX packets 0  bytes 0 (0.0 B)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 0  bytes 0 (0.0 B)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

lo: flags=73<UP,LOOPBACK,RUNNING> mtu 65536
inet 127.0.0.1 netmask 255.0.0.0
inet6 ::1 prefixlen 128 scopeid 0x10<host>
loop txqueuelen 1000 (Local Loopback)
RX packets 5474 bytes 2579528 (2.5 MB)
RX errors 0 dropped 0 overruns 0 frame 0
TX packets 5474 bytes 2579528 (2.5 MB)
TX errors 0 dropped 0 overruns 0 carrier 0 collisions 0

wlan0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST> mtu 1500
inet 192.168.123.7 netmask 255.255.255.0 broadcast 192.168.123.255
inet6 fe80::e65f:1ff:fe9c:f336 prefixlen 64 scopeid 0x20<link>
ether e4:5f:01:9c:f3:36 txqueuelen 1000 (Ethernet)
RX packets 58217 bytes 36725951 (36.7 MB)
RX errors 0 dropped 0 overruns 0 frame 0
TX packets 42386 bytes 7540910 (7.5 MB)
TX errors 0 dropped 0 overruns 0 carrier 0 collisions 0

```

</details>

### Installing ROS and software stack

1. SSH into the RPi.
2. Clone this repo:

   ```bash
   git clone https://github.com/tianyilim/worldOfScience2026.git
   ```

3. Run the installation script in this folder: [`./install.sh <RPI_ID>`](./install.sh).

## Dev PC Setup

For now, this is the same as the ROS2 Jazzy [installation instructions](https://docs.ros.org/en/jazzy/Installation.html).

Additional software:

- VS Code
- Tmux (if using a Linux terminal), else Windows Terminal
- WinSCP if using Windows

## Running the Code

### RPi

1. RPi Driver:

   ```bash
   ros2 launch rplidar_ros rplidar_a1_launch.py
   ```

2. Motor Driver:

   ```bash
   ros2 run motor_driver motor_driver_node
   ```

3. SLAM

### Host PC

Ensure first that `ROS_DOMAIN_ID` is set properly.

You can identify this by doing `ros2 node list` and seeing if the list of nodes is as you expect.

> **TODO**: We should prefix the nodes with the `RPI_ID`, which would help immensely in debugging any future networking issues!

1. Teleop from Keyboard:

   ```bash
   # Need to set the linear and angular speeds appropriately
   ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -p speed:=0.05 -p turn:=2.5
   ```

2. RViz:

   ```bash
   rviz2 -d ./viz/worldOfScienceViz.rviz
   ```
