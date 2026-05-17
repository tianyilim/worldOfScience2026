# Servo Driver Module

This package was generated from the ROS2 template:

```bash
ros2 pkg create --build-type ament_python --node-name servo_driver_node servo_driver
```

This interfaces with any servo over GPIO, subscribing either to:
- `std_msgs/Int8` for a direct servo angle command or
- `sensor_msgs/Joy` (left/right bumper) to influence angle of servo
