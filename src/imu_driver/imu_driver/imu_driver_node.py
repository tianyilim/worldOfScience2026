import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
from geometry_msgs.msg import Vector3
import numpy as np
import adafruit_bno055
import board
import busio


class BNO055DriverNode(Node):
    """ROS2 node for BNO055 IMU sensor."""

    def __init__(self):
        super().__init__('imu_driver_node')

        # Declare parameters
        # yaw, pitch, roll in degrees
        self.declare_parameter('orientation_yaw_deg', 0.0)
        self.declare_parameter('orientation_pitch_deg', 0.0)
        self.declare_parameter('orientation_roll_deg', 0.0)
        self.declare_parameter('poll_rate_hz', 50.0)

        # Get parameter values
        yaw_deg = self.get_parameter(
            'orientation_yaw_deg').get_parameter_value().double_value
        pitch_deg = self.get_parameter(
            'orientation_pitch_deg').get_parameter_value().double_value
        roll_deg = self.get_parameter(
            'orientation_roll_deg').get_parameter_value().double_value
        self.poll_rate = self.get_parameter(
            'poll_rate_hz').get_parameter_value().double_value

        # Compute rotation matrix from sensor frame to robot frame
        self.rotation_matrix = self._euler_to_rotation_matrix(
            np.radians(yaw_deg),
            np.radians(pitch_deg),
            np.radians(roll_deg))

        # Initialize BNO055 sensor
        try:
            i2c = busio.I2C(board.SCL, board.SDA)
            self.sensor = adafruit_bno055.BNO055_I2C(i2c_bus=i2c)
            self.get_logger().info('BNO055 initialized successfully')
        except Exception as e:
            self.get_logger().error(f'Failed to initialize BNO055: {e}')
            raise

        # Create publisher for IMU messages
        self.imu_publisher = self.create_publisher(Imu, '/imu', 5)

        # Create timer for periodic reading
        period = 1.0 / self.poll_rate
        self.timer = self.create_timer(period, self.timer_callback)

        self.get_logger().info(
            f'IMU driver node started at {self.poll_rate} Hz')

    def _euler_to_rotation_matrix(self, roll: float, pitch: float, yaw: float):
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
        Rz = np.array([[np.cos(yaw), -np.sin(yaw), 0],
                       [np.sin(yaw), np.cos(yaw), 0],
                       [0, 0, 1]])

        Ry = np.array([[np.cos(pitch), 0, np.sin(pitch)],
                       [0, 1, 0],
                       [-np.sin(pitch), 0, np.cos(pitch)]])

        Rx = np.array([[1, 0, 0],
                       [0, np.cos(roll), -np.sin(roll)],
                       [0, np.sin(roll), np.cos(roll)]])

        # Combined rotation: R = Rz * Ry * Rx
        return Rz @ Ry @ Rx

    def _transform_vector(self, vector: np.ndarray) -> np.ndarray:
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
            # (x, y, z) in rad/s
            gyro = self.sensor.gyro
            # (x, y, z, w)
            quat = self.sensor.quaternion

            if euler is None or gravity is None or linear_accel is None or gyro is None or quat is None:
                self.get_logger().warn('Received None from sensor, skipping this reading')
                return

            # Transform acceleration and gyro to robot frame
            accel_robot = self._transform_vector(linear_accel)
            gyro_robot = self._transform_vector(gyro)

            self.get_logger().info(
                f"Accel: [{accel_robot[0]:.2f}, {accel_robot[1]:.2f}, {accel_robot[2]:.2f}] m/s^2")
            self.get_logger().info(
                f"Gyro: [{gyro_robot[0]:.2f}, {gyro_robot[1]:.2f}, {gyro_robot[2]:.2f}] rad/s")

            # For now let's try this
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
