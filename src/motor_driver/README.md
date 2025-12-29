# Motor Driver Module

This package was generated from the ROS2 template:

```bash
ros2 pkg create --build-type ament_python --node-name motor_driver_node motor_driver
```

This package contains the driver program that subscribes to a `twist` command and interfaces with a motor driver on the Raspberry Pi to output the relevant motor commands.

This is a basic example, implemented in Python as a learning exercise.

> **NOTE:** Ideally, one would implement this package as a standalone git repo, which would then be pulled into the overall system repo as a submodule.
