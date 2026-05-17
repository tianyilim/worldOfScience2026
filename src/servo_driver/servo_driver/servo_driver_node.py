"""
Servo driver.

Logic taken from https://gist.github.com/MichaelCurrin/48c412b28cb0a44ae9f74bc5f260e1d3
"""

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


def angle_to_duty_cycle(angle: float) -> int:
    """
    Convert an angle in degrees to a PWM duty cycle percentage.

    Args:
        angle: Desired servo angle in degrees (0 to 180)
    Returns:
        Duty cycle percentage corresponding to the angle
    """

    # Ensure angle is within bounds
    angle = max(0, min(180, angle))
    # Map angle to duty cycle: 0 deg -> 2, 180 deg -> 12
    duty_cycle = (angle / 180) * 10 + 2.0
    return int(round(duty_cycle))


class ServoDriverNode(Node):
    """ROS2 node for generic servo over PWM."""

    def __init__(self):
        super().__init__('servo_driver_node')

        # Declare parameters
        # yaw, pitch, roll in degrees
        self.declare_parameter(PARAM_NAME_OUT_PIN, 11)
        self.declare_parameter(PARAM_NAME_MAX_ANGLE, 180)
        self.declare_parameter(PARAM_NAME_MIN_ANGLE, 0)
        self.declare_parameter(PARAM_NAME_JOY_ANGLE_INCREMENT, 5)

        # Get parameter values
        out_pin = self.get_parameter(
            PARAM_NAME_OUT_PIN).get_parameter_value().integer_value
        self.max_angle = self.get_parameter(
            PARAM_NAME_MAX_ANGLE).get_parameter_value().integer_value
        self.min_angle = self.get_parameter(
            PARAM_NAME_MIN_ANGLE).get_parameter_value().integer_value
        self.joy_angle_increment = self.get_parameter(
            PARAM_NAME_JOY_ANGLE_INCREMENT).get_parameter_value().integer_value

        # Initialize PWM
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(out_pin, GPIO.OUT)
        self.pwm = GPIO.PWM(out_pin, PULSE_FREQ)
        self.pwm.start(0)

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
        desired_angle = min(self.max_angle, max(self.min_angle, msg.data))
        duty_cycle = angle_to_duty_cycle(desired_angle)
        self.pwm.ChangeDutyCycle(duty_cycle)
        self.get_logger().info(
            f'Angle command received: {desired_angle} degrees, setting duty cycle to {duty_cycle}%')
        self.curr_angle = desired_angle

    def joy_callback(self, msg: Joy):
        """Callback for receiving joystick input."""

        # Assume LB and RB buttons are used to control the servo angle
        # LB: index 4, RB: index 5

        angle_incr = self.joy_angle_increment

        if len(msg.axes) > 0:
            LB_pressed = msg.buttons[4] == 1
            RB_pressed = msg.buttons[5] == 1

            if LB_pressed and not RB_pressed:
                # Decrease angle
                new_angle = max(self.min_angle, self.curr_angle - angle_incr)
                self.cmd_angle_callback(Int8(data=new_angle))
            elif RB_pressed and not LB_pressed:
                # Increase angle
                new_angle = min(self.max_angle, self.curr_angle + angle_incr)
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
