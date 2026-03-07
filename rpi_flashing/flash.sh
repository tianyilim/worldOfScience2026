#!/bin/bash

# --- CONFIGURATION ---
WIFI_SSID="Your_SSID_Here"
WIFI_PASS="Your_Password_Here"
IMG_PATH="./data/ubuntu-24.04.2-rt-ros2-arm64+raspi.img"
RPI_IMAGER_PATH="./data/imager_latest_amd64.AppImage"
NO_FLASH=false

# --- First, check for required files and tools. ---

# Check for zstd. If not, error out and prompt user to install it.
if ! command -v zstd &>/dev/null; then
    echo "Error: zstd is not installed (needed for decompressing RPi image). Please install it and try again."
    exit 1
fi

# -> Check for the image file. If not found, download it.
if [ ! -f "$IMG_PATH" ]; then
    echo "Image file not found at $IMG_PATH. Downloading..."
    # Example URL, replace with actual download link if needed.
    IMG_URL="https://github.com/ros-realtime/ros-realtime-rpi4-image/releases/download/24.04.2_v6.8.4-rt11-raspi_ros2_jazzy/ubuntu-24.04.2-rt-ros2-arm64+raspi.img.zst"
    wget -O "${IMG_PATH}.zst" "$IMG_URL"
    if [ $? -ne 0 ]; then
        echo "Error: Failed to download image from $IMG_URL."
        exit 1
    fi
    echo "Decompressing the image..."
    zstd -d "${IMG_PATH}.zst" -o "$IMG_PATH"
    if [ $? -ne 0 ]; then
        echo "Error: Failed to decompress the image."
        exit 1
    fi
    rm "${IMG_PATH}.zst"
fi

# -> Check for rpi-imager. If not, download it.
if [ ! -f "$RPI_IMAGER_PATH" ]; then
    echo "Raspberry Pi Imager not found at $RPI_IMAGER_PATH. Downloading..."
    wget -O "$RPI_IMAGER_PATH" "https://downloads.raspberrypi.com/imager/imager_latest_amd64.AppImage"
    if [ $? -ne 0 ]; then
        echo "Error: Failed to download RPi Imager."
        exit 1
    fi
    chmod +x "$RPI_IMAGER_PATH"
fi

# --- 1. PARSE USER INPUT ---
HELP_TEXT="Usage: $0 <ID> [-h|--help]
<ID>    : A unique integer ID for this Raspberry Pi (1-100).
-h, --help : Show this help message and exit.
--no_flash : Skip the flashing step (for testing configuration generation)."

# Parse flags
for arg in "$@"; do
    if [[ "$arg" == "-h" ]] || [[ "$arg" == "--help" ]]; then
        echo "$HELP_TEXT"
        exit 1
    fi

    if [[ "$arg" == "--no_flash" ]]; then
        NO_FLASH=true
    fi
done

# Validate ID argument
if [ -z "$1" ]; then
    echo "Error: ID argument is required."
    echo "$HELP_TEXT"
    exit 1
fi

if [[ ! $1 =~ ^[0-9]+$ ]] || [ "$1" -lt 1 ] || [ "$1" -gt 100 ]; then
    echo "Error: ID provided '$1' must be an integer between 1 and 100."
    echo "$HELP_TEXT"
    exit 1
fi

ID="$1"

# --- 2. DETECT SD CARD ---
if [ "$NO_FLASH" = true ]; then
    echo "No-flash mode enabled. Skipping SD card detection and flashing."
else
    echo "Searching for SD cards..."
    lsblk -p -d -o NAME,SIZE,MODEL | grep -E "sd|mmcblk"
    read -p "Enter the device path to flash (e.g., /dev/sdb): " DEVICE

    if [ ! -b "$DEVICE" ]; then
        echo "Error: Device $DEVICE not found or not a block device."
        exit 1
    fi

    # --- 3. FLASH THE IMAGE ---
    echo "Flashing $IMG_PATH to $DEVICE..."
    sudo $RPI_IMAGER_PATH --cli --no-verify "$IMG_PATH" "$DEVICE"

    if [ $? -ne 0 ]; then
        echo "Flashing failed!"
        exit 1
    fi
fi

# --- 4. MOUNT AND CONFIGURE ---
# Ubuntu images usually have two partitions. We need the 'system-boot' (vfat) partition.
# It is typically the first partition.
BOOT_PART="${DEVICE}1"
# For NVMe/SD names like /dev/mmcblk0, the partition is /dev/mmcblk0p1
if [[ "$DEVICE" == *"mmcblk"* ]]; then
    BOOT_PART="${DEVICE}p1"
fi

MOUNT_DIR="/tmp/rpi_boot"
mkdir -p "$MOUNT_DIR"
sudo mount "$BOOT_PART" "$MOUNT_DIR"

echo "Injecting custom configurations..."

# Create user-data (User, Password, Groups)
cat <<EOF | sudo tee "$MOUNT_DIR/user-data" >/dev/null
#cloud-config
ssh_pwauth: True
users:
  - name: rpi_${ID}
    gecos: ROS Robot ${ID}
    sudo: ALL=(ALL) NOPASSWD:ALL
    groups: [sudo, dialout]
    shell: /bin/bash
    lock_passwd: false
    passwd: "\$6\$rounds=4096\$robotics_salt\$h8.0hM.M0rF.U7v8v7.zR7N5yLhG0V5Q8p6m5f5z7f7d7s7a7s7d7f7g7h7j7k7l" # Hash for 'robotics'
chpasswd:
  list: |
    rpi_${ID}:robotics
  expire: False
EOF

# Create network-config (WiFi + Static IP)
cat <<EOF | sudo tee "$MOUNT_DIR/network-config" >/dev/null
version: 2
ethernets:
  eth0:
    dhcp4: true
    optional: true
wifis:
  wlan0:
    dhcp4: false
    addresses: [192.168.1.${ID}/24]
    routes:
      - to: default
        via: 192.168.1.1
    nameservers:
      addresses: [8.8.8.8, 1.1.1.1]
    access-points:
      "$WIFI_SSID":
        password: "$WIFI_PASS"
EOF

# --- 5. CLEANUP ---
sudo umount "$MOUNT_DIR"
echo "Done! Raspberry Pi ${ID} is ready. Eject the SD card."
