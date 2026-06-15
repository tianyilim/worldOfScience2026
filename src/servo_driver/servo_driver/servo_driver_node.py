import time

import rclpy
from rclpy.node import Node
import RPi.GPIO as GPIO

from std_msgs.msg import Int8
from sensor_msgs.msg import Joy

PULSE_FREQ = 50
PARAM_NAME_OUT_PIN = 'out_pin'
PARAM_NAME_MAX_ANGLE = 'max_angle'
PARAM_NAME_MIN_ANGLE = 'min_angle'
PARAM_NAME_JOY_ANGLE_INCREMENT = 'joy_angle_increment'
PARAM_NAME_JOY_OPEN_BUTTON_INDEX = 'joy_open_button_index'
PARAM_NAME_JOY_CLOSE_BUTTON_INDEX = 'joy_close_button_index'


def angle_to_duty_cycle(angle: float) -> int:
    """
    Convert an angle in degrees to a PWM duty cycle percentage.

    Args:
        angle: Desired servo angle in degrees (0 to 180)
    Returns:
        Duty cycle percentage corresponding to the angle

    You should:
    1. Ensure that the Servo Angle is within the Servo's Bounds (X degrees to Y degrees)
    2. Map the Servo Angle to the PWM Cycle
    """

    # TODO: Remove this line after you have written your function
    raise NotImplementedError("Please implement this function.")


class ServoDriverNode(Node):
    """ROS2 node for generic servo over PWM."""

    def __init__(self):
        super().__init__('servo_driver_node')

        # Declare parameters. This allows us to change values in our ROS Node
        # without needing to edit the code.
        self.declare_parameter(PARAM_NAME_OUT_PIN, 11)
        self.declare_parameter(PARAM_NAME_MAX_ANGLE, 180)
        self.declare_parameter(PARAM_NAME_MIN_ANGLE, 0)
        self.declare_parameter(PARAM_NAME_JOY_ANGLE_INCREMENT, 5)
        self.declare_parameter(PARAM_NAME_JOY_OPEN_BUTTON_INDEX, 2)
        self.declare_parameter(PARAM_NAME_JOY_CLOSE_BUTTON_INDEX, 0)

        # Get parameter values from outside.
        out_pin = self.get_parameter(
            PARAM_NAME_OUT_PIN).get_parameter_value().integer_value
        self.max_angle = self.get_parameter(
            PARAM_NAME_MAX_ANGLE).get_parameter_value().integer_value
        self.min_angle = self.get_parameter(
            PARAM_NAME_MIN_ANGLE).get_parameter_value().integer_value
        self.joy_angle_increment = self.get_parameter(
            PARAM_NAME_JOY_ANGLE_INCREMENT).get_parameter_value().integer_value
        self.joy_open_button = self.get_parameter(
            PARAM_NAME_JOY_OPEN_BUTTON_INDEX).get_parameter_value().integer_value
        self.joy_close_button = self.get_parameter(
            PARAM_NAME_JOY_CLOSE_BUTTON_INDEX).get_parameter_value().integer_value

        # Initialize General Purpose Input and Output (GPIO) pin on the RPI board
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(out_pin, GPIO.OUT)
        self.pwm = GPIO.PWM(out_pin, PULSE_FREQ)
        self.pwm.start(0)

        # This is the current commanded angle of the servo.
        self.curr_angle = 0
        self.get_logger().info(
            f'Servo initialized on pin {out_pin} with frequency {PULSE_FREQ} Hz')

        # Initialise callbacks last, after all setup is done
        self.cmd_angle_subscription = self.create_subscription(
            Int8, 'cmd_angle',
            self.cmd_angle_callback,
            2)
        self.joy_subscription = self.create_subscription(
            Joy, 'joy',
            self.joy_callback,
            2)

    def cmd_angle_callback(self, msg: Int8):
        """Callback for receiving desired servo angle."""
        
        # Clamp the desired angle between safety bounds.
        desired_angle = min(self.max_angle, max(self.min_angle, msg.data))
        # Convert from an angle in degrees to a servo's duty cycle.
        duty_cycle = angle_to_duty_cycle(desired_angle)
        self.pwm.ChangeDutyCycle(duty_cycle)
        # Print out what we are doing
        self.get_logger().info(
            f'Angle command received: {desired_angle}deg -> duty cycle to {duty_cycle}%')

        self.curr_angle = desired_angle

    def joy_callback(self, msg: Joy):
        """
        Function that Translates Button Press Commands to Servo Angle Movements
        - Determine the Index of the Button you are using
        """
        
        # Ensure that the ROS Message contains valid content.
        if len(msg.axes) <= 0:
            # By returning early, invalid code will not be executed.
            return

        self.get_logger().info(f"Open  button index is set to: {self.joy_open_button}")
        self.get_logger().info(f"Close button index is set to: {self.joy_close_button}")
        msg.buttons[None]

        # TODO 1: Check if the Open / Closed Button has been pressed
        # The Open and Close buttons are defined as class attributes above. Use them!

        # TODO 2: Update the Angle of the Servo based on the Button Presses
        self.curr_angle = ...

        # TODO 3: Do you need to protect against commanding open/closed angle beyond the limits?

        # Call cmd_angle_callback() based on the new angle pressed.
        self.cmd_angle_callback(Int8(data=new_angle))


def main(args=None):
    rclpy.init(args=args)
    node = ServoDriverNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
