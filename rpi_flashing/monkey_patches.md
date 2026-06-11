## Adding to RPi Fan configs

Go to this file:
```bash
sudo vim /boot/firmware/config.txt
```

Add these lines:

```ini
dtparam=cooling_fan=on
dtparam=fan_temp0=40000
dtparam=fan_temp0_hyst=5000
dtparam=fan_temp0_speed=200
```

## Connecting to Playground Wifi

Run the following:

```bash
sudo vim /etc/netplan/50-cloud-init.yaml
```

Should give you something like this:

```yaml
network:
  version: 2
  ethernets:
    eth0:
      optional: true
      dhcp4: true
  wifis:
    wlan0:
      optional: true
      dhcp4: true
      access-points:
        "fluffy_clouds":
          auth:
            key-management: "psk"
            password: "sp1sp2sp3"
```

Add the playground wifi, should look something like this in the end:

```yaml
network:
  version: 2
  ethernets:
    eth0:
      optional: true
      dhcp4: true
  wifis:
    wlan0:
      optional: true
      dhcp4: true
      access-points:
        "fluffy_clouds":
          auth:
            key-management: "psk"
            password: "sp1sp2sp3"
        "DSO-World Of Science":
          auth:
            key-management: "psk"
            password: "Hell0DSO!"
```

01 - 192.168.1.129
02
03 - 192.168.1.130
04 - 192.168.1.128
05
06
07 - 192.168.1.131
11 - 192.168.1.132
