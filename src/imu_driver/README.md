# IMU Driver Module

This package was generated from the ROS2 template:

```bash
ros2 pkg create --build-type ament_python --node-name imu_driver_node imu_driver
```

This interfaces with the BNO055 IMU sensor over I2C, and publishes the raw angular velocity $\omega$ and linear acceleration $a$ readings as a `sensor_msgs/Imu` message.
