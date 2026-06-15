from rcl_interfaces.msg import ParameterDescriptor
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

import RPi.GPIO as GPIO

# Set up. You can consult the pinout.xyz website to change the pins if needed,
# but make sure to update the wiring accordingly.

MOTOR_1_OUT_PIN_A = 32
MOTOR_1_OUT_PIN_B = 36
MOTOR_2_OUT_PIN_A = 38
MOTOR_2_OUT_PIN_B = 40

# Physical pulse frequency for the motors.
PULSE_FREQ = 50

# Initialise GPIO pins
GPIO.setmode(GPIO.BOARD)
GPIO.setup(MOTOR_1_OUT_PIN_A, GPIO.OUT)
GPIO.setup(MOTOR_1_OUT_PIN_B, GPIO.OUT)
GPIO.setup(MOTOR_2_OUT_PIN_A, GPIO.OUT)
GPIO.setup(MOTOR_2_OUT_PIN_B, GPIO.OUT)


def _move_motor(pin_a, pin_b,
                is_forward: bool = True,
                speed: float = 0):

    speed = min(100, max(0, speed))

    # TODO: With knowledge of how a dual H-bridge motor driver works, implement the logic to control
    #      forward and reverse motion of motors using the two pins.
    # Change the assignment of these values below.
    pin_a_speed = None
    pin_b_speed = None

    if is_forward:
        raise NotImplementedError(
            "This function is not implemented yet. Please implement the motor control logic here.")
        pin_a.ChangeDutyCycle(pin_a_speed)
        pin_b.ChangeDutyCycle(pin_b_speed)
    else:
        raise NotImplementedError(
            "This function is not implemented yet. Please implement the motor control logic here.")
        pin_a.ChangeDutyCycle(pin_a_speed)
        pin_b.ChangeDutyCycle(pin_b_speed)


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

        # Define motor control pins as class attributes, and set up PWM control on those pins.
        self.motor_1_a = GPIO.PWM(MOTOR_1_OUT_PIN_A, PULSE_FREQ)
        self.motor_1_b = GPIO.PWM(MOTOR_1_OUT_PIN_B, PULSE_FREQ)
        self.motor_2_a = GPIO.PWM(MOTOR_2_OUT_PIN_A, PULSE_FREQ)
        self.motor_2_b = GPIO.PWM(MOTOR_2_OUT_PIN_B, PULSE_FREQ)
        self.motor_1_a.start(0)
        self.motor_1_b.start(0)
        self.motor_2_a.start(0)
        self.motor_2_b.start(0)

        # Stop Motor
        self.stop_motors()

        # Initialise callbacks last, after all setup is done
        self.twist_subscription = self.create_subscription(
            Twist,
            'cmd_vel',
            self.twist_callback,
            10)

    def stop_motors(self):
        '''Convenience function for you to stop the motors by setting the speed to 0.'''
        _move_motor(self.motor_1_a, self.motor_1_b, speed=0.0)
        _move_motor(self.motor_2_a, self.motor_2_b, speed=0.0)

    def _unbind_gpio(self):
        '''This function is required to clean up the GPIO pins when the node is stopped,
        otherwise the pins will remain in their last state and may cause issues when you try to run the node again.'''
        self.motor_1_a.stop()
        self.motor_1_b.stop()
        self.motor_2_a.stop()
        self.motor_2_b.stop()
        GPIO.cleanup([MOTOR_1_OUT_PIN_A, MOTOR_1_OUT_PIN_B,
                      MOTOR_2_OUT_PIN_A, MOTOR_2_OUT_PIN_B])

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
        # Convert the Velocity command into the speed for each wheel

        # TODO Step 3: Ensure that Both Motors are spinning at the same speed
        # If the Motors do not spin at the same speed, the Robot will not be able to
        # drive in a straight line.

        # TODO Step 4: Convert from rad/s to pwm value
        pwm_left = 0.0  # should be something between 0.0 to 100.0
        pwm_right = 0.0  # should be something between 0.0 to 100.0

        # TODO Step 4.1 (Optional): Log the Mapping from rad/s to PWM Value for Debug Purposes
        self.get_logger().info(
            f"Hello, this a number with an example value {1.2}")

        # TODO Step 5: Sending the Motor PWM Values to the actual motors
        # Specify:
        # - Which Motor to Control (M1 for Left, M2 for Right)
        # - Direction: Clockwise (CW) / Counter Clockwise (CCW)
        # - Speed: PWM Values that you have previously calculated above

        # Set motor directions and speeds. For instance:
        left_motor_is_forward = True  # or False, depending on the sign of the speed
        right_motor_is_forward = True  # or False, depending on the sign of the speed

        # Call motor control function with the appropriate parameters. For instance:
        _move_motor(self.motor_1_a, self.motor_1_b,
                    is_forward=left_motor_is_forward, speed=pwm_left)
        _move_motor(self.motor_2_a, self.motor_2_b,
                    is_forward=right_motor_is_forward, speed=pwm_right)


def main(args=None):
    rclpy.init(args=args)
    motor_driver = MotorDriverNode()
    try:
        rclpy.spin(motor_driver)
    except KeyboardInterrupt:
        print("[motor driver]:", "-"*100)
        print("[motor driver]: STOPPING MOTOR DRIVER")
        motor_driver.stop_motors()
        motor_driver._unbind_gpio()
        print("[motor driver]:", "-"*100)
    except Exception as e:
        print(f"[motor driver]: {e}")

    motor_driver.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
