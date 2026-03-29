#!/usr/bin/env python3

import os

from ament_index_python.packages import get_package_share_directory
from launch.actions import (DeclareLaunchArgument, IncludeLaunchDescription,
                            LogInfo)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

from launch import LaunchDescription

# Launch arguments for RPLidar A1
channel_type = LaunchConfiguration('channel_type', default='serial')
serial_port = LaunchConfiguration('serial_port', default='/dev/ttyUSB0')
serial_baudrate = LaunchConfiguration('serial_baudrate', default=115200)
frame_id = LaunchConfiguration('frame_id', default='laser')
inverted = LaunchConfiguration('inverted', default=False)
angle_compensate = LaunchConfiguration('angle_compensate', default=True)
scan_mode = LaunchConfiguration('scan_mode', default='Sensitivity')

# Launch arguments for motor driver
max_linear_vel = LaunchConfiguration('max_linear_vel', default=1.0)
max_angular_vel = LaunchConfiguration('max_angular_vel', default=2.5)
left_right_ratio = LaunchConfiguration('left_right_ratio', default=1.0)
wheelbase = LaunchConfiguration('wheelbase', default=0.12)
wheel_radius = LaunchConfiguration('wheel_radius', default=0.032)
wheel_angvel_to_pwm = LaunchConfiguration('wheel_angvel_to_pwm', default=1.0)
invert_left_motor = LaunchConfiguration('invert_left_motor', default=False)
invert_right_motor = LaunchConfiguration('invert_right_motor', default=False)

# Launch arguments for IMU driver
yaw_b_i_deg = LaunchConfiguration('yaw_B_I_deg', default=180.0)
pitch_b_i_deg = LaunchConfiguration('pitch_B_I_deg', default=0.0)
roll_b_i_deg = LaunchConfiguration('roll_B_I_deg', default=180.0)
freq_hz = LaunchConfiguration('freq_hz', default=100.0)


def get_lidar_launch_arguments():
    return [
        DeclareLaunchArgument(
            'channel_type',
            default_value=channel_type,
            description='Specifying channel type of lidar'),

        DeclareLaunchArgument(
            'serial_port',
            default_value=serial_port,
            description='Specifying usb port to connected lidar'),

        DeclareLaunchArgument(
            'serial_baudrate',
            default_value=serial_baudrate,
            description='Specifying usb port baudrate to connected lidar'),

        DeclareLaunchArgument(
            'frame_id',
            default_value=frame_id,
            description='Specifying frame_id of lidar'),

        DeclareLaunchArgument(
            'inverted',
            default_value=inverted,
            description='Specifying whether or not to invert scan data'),

        DeclareLaunchArgument(
            'angle_compensate',
            default_value=angle_compensate,
            description='Specifying whether or not to enable angle_compensate of scan data'),
        DeclareLaunchArgument(
            'scan_mode',
            default_value=scan_mode,
            description='Specifying scan mode of lidar'),
    ]


def get_motor_driver_launch_arguments():
    return [
        DeclareLaunchArgument(
            'max_linear_vel',
            default_value=max_linear_vel,
            description='Maximum linear velocity for motor driver (m/s)'),

        DeclareLaunchArgument(
            'max_angular_vel',
            default_value=max_angular_vel,
            description='Maximum angular velocity for motor driver (rad/s)'),

        DeclareLaunchArgument(
            'left_right_ratio',
            default_value=left_right_ratio,
            description='Left-to-right motor speed ratio compensation'),

        DeclareLaunchArgument(
            'wheelbase',
            default_value=wheelbase,
            description='Distance between left and right wheel centers (m)'),

        DeclareLaunchArgument(
            'wheel_radius',
            default_value=wheel_radius,
            description='Wheel radius (m)'),

        DeclareLaunchArgument(
            'wheel_angvel_to_pwm',
            default_value=wheel_angvel_to_pwm,
            description='Conversion factor from wheel angular velocity to PWM'),

        DeclareLaunchArgument(
            'invert_left_motor',
            default_value=invert_left_motor,
            description='Whether to invert the left motor direction'),

        DeclareLaunchArgument(
            'invert_right_motor',
            default_value=invert_right_motor,
            description='Whether to invert the right motor direction'),
    ]


def get_imu_driver_launch_arguments():
    return [
        DeclareLaunchArgument(
            'yaw_B_I_deg',
            default_value=yaw_b_i_deg,
            description='Yaw rotation from IMU frame to robot body frame (deg)'),

        DeclareLaunchArgument(
            'pitch_B_I_deg',
            default_value=pitch_b_i_deg,
            description='Pitch rotation from IMU frame to robot body frame (deg)'),

        DeclareLaunchArgument(
            'roll_B_I_deg',
            default_value=roll_b_i_deg,
            description='Roll rotation from IMU frame to robot body frame (deg)'),

        DeclareLaunchArgument(
            'freq_hz',
            default_value=freq_hz,
            description='IMU polling frequency (Hz)'),
    ]


def generate_launch_description():

    return LaunchDescription(
        get_lidar_launch_arguments() +
        get_motor_driver_launch_arguments() +
        get_imu_driver_launch_arguments() +
        [
            Node(
                package='rplidar_ros',
                executable='rplidar_node',
                name='rplidar_node',
                parameters=[{'channel_type': channel_type,
                             'serial_port': serial_port,
                             'serial_baudrate': ParameterValue(serial_baudrate, value_type=int),
                             'frame_id': frame_id,
                             'inverted': ParameterValue(inverted, value_type=bool),
                             'angle_compensate': ParameterValue(angle_compensate, value_type=bool),
                             'scan_mode': scan_mode}],
                output='screen'),

            Node(
                package='motor_driver',
                executable='motor_driver_node',
                name='motor_driver_node',
                parameters=[{
                    'max_linear_vel': ParameterValue(max_linear_vel, value_type=float),
                    'max_angular_vel': ParameterValue(max_angular_vel, value_type=float),
                    'left_right_ratio': ParameterValue(left_right_ratio, value_type=float),
                    'wheelbase': ParameterValue(wheelbase, value_type=float),
                    'wheel_radius': ParameterValue(wheel_radius, value_type=float),
                    'wheel_angvel_to_pwm': ParameterValue(wheel_angvel_to_pwm, value_type=float),
                    'invert_left_motor': ParameterValue(invert_left_motor, value_type=bool),
                    'invert_right_motor': ParameterValue(invert_right_motor, value_type=bool),
                }],
                output='screen'),

            Node(
                package='imu_driver',
                executable='imu_driver_node',
                name='imu_driver_node',
                parameters=[{
                    'yaw_B_I_deg': ParameterValue(yaw_b_i_deg, value_type=float),
                    'pitch_B_I_deg': ParameterValue(pitch_b_i_deg, value_type=float),
                    'roll_B_I_deg': ParameterValue(roll_b_i_deg, value_type=float),
                    'freq_hz': ParameterValue(freq_hz, value_type=float),
                }],
                output='screen'),

            Node(
                package='tf2_ros',
                executable='static_transform_publisher',
                arguments=['0', '0', '0', '0', '0', '0', 'base_link', 'laser'],
                name='base_link_laser_tf',
                output='screen'),

            Node(
                package='rf2o_laser_odometry',
                executable='rf2o_laser_odometry_node',
                name='rf2o_laser_odometry',
                output='screen',
                parameters=[{
                    'laser_scan_topic': '/scan',
                    'odom_topic': '/odom',
                    'publish_tf': True,
                    'base_frame_id': 'base_link',
                    'odom_frame_id': 'odom',
                    'init_pose_from_topic': '',
                    'freq': 10.0}],
            )
        ])
