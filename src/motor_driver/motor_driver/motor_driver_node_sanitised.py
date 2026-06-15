from rcl_interfaces.msg import ParameterDescriptor
import rclpy
from rclpy.node import Node
import time
from pprint import pformat
from geometry_msgs.msg import Twist, Vector3
from motor_driver.motor_driver_impl import THIS_BOARD_TYPE, DFRobot_DC_Motor_IIC as Board


def print_board_status(board: Board):
    '''Helper function to read Motor Driver board status.'''
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
    '''Helper function to read Motor Driver board status.'''
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

        # Declare parameters. This allows us to change values in our ROS Node
        # without needing to edit the code.
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
        self.declare_parameter("wheel_angvel_to_pwm", 20.0,
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
        """
        Translating Data from ROS Messages to Robot Wheel Velocities
        """

        # Access the useful attributes from the Twist msg.
        raw_linear = msg.linear.x
        raw_angular = msg.angular.z

        # TODO Step 1: Clamp Linear and Angular Velocities between limits
        # clamped_linear = 
        # clamped_angular =

        # TODO Step 2: Calculate the Differential Drive Kinematics
        ## Convert the Velocity command into the speed for each wheel

        # TODO Step 3: Ensure that Both Motors are spinning at the same speed
        ## If the Motors do not spin at the same speed, the Robot will not be able to
        ## drive in a straight line.

        # TODO Step 4: Convert from rad/s to pwm value
        pwm_left = 0.0 # should be something between 0.0 to 100.0
        pwm_right = 0.0 # should be something between 0.0 to 100.0

        # TODO Step 4.1 (Optional): Log the Mapping from rad/s to PWM Value for Debug Purposes
        self.get_logger().info(f"Hello, this a number with value {1.2}")

        # TODO Step 5: Sending the Motor PWM Values to the actual motors
        ## Specify:
        ##     - Which Motor to Control (M1 for Left, M2 for Right)
        ##     - Direction: Clockwise (CW) / Counter Clockwise (CCW)
        ##     - Speed: PWM Values that you have previously calculated above

        # Set motor directions and speeds. For instance:
        left_motor_direction = self.board.CW   # TODO: what should this be?
        right_motor_direction = self.board.CCW # TODO: what should this be?

        # Write to left motor
        self.board.motor_movement(
            [self.board.M1], left_motor_direction, pwm_left)
        # Write to right motor
        self.board.motor_movement(
            [self.board.M2], right_motor_direction, pwm_right)


def main(args=None):
    rclpy.init(args=args)
    motor_driver = MotorDriverNode()
    try:
        rclpy.spin(motor_driver)
    except KeyboardInterrupt:
        print("[motor driver]:", "-"*100)
        print("[motor driver]: STOPPING MOTOR DRIVER")
        motor_driver.board.motor_movement(
            [motor_driver.board.M1, motor_driver.board.M2],
            motor_driver.board.CW, 0)
        print("[motor driver]:", "-"*100)
    except Exception as e:
        print(f"[motor driver]: {e}")

    motor_driver.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()