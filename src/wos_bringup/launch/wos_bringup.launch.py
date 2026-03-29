#!/usr/bin/env python3

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

LIDAR_CHANNEL_TYPE = 'serial'
LIDAR_SERIAL_BAUDRATE = '115200'
LIDAR_INVERTED = 'false'
LIDAR_ANGLE_COMPENSATE = 'true'
LIDAR_SCAN_MODE = 'Sensitivity'


def generate_launch_description():
    serial_port = LaunchConfiguration('serial_port', default='/dev/ttyUSB0')
    frame_id = LaunchConfiguration('frame_id', default='laser')

    return LaunchDescription([
        DeclareLaunchArgument(
            'serial_port',
            default_value=serial_port,
            description='Specifying usb port to connected lidar'),

        DeclareLaunchArgument(
            'frame_id',
            default_value=frame_id,
            description='Specifying frame_id of lidar'),

        Node(
            package='rplidar_ros',
            executable='rplidar_node',
            name='rplidar_node',
            parameters=[{'channel_type': LIDAR_CHANNEL_TYPE,
                         'serial_port': serial_port,
                         'serial_baudrate': LIDAR_SERIAL_BAUDRATE,
                         'frame_id': frame_id,
                         'inverted': LIDAR_INVERTED,
                         'angle_compensate': LIDAR_ANGLE_COMPENSATE}],
            output='screen'),
    ])
