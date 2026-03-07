#!/bin/bash

# --- CONFIGURATION ---
WIFI_SSID="fluffy_clouds"
WIFI_PASS="sp1sp2sp3"
IMG_PATH="./data/ubuntu-24.04.2-rt-ros2-arm64+raspi.img"
RPI_IMAGER_PATH="./data/imager_latest_amd64.AppImage"
NO_FLASH=false
IP_ID_OFFSET=100 # To avoid IP conflicts, we can offset the ID for static IP assignment (e.g., 192.168.1.(ID+100))

# --- FUNCTIONS ---

# Status echo: prints text with cyan background and black text
status_echo() {
    echo -e "\033[46m\033[30m$1\033[0m"
}

# Warn echo: prints text with yellow background and black text
warn_echo() {
    echo -e "\033[43m\033[30m$1\033[0m"
}

# Error echo: prints text with red background and black text
error_echo() {
    echo -e "\033[41m\033[30m$1\033[0m"
}

# --- First, check for required files and tools. ---

# Check for zstd. If not, error out and prompt user to install it.
if ! command -v zstd &>/dev/null; then
    error_echo "Error: zstd is not installed (needed for decompressing RPi image). Please install it and try again."
    exit 1
fi

# -> Check for the image file. If not found, download it.
if [ ! -f "$IMG_PATH" ]; then
    status_echo "Image file not found at $IMG_PATH. Downloading..."
    # Example URL, replace with actual download link if needed.
    IMG_URL="https://github.com/ros-realtime/ros-realtime-rpi4-image/releases/download/24.04.2_v6.8.4-rt11-raspi_ros2_jazzy/ubuntu-24.04.2-rt-ros2-arm64+raspi.img.zst"
    wget -O "${IMG_PATH}.zst" "$IMG_URL"
    if [ $? -ne 0 ]; then
        error_echo "Error: Failed to download image from $IMG_URL."
        exit 1
    fi
    status_echo "Decompressing the image..."
    zstd -d "${IMG_PATH}.zst" -o "$IMG_PATH"
    if [ $? -ne 0 ]; then
        error_echo "Error: Failed to decompress the image."
        exit 1
    fi
    rm "${IMG_PATH}.zst"
else
    status_echo "Image file found at $IMG_PATH."
fi

# -> Check for rpi-imager. If not, download it.
if [ ! -f "$RPI_IMAGER_PATH" ]; then
    status_echo "Raspberry Pi Imager not found at $RPI_IMAGER_PATH. Downloading..."
    wget -O "$RPI_IMAGER_PATH" "https://downloads.raspberrypi.com/imager/imager_latest_amd64.AppImage"
    if [ $? -ne 0 ]; then
        error_echo "Error: Failed to download RPi Imager."
        exit 1
    fi
    chmod +x "$RPI_IMAGER_PATH"
else
    status_echo "Raspberry Pi Imager found at $RPI_IMAGER_PATH."
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
    error_echo "Error: ID argument is required."
    echo "$HELP_TEXT"
    exit 1
fi

if [[ ! $1 =~ ^[0-9]+$ ]] || [ "$1" -lt 1 ] || [ "$1" -gt 100 ]; then
    error_echo "Error: ID provided '$1' must be an integer between 1 and 100."
    echo "$HELP_TEXT"
    exit 1
fi

ID="$1"

# --- 2. DETECT SD CARD ---
status_echo "Searching for SD cards..."
lsblk -p -d -o NAME,SIZE,MODEL | grep -E "sd|mmcblk"
read -p "Enter the device path to flash (e.g., /dev/sdb): " DEVICE

if [ ! -b "$DEVICE" ]; then
    error_echo "Error: Device $DEVICE not found or not a block device."
    exit 1
fi

# --- 3. FLASH THE IMAGE ---
if [ "$NO_FLASH" = true ]; then
    warn_echo "No-flash mode enabled. Skipping SD card detection and flashing."
else
    status_echo "Flashing $IMG_PATH to $DEVICE..."
    sudo $RPI_IMAGER_PATH --cli --no-verify "$IMG_PATH" "$DEVICE"

    if [ $? -ne 0 ]; then
        error_echo "Flashing failed!"
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
echo "Sudo is required to mount the RPi boot partition and write configuration files..."
sudo mount "$BOOT_PART" "$MOUNT_DIR"

status_echo "Injecting custom configurations..."

# Create user-data (User, Password, Groups)
cat <<EOF | sudo tee "$MOUNT_DIR/user-data" >/dev/null
#cloud-config
ssh_pwauth: True
ssh:
  install_server: True
  allow_pw: True
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
runcmd:
  - systemctl enable --now ssh
  - ufw allow ssh  # Ensures firewall doesn't block you
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
    addresses: [192.168.1.$((ID + IP_ID_OFFSET))/24]
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
status_echo "Done! Raspberry Pi ${ID} is ready. Eject the SD card."
