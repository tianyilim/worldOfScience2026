from rcl_interfaces.msg import ParameterDescriptor
import rclpy
from rclpy.node import Node
import time
from pprint import pformat
from geometry_msgs.msg import Twist
from motor_driver.motor_driver_impl import THIS_BOARD_TYPE, DFRobot_DC_Motor_IIC as Board


''' print last operate status, users can use this variable to determine the result of a function call. '''


def print_board_status(board: Board):
    if board.last_operate_status == board.STA_OK:
        print("board status: everything ok")
    elif board.last_operate_status == board.STA_ERR:
        print("board status: unexpected error")
    elif board.last_operate_status == board.STA_ERR_DEVICE_NOT_DETECTED:
        print("board status: device not detected")
    elif board.last_operate_status == board.STA_ERR_PARAMETER:
        print("board status: parameter error, last operate no effective")
    elif board.last_operate_status == board.STA_ERR_SOFT_VERSION:
        print("board status: unsupport board framware version")


def get_motor_driver_board(node: "MotorDriverNode") -> Board:
    if THIS_BOARD_TYPE:
        # RaspberryPi select bus 1, set address to 0x10
        board = Board(1, 0x10)
    else:
        # RockPi select bus 7, set address to 0x10
        board = Board(7, 0x10)

    # Do initial configuration and hardware sanity check
    l = board.detect()
    node.get_logger().info("Motor driver board list conform:")
    node.get_logger().info(f"{pformat(l)}")

    while board.begin() != board.STA_OK:    # Board begin and check board status
        print_board_status(board)
        node.get_logger().warning("Motor driver board init failed, retrying...")
        time.sleep(2)
    node.get_logger().info("Motor driver board init success")

    # Set initial parameters
    # board.set_encoder_enable(board.NONE)                 # Set selected DC motor encoder enable
    # Set selected DC motor encoder disable
    board.set_encoder_disable(board.ALL)
    # board.set_encoder_reduction_ratio(board.ALL, 43)    # Set selected DC motor encoder reduction ratio, test motor reduction ratio is 43.8
    # Set DC motor pwm frequency to 1000HZ; can experiment with other values.
    board.set_motor_pwm_frequency(1000)
    return board


class MotorDriverNode(Node):

    def __init__(self):
        super().__init__('motor_driver_node')

        self.declare_parameter("max_linear_vel", 1.0,
                               descriptor=ParameterDescriptor(description="Maximum linear velocity"))
        self.declare_parameter("max_angular_vel", 0.5,
                               descriptor=ParameterDescriptor(description="Maximum angular velocity"))
        self.declare_parameter("left_right_ratio", 1.0,
                               descriptor=ParameterDescriptor(description="Ratio of left to right motor speed"))
        self.declare_parameter("wheelbase", 0.12,
                               descriptor=ParameterDescriptor(description="Distance between the wheels"))
        self.declare_parameter("wheel_radius", 0.032,
                               descriptor=ParameterDescriptor(description="Radius of the wheels"))
        self.declare_parameter("wheel_angvel_to_pwm", 100.0,
                               descriptor=ParameterDescriptor(description="Conversion factor from wheel angular velocity to PWM value"))
        self.declare_parameter("invert_left_motor", False,
                               descriptor=ParameterDescriptor(description="Invert the direction of the left motor"))
        self.declare_parameter("invert_right_motor", False,
                               descriptor=ParameterDescriptor(description="Invert the direction of the right motor"))

        # Declare class parameters
        self.MAX_LINEAR_VEL = self.get_parameter(
            "max_linear_vel").get_parameter_value().double_value
        '''Maximum linear velocity. Input values outside the range will be clamped'''
        self.MAX_ANGULAR_VEL = self.get_parameter(
            "max_angular_vel").get_parameter_value().double_value
        '''Maximum angular velocity. Input values outside the range will be clamped'''
        self.LEFT_RIGHT_RATIO = self.get_parameter(
            "left_right_ratio").get_parameter_value().double_value
        '''Ratio of left to right motor speed, to account for hardware differences'''

        self.WHEELBASE = self.get_parameter(
            "wheelbase").get_parameter_value().double_value
        self.WHEEL_RADIUS = self.get_parameter(
            "wheel_radius").get_parameter_value().double_value
        # Conversion factor from wheel angular velocity (rad/s) to PWM value
        self.WHEEL_ANGVEL_TO_PWM = self.get_parameter(
            "wheel_angvel_to_pwm").get_parameter_value().double_value

        self.INVERT_LEFT_MOTOR = self.get_parameter(
            "invert_left_motor").get_parameter_value().bool_value
        self.INVERT_RIGHT_MOTOR = self.get_parameter(
            "invert_right_motor").get_parameter_value().bool_value

        # Initialize motor driver board
        self.board = get_motor_driver_board(self)

        # Ensure that motors are stopped at startup
        self.board.motor_stop(self.board.ALL)

        # Initialise callbacks last, after all setup is done
        self.twist_subscription = self.create_subscription(
            Twist,
            'cmd_vel',
            self.twist_callback,
            10)

    def twist_callback(self, msg: Twist):
        # This is of course quite basic, does not account for deadband etc.

        clamped_linear = max(
            min(msg.linear.x, self.MAX_LINEAR_VEL), -self.MAX_LINEAR_VEL)
        clamped_angular = max(
            min(msg.angular.z, self.MAX_ANGULAR_VEL), -self.MAX_ANGULAR_VEL)

        speed_left = (clamped_linear - clamped_angular *
                      self.WHEELBASE / 2) / self.WHEEL_RADIUS
        speed_right = (clamped_linear + clamped_angular *
                       self.WHEELBASE / 2) / self.WHEEL_RADIUS

        if self.LEFT_RIGHT_RATIO > 1.0:
            # Left motor is faster, scale down left motor
            speed_left = speed_left / self.LEFT_RIGHT_RATIO
        elif self.LEFT_RIGHT_RATIO < 1.0:
            # Right motor is faster, scale down right motor
            speed_right = speed_right * self.LEFT_RIGHT_RATIO

        # Convert from rad/s to pwm value
        pwm_left = min(abs(speed_left) * self.WHEEL_ANGVEL_TO_PWM, 100.0)
        pwm_right = min(abs(speed_right) * self.WHEEL_ANGVEL_TO_PWM, 100.0)
        self.get_logger().debug(
            f"cmd_vel received: linear {msg.linear.x:.2f} m/s, angular {msg.angular.z:.2f} rad/s")
        self.get_logger().debug(
            f"  -> wheel speeds: left {speed_left:.2f} rad/s, right {speed_right:.2f} rad/s")
        self.get_logger().debug(
            f"  -> pwm values: left {pwm_left:.2f} %, right {pwm_right:.2f} %")

        # Set motor directions and speeds.
        if speed_left >= 0:
            self.board.motor_movement(
                [self.board.M1],
                self.board.CCW if not self.INVERT_LEFT_MOTOR else self.board.CW,
                pwm_left)
        else:
            self.board.motor_movement(
                [self.board.M1],
                self.board.CW if not self.INVERT_LEFT_MOTOR else self.board.CCW,
                pwm_left)

        if speed_right >= 0:
            self.board.motor_movement(
                [self.board.M2],
                self.board.CW if not self.INVERT_RIGHT_MOTOR else self.board.CCW,
                pwm_right)
        else:
            self.board.motor_movement(
                [self.board.M2],
                self.board.CCW if not self.INVERT_RIGHT_MOTOR else self.board.CW,
                pwm_right)


def main(args=None):
    rclpy.init(args=args)
    motor_driver = MotorDriverNode()
    rclpy.spin(motor_driver)
    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically when the garbage collector destroys the node object)
    motor_driver.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
