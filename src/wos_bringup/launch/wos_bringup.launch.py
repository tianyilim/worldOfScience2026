#!/usr/bin/env python3

import os

from ament_index_python.packages import get_package_share_directory
from launch.actions import (DeclareLaunchArgument, GroupAction,
                            IncludeLaunchDescription)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_xml.launch_description_sources import XMLLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node, PushRosNamespace, SetRemap
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare

from launch import LaunchDescription

rpi_id = os.environ.get('RPI_ID')
if not rpi_id:
    raise RuntimeError('RPI_ID environment variable must be set')

robot_namespace = f'/rpi_{rpi_id}'

# Launch arguments for RPLidar A1
channel_type = LaunchConfiguration('channel_type', default='serial')
serial_port = LaunchConfiguration('serial_port', default='/dev/ttyUSB0')
serial_baudrate = LaunchConfiguration('serial_baudrate', default=115200)
frame_id = LaunchConfiguration('frame_id', default='laser')
inverted = LaunchConfiguration('inverted', default=False)
angle_compensate = LaunchConfiguration('angle_compensate', default=True)
scan_mode = LaunchConfiguration('scan_mode', default='Sensitivity')

# Launch arguments for motor driver
max_linear_vel = LaunchConfiguration('max_linear_vel', default=0.25)
max_angular_vel = LaunchConfiguration('max_angular_vel', default=2.5)
left_right_ratio = LaunchConfiguration('left_right_ratio', default=1.0)
wheelbase = LaunchConfiguration('wheelbase', default=0.12)
wheel_radius = LaunchConfiguration('wheel_radius', default=0.032)
wheel_angvel_to_pwm = LaunchConfiguration('wheel_angvel_to_pwm', default=20.0)
invert_left_motor = LaunchConfiguration('invert_left_motor', default=False)
invert_right_motor = LaunchConfiguration('invert_right_motor', default=False)

# Launch arguments for servo driver
servo_pin = LaunchConfiguration('servo_pin', default='11')
max_angle = LaunchConfiguration('max_angle', default='150')
min_angle = LaunchConfiguration('min_angle', default='0')
joy_open_button_index = LaunchConfiguration(
    'joy_open_button_index', default='2')
joy_close_button_index = LaunchConfiguration(
    'joy_close_button_index', default='0')
joy_angle_increment = LaunchConfiguration('joy_angle_increment', default='2')

# Launch arguments for SLAM
slam_params_file = LaunchConfiguration(
    'slam_params_file',
    default=PathJoinSubstitution([
        FindPackageShare('wos_bringup'),
        'config', 'slam_online_async.yaml']))


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


def get_servo_driver_launch_arguments():
    return [
        DeclareLaunchArgument(
            'servo_pin',
            default_value=servo_pin,
            description='GPIO pin number for servo output'),

        DeclareLaunchArgument(
            'max_angle',
            default_value=max_angle,
            description='Maximum angle for the servo (degrees)'),

        DeclareLaunchArgument(
            'min_angle',
            default_value=min_angle,
            description='Minimum angle for the servo (degrees)'),

        DeclareLaunchArgument(
            'joy_open_button_index',
            default_value=joy_open_button_index,
            description='Joy button index for opening the servo'),

        DeclareLaunchArgument(
            'joy_close_button_index',
            default_value=joy_close_button_index,
            description='Joy button index for closing the servo'),

        DeclareLaunchArgument(
            'joy_angle_increment',
            default_value=joy_angle_increment,
            description='Angle increment for joystick control (degrees)'),
    ]


def generate_launch_description():
    # Include SLAM Toolbox Launch
    slam_toolbox_launch = GroupAction(
        actions=[
            PushRosNamespace(robot_namespace),
            SetRemap(src='/scan', dst='scan'),
            SetRemap(src='/map', dst='map'),
            SetRemap(src='/map_metadata', dst='map_metadata'),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(get_package_share_directory('slam_toolbox'),
                                 'launch', 'online_async_launch.py')
                ),
                launch_arguments={
                    'slam_params_file': slam_params_file
                }.items())
        ]
    )
    # Include BLE Teleop Joy Launch
    joy_launch = IncludeLaunchDescription(
        XMLLaunchDescriptionSource(
            os.path.join(get_package_share_directory('wos_bringup'),
                         'launch', 'ble_teleop_joy.launch.xml')
        ),
        launch_arguments={
            'namespace': robot_namespace,
        }.items()
    )

    robot_nodes = GroupAction(
        actions=[
            # Set namespace prefix for all nodes
            PushRosNamespace(robot_namespace),
            # Remap scan and map topic to be relative to namespace
            SetRemap(src='/scan', dst='scan'),
            SetRemap(src='/map', dst='map'),

            Node(
                package='rplidar_ros',
                executable='rplidar_node',
                parameters=[{'channel_type': channel_type,
                             'serial_port': serial_port,
                             'serial_baudrate': ParameterValue(serial_baudrate, value_type=int),
                             'frame_id': frame_id,
                             'inverted': ParameterValue(inverted, value_type=bool),
                             'angle_compensate': ParameterValue(angle_compensate, value_type=bool),
                             'scan_mode': scan_mode}],
                output='log'),

            Node(
                package='motor_driver',
                executable='motor_driver_node',
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
                package='servo_driver',
                executable='servo_driver_node',
                parameters=[{
                    'servo_pin': ParameterValue(servo_pin, value_type=int),
                    'max_angle': ParameterValue(max_angle, value_type=int),
                    'min_angle': ParameterValue(min_angle, value_type=int),
                    'joy_angle_increment': ParameterValue(joy_angle_increment, value_type=int),
                    'joy_open_button_index': ParameterValue(joy_open_button_index, value_type=int),
                    'joy_close_button_index': ParameterValue(joy_close_button_index, value_type=int)
                }],
                output='screen'),

            Node(
                package='tf2_ros',
                executable='static_transform_publisher',
                arguments=['0', '0', '0', '0', '0',
                           '0', 'base_footprint', 'laser'],
                name='base_footprint_laser_tf',
                output='log'),

            Node(
                package='rf2o_laser_odometry',
                executable='rf2o_laser_odometry_node',
                output='log',
                parameters=[{
                    'laser_scan_topic': 'scan',
                    'odom_topic': 'odom',
                    'publish_tf': True,
                    'base_frame_id': 'base_footprint',
                    'odom_frame_id': 'odom',
                    'init_pose_from_topic': '',
                    'freq': 10.0}],
            ),
        ])

    return LaunchDescription(
        get_lidar_launch_arguments() +
        get_motor_driver_launch_arguments() +
        get_servo_driver_launch_arguments() +
        [
            robot_nodes,
            slam_toolbox_launch,
            joy_launch
        ])
