import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
from geometry_msgs.msg import Vector3
import numpy as np
from adafruit_bno055 import Adafruit_BNO055
import board
import busio


class BNO055DriverNode(Node):
    """ROS2 node for BNO055 IMU sensor."""

    def __init__(self):
        super().__init__('imu_driver_node')

        # Declare parameters
        # yaw, pitch, roll in degrees
        self.declare_parameter('orientation_ypr', [0.0, 0.0, 0.0])
        self.declare_parameter('poll_rate_hz', 50.0)

        # Get parameter values
        ypr = self.get_parameter('orientation_ypr').value
        self.poll_rate = self.get_parameter('poll_rate_hz').value

        # Store orientation as euler angles (in radians) for rotation matrix calculation
        self.yaw = np.radians(ypr[0])
        self.pitch = np.radians(ypr[1])
        self.roll = np.radians(ypr[2])

        # Compute rotation matrix from sensor frame to robot frame
        self.rotation_matrix = self._euler_to_rotation_matrix(
            self.roll, self.pitch, self.yaw)

        # Initialize BNO055 sensor
        try:
            i2c = busio.I2C(board.SCL, board.SDA)
            self.sensor = Adafruit_BNO055.Adafruit_BNO055(i2c_bus=i2c)
            self.get_logger().info('BNO055 initialized successfully')
        except Exception as e:
            self.get_logger().error(f'Failed to initialize BNO055: {e}')
            raise

        # Create publisher for IMU messages
        self.imu_publisher = self.create_publisher(Imu, '/imu', 10)

        # Create timer for periodic reading
        period = 1.0 / self.poll_rate
        self.timer = self.create_timer(period, self.timer_callback)

        self.get_logger().info(
            f'IMU driver node started at {self.poll_rate} Hz')

    def _euler_to_rotation_matrix(self, roll, pitch, yaw):
        """
        Convert Euler angles (roll, pitch, yaw) to rotation matrix.
        Uses ZYX convention (yaw-pitch-roll).

        Args:
            roll: rotation around x-axis (radians)
            pitch: rotation around y-axis (radians)
            yaw: rotation around z-axis (radians)

        Returns:
            3x3 rotation matrix (numpy array)
        """
        # Rotation matrices for each axis
        Rz = np.array([
            [np.cos(yaw), -np.sin(yaw), 0],
            [np.sin(yaw), np.cos(yaw), 0],
            [0, 0, 1]
        ])

        Ry = np.array([
            [np.cos(pitch), 0, np.sin(pitch)],
            [0, 1, 0],
            [-np.sin(pitch), 0, np.cos(pitch)]
        ])

        Rx = np.array([
            [1, 0, 0],
            [0, np.cos(roll), -np.sin(roll)],
            [0, np.sin(roll), np.cos(roll)]
        ])

        # Combined rotation: R = Rz * Ry * Rx
        return Rz @ Ry @ Rx

    def _transform_vector(self, vector):
        """
        Transform a 3D vector from sensor frame to robot frame.

        Args:
            vector: 3-element array (x, y, z)

        Returns:
            Transformed 3-element array
        """
        vec = np.array(vector)
        return self.rotation_matrix @ vec

    def timer_callback(self):
        """Periodic callback to read sensor and publish IMU message."""
        try:
            # Read sensor data
            euler = self.sensor.euler  # (heading, roll, pitch) in degrees
            gravity = self.sensor.gravity  # (x, y, z) in m/s^2
            # (x, y, z) in m/s^2
            linear_accel = self.sensor.linear_acceleration
            gyro = self.sensor.gyro  # (x, y, z) in rad/s

            if euler is None or gravity is None or linear_accel is None or gyro is None:
                self.get_logger().warn('Received None from sensor, skipping this reading')
                return

            # Transform acceleration and gyro to robot frame
            accel_robot = self._transform_vector(linear_accel)
            gyro_robot = self._transform_vector(gyro)

            # Get quaternion for IMU message (BNO055 provides this)
            quat = self.sensor.quaternion  # Returns (x, y, z, w)

            if quat is None:
                self.get_logger().warn('Received None quaternion from sensor')
                return

            # Create and populate IMU message
            imu_msg = Imu()
            imu_msg.header.stamp = self.get_clock().now().to_msg()
            imu_msg.header.frame_id = 'imu_link'

            # Set orientation (quaternion)
            imu_msg.orientation.x = float(quat[0])
            imu_msg.orientation.y = float(quat[1])
            imu_msg.orientation.z = float(quat[2])
            imu_msg.orientation.w = float(quat[3])

            # Set angular velocity
            imu_msg.angular_velocity.x = float(gyro_robot[0])
            imu_msg.angular_velocity.y = float(gyro_robot[1])
            imu_msg.angular_velocity.z = float(gyro_robot[2])

            # Set linear acceleration
            imu_msg.linear_acceleration.x = float(accel_robot[0])
            imu_msg.linear_acceleration.y = float(accel_robot[1])
            imu_msg.linear_acceleration.z = float(accel_robot[2])

            # Set covariance (diagonal uncertainty values)
            # These can be tuned based on sensor specifications
            imu_msg.orientation_covariance = [
                0.0015] * 9  # ~0.9 degree std dev
            imu_msg.angular_velocity_covariance = [
                0.001] * 9  # rad/s covariance
            imu_msg.linear_acceleration_covariance = [
                0.01] * 9  # m/s^2 covariance

            # Publish message
            self.imu_publisher.publish(imu_msg)

        except Exception as e:
            self.get_logger().error(f'Error reading IMU sensor: {e}')


def main(args=None):
    rclpy.init(args=args)
    node = BNO055DriverNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
