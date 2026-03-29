#!/usr/bin/env python3

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import LogInfo
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

# RPLidar A1 constants
LIDAR_CHANNEL_TYPE = 'serial'
LIDAR_BAUDRATE = '115200'
LIDAR_IS_INVERTED = 'false'
LIDAR_TO_ANGLE_COMPENSATE = 'true'
LIDAR_SCAN_MODE = 'Sensitivity'


def generate_launch_description():
    # Launch arguments for RPLidar A1
    lidar_serial_port = LaunchConfiguration('serial_port')
    lidar_frame_id = LaunchConfiguration('frame_id')

    # Launch arguments for motor driver
    max_linear_vel = LaunchConfiguration('max_linear_vel')
    max_angular_vel = LaunchConfiguration('max_angular_vel')
    left_right_ratio = LaunchConfiguration('left_right_ratio')
    wheelbase = LaunchConfiguration('wheelbase')
    wheel_radius = LaunchConfiguration('wheel_radius')
    wheel_angvel_to_pwm = LaunchConfiguration('wheel_angvel_to_pwm')
    invert_left_motor = LaunchConfiguration('invert_left_motor')
    invert_right_motor = LaunchConfiguration('invert_right_motor')

    # Launch arguments for IMU driver
    yaw_b_i_deg = LaunchConfiguration('yaw_B_I_deg')
    pitch_b_i_deg = LaunchConfiguration('pitch_B_I_deg')
    roll_b_i_deg = LaunchConfiguration('roll_B_I_deg')
    freq_hz = LaunchConfiguration('freq_hz')

    return LaunchDescription([
        DeclareLaunchArgument(
            'serial_port',
            default_value='/dev/ttyUSB0',
            description='Specifying usb port to connected lidar'),

        DeclareLaunchArgument(
            'frame_id',
            default_value='laser',
            description='Specifying TF frame_id of lidar'),

        DeclareLaunchArgument(
            'max_linear_vel',
            default_value='1.0',
            description='Maximum linear velocity for motor driver (m/s)'),

        DeclareLaunchArgument(
            'max_angular_vel',
            default_value='2.5',
            description='Maximum angular velocity for motor driver (rad/s)'),

        DeclareLaunchArgument(
            'left_right_ratio',
            default_value='1.0',
            description='Left-to-right motor speed ratio compensation'),

        DeclareLaunchArgument(
            'wheelbase',
            default_value='0.12',
            description='Distance between left and right wheel centers (m)'),

        DeclareLaunchArgument(
            'wheel_radius',
            default_value='0.032',
            description='Wheel radius (m)'),

        DeclareLaunchArgument(
            'wheel_angvel_to_pwm',
            default_value='20.0',
            description='Conversion factor from wheel angular velocity to PWM'),

        DeclareLaunchArgument(
            'invert_left_motor',
            default_value='false',
            description='Whether to invert the left motor direction'),

        DeclareLaunchArgument(
            'invert_right_motor',
            default_value='false',
            description='Whether to invert the right motor direction'),

        DeclareLaunchArgument(
            'yaw_B_I_deg',
            default_value='180.0',
            description='Yaw rotation from IMU frame to robot body frame (deg)'),

        DeclareLaunchArgument(
            'pitch_B_I_deg',
            default_value='0.0',
            description='Pitch rotation from IMU frame to robot body frame (deg)'),

        DeclareLaunchArgument(
            'roll_B_I_deg',
            default_value='180.0',
            description='Roll rotation from IMU frame to robot body frame (deg)'),

        DeclareLaunchArgument(
            'freq_hz',
            default_value='50.0',
            description='IMU polling frequency (Hz)'),

        Node(
            package='rplidar_ros',
            executable='rplidar_node',
            name='rplidar_node',
            parameters=[{'channel_type': LIDAR_CHANNEL_TYPE,
                         'serial_port': lidar_serial_port,
                         'serial_baudrate': LIDAR_BAUDRATE,
                         'frame_id': lidar_frame_id,
                         'inverted': LIDAR_IS_INVERTED,
                         'angle_compensate': LIDAR_TO_ANGLE_COMPENSATE,
                         'scan_mode': LIDAR_SCAN_MODE}],
            output='screen'),

        Node(
            package='motor_driver',
            executable='motor_driver_node',
            name='motor_driver_node',
            parameters=[{
                'max_linear_vel': max_linear_vel,
                'max_angular_vel': max_angular_vel,
                'left_right_ratio': left_right_ratio,
                'wheelbase': wheelbase,
                'wheel_radius': wheel_radius,
                'wheel_angvel_to_pwm': wheel_angvel_to_pwm,
                'invert_left_motor': invert_left_motor,
                'invert_right_motor': invert_right_motor,
            }],
            output='screen'),

        Node(
            package='imu_driver',
            executable='imu_driver_node',
            name='imu_driver_node',
            parameters=[{
                'yaw_B_I_deg': yaw_b_i_deg,
                'pitch_B_I_deg': pitch_b_i_deg,
                'roll_B_I_deg': roll_b_i_deg,
                'freq_hz': freq_hz,
            }],
            output='screen'),
    ])
